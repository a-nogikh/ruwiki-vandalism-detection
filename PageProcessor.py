from FlaggedRevs import FlaggedRevs
from UserFlags import UserFlags
from mw.xml_dump.iteration.page import Page
from mw.xml_dump.iteration.revision import Revision
from mw.xml_dump.iteration.contributor import Contributor
from RevisionTools import RevisionTools
from pymongo import database, collection
import VandalStatsProcessor

# not all but just enough
TRUSTED_GROUPS = ['editor', 'autoeditor', 'rollbacker', 'reviewer', 'sysop', 'bureaucrat']
TAKE_REVISIONS = 50


class PageProcessor:
    def __init__(self,
                 flagged_pages: FlaggedRevs,
                 user_flags: UserFlags,
                 db: database,
                 geoip):
        self.flagged_revs = flagged_pages
        self.user_flags = user_flags
        self.db = db.items # type: collection.Collection
        self.to_save = []
        self.vandal = VandalStatsProcessor.VandalStatsProcessor(db, geoip)

    def process(self, page: Page):
        revs = list(page)  # type: list[Revision]
        self.set_reverted_and_cancelled(revs)

        last_trusted = None
        last_flagged = None

        for index, rev in enumerate(revs):
            flags = self.user_flags.get_flags(rev.contributor.id) or []

            is_trusted_user = self.is_trusted(flags)
            is_flagged_rev = self.flagged_revs.exists(rev.id)
            if is_flagged_rev:
                last_flagged = rev

            is_trusted_rev = is_flagged_rev or is_trusted_user
            if is_trusted_rev:
                last_trusted = rev

            if 'bot' in flags:
                continue  # ignore bots

            if is_trusted_rev or \
                    (rev.cancelled_by is None and rev.reverted_by is None):
                self.record_normal_statistics(rev)
                continue  # TODO: capture normal revisions as well
            else:
                self.record_vandal_statistics(rev)

            if rev.reverted_by is None or rev.reverts_till is not None or rev.cancels is not None:
                continue  # interested in reverts only

            if rev.timestamp.year != 2016:
                continue  # not interested in other years

            revs_list = revs[max(0, index - TAKE_REVISIONS):(1 + index)]
            obj = {
                "page": {
                    "id": page.id,
                    "title": page.title,
                    "ns": page.namespace
                },
                "revs": self.make_db_object(revs_list),
                "last_flagged": self.make_db_object([last_flagged])[0] if last_flagged is not None else None,
                "vandal": 1
            }
            if last_trusted is not None and \
                    last_trusted.id in {x.id for x in revs_list}:
                obj["last_trusted"] = last_trusted.id

            self.to_save.append(obj)
            if len(self.to_save) >= 100:
                self.db.insert_many(self.to_save)
                self.to_save = []

        # memory cleanup
        for rev in revs:
            rev.reverted_by = None

        # del revs
        return len(revs)

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
                        revs[x].cancelled_by = revision.id
                        break

            reverting = RevisionTools.is_reverting(revision.comment)
            if reverting and revision.contributor.id is not None:
                reverted = None
                for x in range(index - 1, 0, -1):
                    if reverted is None:
                        reverted = revs[x]

                    curr_contributor = revs[x].contributor.user_text
                    if curr_contributor == current_user_text:
                        break # reverting oneself

                    if curr_contributor != reverted.contributor.user_text:
                        revision.reverts_till = revs[x].id
                        break

                    revs[x].reverted_by = revision.id

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

    @staticmethod
    def is_trusted(flags: list):
        return not set(flags).isdisjoint(TRUSTED_GROUPS)

    def save(self):
        self.vandal.save()
        self.db.insert_many(self.to_save)
        self.to_save = []

    def clear(self):
        self.db.delete_many({})
