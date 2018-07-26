from .page import Page
from .revision_list import RevisionList

class Instance:
    def __init__(self,
                 page: Page,
                 revision_id: int):
        self.page = page
        self.revision_id = revision_id
        self.revisions = RevisionList()
        self.feature_cache = {}


