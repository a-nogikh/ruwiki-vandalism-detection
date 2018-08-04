from .revision import Revision
from typing import List


class RevisionList:
    def __init__(self, revs: List[Revision] = []):
        self.replace(revs)

    def replace(self, revs: List[Revision]):
        self.revs = revs

    def __len__(self):
        return len(self.revs)

    def __getitem__(self, key):
        return self.revs[key]
        
    def __iter__(self):
        return iter(self.revs)
