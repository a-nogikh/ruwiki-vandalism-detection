from .feature import Feature
from text.char_statistics import CharStatistics


class TextCharStatistics(Feature):

    def extract(self, raw):
        sum = CharStatistics.stats('')

        longest_word = 0
        longest_conseq = 0
        for word, diff in raw["rwords"]:
            if diff < 0:
                continue

            longest_word = max(longest_word, len(word))
            longest_conseq = max(longest_conseq, CharStatistics.longest_conseq(word))

            stats = CharStatistics.stats(word)
            for k, v in stats.items():
                sum[k] += v

        return {
            't_cap': sum['capitalized'] / (1 + sum['alpha']),
            't_lgt_w': longest_word,
            't_numalpha': sum['num'] / (1 + sum['alpha'] + sum['num']),
            't_lgt_cs': longest_conseq
        }