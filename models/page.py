from .revision_list import RevisionList


class Page:
    def __init__(self, page_id: int, title: str, ns: int):
        self.page_id = page_id
        self.title = title
        self.ns = ns

    def __eq__(self, other):
        return self.page_id == other.page_id \
            and self.title == other.title \
            and self.ns == other.ns
