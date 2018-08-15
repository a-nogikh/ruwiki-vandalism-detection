from datetime import datetime


class LabelingTask:
    def __init__(self,
                 rev_from: int,
                 rev_to: int,
                 tags: list,
                 labeled_at: datetime,
                 cached_diff: str = None,
                 cached_title: str = None,
                 cached_username: str = None):
        self.rev_from = rev_from
        self.rev_to = rev_to
        self.tags = tags
        self.labeled_at = labeled_at
        self.cached_title = cached_title
        self.cached_diff = cached_diff
        self.cached_username = cached_username
