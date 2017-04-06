from .feature import Feature
from common.utils import strip_comment
from text.char_statistics import CharStatistics


class CommentCharStatistics(Feature):
    default_words = {"викификация", "оформление", "стилевые правки", "орфография", "пунктуация", "ответ",
                     "комментарий", "категоризация", "шаблон", "к удалению", "иллюстрация", "источники",
                     "запрос источника", "дополнение", "уточнение", "обновление", "закрыто", "итог"}

    def extract(self, raw):
        last_rev = self.last_rev(raw)
        comment = strip_comment(last_rev["comment"])
        comment_words = comment.replace(',','').split(' ')

        sum = CharStatistics.stats(comment)
        return {
            'c_len': len(comment),
            'c_cap': sum['capitalized'] / (1 + sum['alpha']),
            'c_lgt_w': max(len(x) for x in comment_words),
            'c_wrd_c': len(comment_words),
            'c_wrd_avg': len(comment) / (len(comment_words) + 1),
            'c_numalpha': sum['num'] / (1 + sum['alpha'] + sum['num']),
            'c_def_wrds': 1 if any(x in self.default_words for x in comment_words) else 0,
            'c_lgt_cs': CharStatistics.longest_conseq(comment)
        }