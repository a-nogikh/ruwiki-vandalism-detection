from .revision import Revision


class RevisionList:
    def __init__(revs: List[Revision]):
        self.revs = revs
