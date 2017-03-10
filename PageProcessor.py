from FlaggedRevs import FlaggedRevs
from UserFlags import UserFlags
from mw.xml_dump.iteration.page import Page
from mw.xml_dump.iteration.revision import Revision
from mw.xml_dump.iteration.contributor import Contributor
from RevisionTools import RevisionTools
from pymongo import database
import VandalStatsProcessor

# not all but just enough
TRUSTED_GROUPS = ['editor', 'autoeditor', 'rollbacker', 'reviewer', 'sysop', 'bureaucrat']
TAKE_REVISIONS = 20

class PageProcessor:
    def __init__(self,
                 flagged_pages: FlaggedRevs,
                 user_flags: UserFlags,
                 db: database,
                 geoip):
        self.flagged_revs = flagged_pages
        self.user_flags = user_flags
        self.db = db.items
        self.tosave = []
        self.vandal = VandalStatsProcessor.VandalStatsProcessor(db, geoip)

    def process(self, page: Page):
        revs = list(page)  # type: list[Revision]
        self.set_reverted_and_cancelled(revs)

        for index, rev in enumerate(revs):
            flags = self.user_flags.get_flags(rev.contributor.id) or []
            if 'bot' in flags:
                continue  # ignore bots

            if self.is_trusted(flags) or \
                    (rev.cancelled_by is None and rev.reverted_by is None):
                self.record_normal_statistics(rev)
                continue # TODO: capture normal revisions as well
            else:
                self.record_vandal_statistics(rev)

            if rev.reverted_by is None:
                continue  # interested in reverts only

            #if rev.timestamp.year != 2016:
            #    continue  # not interested in other years
            obj = self.make_db_object(revs[max(0,index-TAKE_REVISIONS):(1+index)])
            print(obj)

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
                "comment" : x.comment
            }
            for x in revisions
        ]

    def set_reverted_and_cancelled(self, revs):
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
            if reverting and revision.contributor.id is not None:
                reverted = None
                for x in range(index - 1, 0, -1):
                    if reverted is None:
                        reverted = revs[x]

                    if revs[x].contributor.user_text != reverted.contributor.user_text:
                        revision.reverts_till = revs[x].id
                        break

                    revs[x].reverted_by = revision.id
                break

    def record_normal_statistics(self, rev: Revision):
        if rev.contributor.id is None:
            self.vandal.add_ip(rev.contributor.user_text, rev.timestamp, False)

    def record_vandal_statistics(self, rev: Revision):
        if rev.contributor.id is not None:
            return

        self.vandal.add_ip(rev.contributor.user_text, rev.timestamp, True)
        return

    @staticmethod
    def is_trusted(flags: list):
        return not set(flags).isdisjoint(TRUSTED_GROUPS)


    def save(self):
        self.vandal.save()