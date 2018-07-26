from .page import Page
from .revision_list import RevisionList

class Instance:
    def __init__(self, page: Page, latest_revs: RevisionList):
        self.page = page
        self.latest_revs = latest_revs
        self.features_cache = {}
