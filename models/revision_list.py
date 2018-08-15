from typing import List
from operator import attrgetter
from .revision import Revision


class RevisionList:
    def __init__(self, revs: List[Revision] = []):
        self.replace(revs)

    def replace(self, revs: List[Revision]):
        self.revs = revs.copy()
        self.revs.sort(key=attrgetter("timestamp"), reverse=True)

    def get_last_revision(self) -> Revision:
        if len(self.revs) > 0:
            return self.revs[0]
        else:
            return None
        
    def __len__(self):
        return len(self.revs)

    def __getitem__(self, key):
        return self.revs[key]
        
    def __iter__(self):
        return iter(self.revs)

    def __repr__(self):
        return "RevisionList({!r})".format(self.revs)
