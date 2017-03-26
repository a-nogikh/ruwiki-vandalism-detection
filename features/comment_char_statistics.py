from .feature import Feature
from common.utils import strip_comment
from text.char_statistics import CharStatistics


class CommentCharStatistics(Feature):

    def extract(self, raw):
        last_rev = self.last_rev(raw)
        comment = strip_comment(last_rev["comment"])

        sum = CharStatistics.stats(comment)
        return {
            'c_len': len(comment),
            'c_cap': sum['capitalized'] / (1 + sum['alpha']),
            'c_lgt_w': max(len(x) for x in comment.split(' ')),
            'c_numalpha': sum['num'] / (1 + sum['alpha'] + sum['num']),
            'c_lgt_cs': CharStatistics.longest_conseq(comment)
        }