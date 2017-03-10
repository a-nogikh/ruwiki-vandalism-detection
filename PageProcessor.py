from FlaggedRevs import FlaggedRevs
from FlaggedUsers import FlaggedUsers
from mw.xml_dump.iteration.page import Page
from mw.xml_dump.iteration.revision import Revision
from mw.xml_dump.iteration.contributor import Contributor
from RevisionTools import RevisionTools
from pymongo import database
import VandalStatsProcessor


class PageProcessor:
    def __init__(self,
                 flagged_pages: FlaggedRevs,
                 flagged_users: FlaggedUsers,
                 db: database,
                 geoip):
        self.flagged_revs = flagged_pages
        self.flagged_users = flagged_users
        self.db = db
        self.vandal = VandalStatsProcessor.VandalStatsProcessor(db, geoip)

    def process(self, page: Page):
        revs = list(page)  # type: list[Revision]

        # TODO: prevent edit wars

        # prev = None
        for index, revision in enumerate(revs):
            #   revision.prev = prev
            #   if prev is not None:
            #       prev.next = revision

            #   prev = revision
            cancels = RevisionTools.cancels_id(revision.comment)
            if cancels is not None:
                for x in range(index - 1, max(index - 20, 0), -1):
                    if revs[x].id == cancels:
                        revision.cancels = revs[x]
                        revs[x].cancelled_by = revision.id

                        break
                break

            reverting = RevisionTools.is_reverting(revision.comment)
            if reverting:
                reverted = None
                for x in range(index - 1, 0, -1):
                    if reverted is None:
                        reverted = revs[x]

                    if revs[x].contributor.user_text != reverted.contributor.user_text:
                        revision.reverts_till = revs[x].id
                        break

                    revs[x].reverted_by = revision.id
                break

        for rev in revs:  # type: Revision
            flags = []  # get sw
            if 'bot' in flags:
                continue

            if not self.is_trusted(rev) and \
                    (rev.cancelled_by is not None or rev.reverted_by is not None):
                self.record_vandal_statistics(rev)
            else:
                self.record_normal_statistics(rev)
                continue

            if rev.reverted_by is None or rev.timestamp:
                continue  # interested in reverts only

            if rev.timestamp.year != 2016:
                continue # not interested in other years





        # memory cleanup
        for rev in revs:
            rev.reverted_by = None


        # del revs
        return len(revs)

    def record_normal_statistics(self, rev: Revision):
        if rev.contributor.id is None:
            self.vandal.add_ip(rev.contributor.user_text, rev.timestamp, False)

    def record_vandal_statistics(self, rev: Revision):
        if rev.contributor.id is not None:
            return

        self.vandal.add_ip(rev.contributor.user_text, rev.timestamp, True)
        return

    def is_trusted(self, rev: Revision):
        if self.flagged_revs.exists(rev.id):
            return True
        user = rev.contributor  # type: Contributor
        if user.id is None:
            return False
        return self.flagged_users.is_flagged(user.id)

    def save(self):
        self.vandal.save()