from .feature import Feature
from text.char_statistics import CharStatistics
from collections import defaultdict
from lzma import LZMACompressor, FORMAT_ALONE

class TextCharStatistics(Feature):
    def extract(self, raw):
        sum = CharStatistics.stats('')
        compressor = LZMACompressor(format=FORMAT_ALONE)

        longest_word = 0
        longest_conseq = 0
        collection = raw["rwords"] if "rwords" in raw else {}
        word_total = 0
        chrs = defaultdict(int)
        added_words = ""

        for word, diff in collection.items():
            if diff < 0:
                continue

            word_total += diff
            added_words += word
            longest_word = max(longest_word, len(word))
            longest_conseq = max(longest_conseq, CharStatistics.longest_conseq(word))

            for c in word:
                chrs[c] += 1

            stats = CharStatistics.stats(word)
            for k, v in stats.items():
                sum[k] += v

        revs = self.revs(raw)
        return {
            't_cap': sum['capitalized'] / (1 + sum['alpha']),
            't_lgt_w': longest_word,
            't_cmpr': 1 if added_words == "" else len(compressor.compress(bytes(added_words, 'utf-8')) + compressor.flush())/(len(added_words) + 1),
            't_c_div': len(added_words) / (1 + len(chrs)),
            't_numalpha': sum['num'] / (1 + sum['alpha'] + sum['num']),
            't_lat': sum['latin'] / (1 + sum['alpha']),
            't_lgt_cs': longest_conseq,
            't_szdiff': (len(revs['current']['text'] or '') - len(revs['prev_user']['text'] or '')) if revs['prev_user'] is not None else 0,
            't_w_total': word_total
        }