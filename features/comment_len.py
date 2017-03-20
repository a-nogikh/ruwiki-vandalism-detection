from .feature import Feature
from common.utils import strip_comment


class CommentLen(Feature):
    def extract(self, raw):
        last_rev = self.last_rev(raw)
        comment = strip_comment(last_rev["comment"])

        return len(comment)
