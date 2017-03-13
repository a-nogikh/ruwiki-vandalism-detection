from flagged_revs import FlaggedRevs
from user_flags import UserFlags
from mw.xml_dump.iteration.page import Page
from mw.xml_dump.iteration.revision import Revision
from mw.xml_dump.iteration.contributor import Contributor
from revision_tools import RevisionTools
from pymongo import database, collection
from datetime import datetime, timedelta
import random
import vandal_stats_processor

# not all but just enough
TRUSTED_GROUPS = ['editor', 'autoeditor', 'rollbacker', 'reviewer', 'sysop', 'bureaucrat']
# number of revisions to save in a database
TAKE_REVISIONS = 50
# to keep the size of the data set reasonably small
TAKE_ONE_GOOD_IN = 6


class PageProcessor:
    def __init__(self,
                 flagged_pages: FlaggedRevs,
                 user_flags: UserFlags,
                 db: database,
                 geoip):
        self.flagged_revs = flagged_pages
        self.user_flags = user_flags
        self.db = db.items  # type: collection.Collection
        self.to_save = []
        self.ok_cnt = [0, 0]
        self.vandal = vandal_stats_processor.VandalStatsProcessor(db, geoip)

    def process(self, page: Page, excl):
        revs = list(page)  # type: list[Revision]
        revs_len = len(revs)
        if excl:
            del revs
            return revs_len

        self.set_reverted_and_cancelled(revs)

        last_trusted = None
        last_flagged = None
        prev_last_flagged = None
        prev_last_trusted = None

        session_start = None  # type: Revision
        allowed_delta = timedelta(hours=3)

        for index, rev in enumerate(revs):
            flags = self.user_flags.get_flags(rev.contributor.id) or []

            is_trusted_user = self.is_trusted(flags)
            is_flagged_rev = self.flagged_revs.exists(rev.id)
            prev_last_flagged = last_flagged

            if is_flagged_rev:
                last_flagged = rev

            is_trusted_rev = is_flagged_rev or is_trusted_user
            prev_last_trusted = last_trusted
            if is_trusted_rev:
                last_trusted = rev

            if session_start is None or \
                    session_start.contributor.user_text != rev.contributor.user_text or \
                    (rev.timestamp - session_start.timestamp) >= allowed_delta:
                session_start = rev

            if 'bot' in flags:
                continue  # ignore bots

            rev_vandal = False
            if is_trusted_rev or \
                    (rev.cancelled_by is None and rev.reverted_by is None):
                self.record_normal_statistics(rev)

                if not is_trusted_rev:
                    continue
            else:
                self.record_vandal_statistics(rev)
                rev_vandal = True

                reverter = rev.reverted_by
                if reverter is None:
                    continue  # reverted

                if reverter.reverted_by is not None or reverter.cancelled_by is not None:
                    continue # not interested in cancelled/reverted reverts

            if rev.reverts_till is not None or rev.cancels is not None:
                continue  # not interested in reverts and cancels

            if rev.timestamp.year != 2016:
                continue  # not interested in other years

            if not rev_vandal:
                if random.randrange(TAKE_ONE_GOOD_IN) != 0:
                    continue  # to keep list of good revs reasonably small

            revs_list = revs[max(0, index - TAKE_REVISIONS):(1 + index)]
            self.ok_cnt[0 if rev_vandal else 1] += 1
            obj = {
                "page": {
                    "id": page.id,
                    "title": page.title,
                    "ns": page.namespace
                },
                "revs": self.make_db_object(revs_list),
                "last_flagged": self.make_db_object([prev_last_flagged])[0] if prev_last_flagged is not None else None,
                "last_trusted": None,
                "session_start": session_start.id,
                "vandal": rev_vandal
            }

            if prev_last_trusted is not None:
                if prev_last_trusted.id in {x.id for x in revs_list}:
                    obj["last_trusted"] = prev_last_trusted.id

            self.to_save.append(obj)
            if len(self.to_save) >= 100:
                self.db.insert_many(self.to_save)
                self.to_save.clear()

        # memory cleanup
        for rev in revs:
            rev.reverted_by = None
            rev.cancelled_by = None
            rev.reverts_till = None
            rev.cancels = None

        del revs
        return revs_len

    def make_db_object(self, revisions: [Revision]):
        return [
            {
                "id": x.id,
                "timestamp": x.timestamp,
                "comment": x.comment,
                "flagged": self.flagged_revs.exists(x.id),
                "minor": x.minor,
                "user": {
                    "id": x.contributor.id,
                    "name": x.contributor.user_text
                },
                "text": ""
            }
            for x in revisions
            ]

    def set_reverted_and_cancelled(self, revs):
        # TODO: consider edit wars
        for index, revision in enumerate(revs):
            current_user_text = revision.contributor.user_text
            cancels = RevisionTools.cancels_id(revision.comment)
            if cancels is not None:
                for x in range(index - 1, max(index - 20, 0), -1):
                    if revs[x].id == cancels:

                        # in case of cancelling one's own revs
                        if revs[x].contributor.user_text == current_user_text:
                            break

                        revision.cancels = revs[x]
                        revs[x].cancelled_by = revision
                        break

            reverting = RevisionTools.is_reverting(revision.comment)
            if reverting and revision.contributor.id is not None:
                reverted = None
                for x in range(index - 1, 0, -1):
                    if reverted is None:
                        reverted = revs[x]

                    curr_contributor = revs[x].contributor.user_text
                    if curr_contributor == current_user_text:
                        break  # reverting oneself

                    if curr_contributor != reverted.contributor.user_text:
                        revision.reverts_till = revs[x].id
                        break

                    revs[x].reverted_by = revision
                    revision.reverts_last = revs[x]

    def record_normal_statistics(self, rev: Revision):
        if rev.contributor.id is None:
            self.vandal.add_ip(rev.contributor.user_text, rev.timestamp, False)
        else:
            self.vandal.add_user(rev.timestamp, False)

    def record_vandal_statistics(self, rev: Revision):
        if rev.contributor.id is None:
            self.vandal.add_ip(rev.contributor.user_text, rev.timestamp, True)
        else:
            self.vandal.add_user(rev.timestamp, True)

        if rev.reverted_by is not None:
            reverter = rev.reverted_by  # type: Revision
            if reverter.reverts_last.id == rev.id:
                self.vandal.add_time_diff(False, rev.timestamp, reverter.timestamp)

        if rev.cancelled_by is not None:
            canceller = rev.cancelled_by  # type: Revision
            self.vandal.add_time_diff(True, rev.timestamp, canceller.timestamp)

    @staticmethod
    def is_trusted(flags: list):
        return not set(flags).isdisjoint(TRUSTED_GROUPS)

    def save(self):
        self.vandal.save()
        self.db.insert_many(self.to_save)
        self.to_save.clear()

    def clear(self):
        self.db.delete_many({})
