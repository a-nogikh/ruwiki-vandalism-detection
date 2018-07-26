from .revision_list import RevisionList


class Page:
    def __init__(page_id: int, title: str, ns: int):
        self.page_id = page_id
        self.title = title
        self.ns = ns
