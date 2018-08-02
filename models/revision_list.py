from .revision import Revision


class RevisionList:
    def __init__(revs: List[Revision]):
        self.replace(revs)

    def replace(self, revs: List[Revision]):
        self.revs = revs
        
    def __iter__(self):
        return iter(self.revs)
