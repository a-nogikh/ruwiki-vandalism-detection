from datetime import timedelta
from models import Revision, RevisionList

# Edit session is a sequence of modifications where:
# 1. Distance between two consequtive edits is <= 10 minutes
# 2. All edits are made by the same person
# 3. The whole session is within 1 hour

class EditSessionSelector:
    MAX_CONSEQ_REVISIONS_TIMEDELTA=timedelta(minutes=10)
    MAX_SESSION_LENGTH_TIMEDELTA=timedelta(minutes=60)
    
    @staticmethod
    def find_session_start(revs: RevisionList) -> Revision:
        end_revision = revs[0]
        candidate = end_revision
        
        for revision in revs:
            delta = candidate.timedelta_with(revision)
            if delta > EditSessionSelector.MAX_CONSEQ_REVISIONS_TIMEDELTA:
                break
            
            if revision.user != candidate.user:
                break

            delta_start = end_revision.timedelta_with(revision)
            if delta_start > EditSessionSelector.MAX_SESSION_LENGTH_TIMEDELTA:
                break

            candidate = revision
            
        return candidate

    @staticmethod
    def find_revision_before_session(revs: RevisionList) -> Revision:
        """ Queries the last revision before edit session begins
        
        Parameters
        -----------
        revs : RevisionList

        Returns
        -----------
        If the revision list contains only 1 revision, returns None
        Otherwise, returns a Revision object
        """

        if len(revs) <= 1:
            return None
        
        rev_start = EditSessionSelector.find_session_start(revs)
        candidate = revs[-1]

        for revision in reversed(revs):
            if revision is not rev_start:
                candidate = revision
            else:
                break

        return candidate
