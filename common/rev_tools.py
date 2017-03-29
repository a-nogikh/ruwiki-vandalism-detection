from models.revision import Revision
from datetime import datetime, timedelta

MAX_DELTA = timedelta(hours=3)


class RevTools:
    @staticmethod
    def session_start(revs: [Revision]) -> Revision:
        end_revision = None
        next_revision = None

        for rev in sorted(revs, key = lambda x: x.timestamp, reverse=True): # type: Revision
            if end_revision is None:
                end_revision = rev
                next_revision = rev
                continue

            if rev.user != end_revision.user:
                return next_revision

            if (next_revision.timestamp - rev.timestamp) > MAX_DELTA:
                return next_revision

            next_revision = rev

        return next_revision
