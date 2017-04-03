from .feature import Feature
from text.char_statistics import CharStatistics
from collections import defaultdict
from lzma import LZMACompressor, FORMAT_ALONE
from common.utils import strip_accents


class TextCharStatistics(Feature):
    russian_alphabet = {x for x in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"}
    def extract(self, raw):
        sum = CharStatistics.stats('')
        compressor = LZMACompressor(format=FORMAT_ALONE)

        longest_word = 0
        longest_conseq = 0
        collection = raw["rwords"] if "rwords" in raw else {}
        chrs = defaultdict(int)
        added_words = ""
        sign_sums = [0, 0]
        been_mixed = 0

        for word, diff in collection.items():  # type: str,int
            if diff < 0:
                sign_sums[0] += -diff
                continue

            sign_sums[1] += diff

            added_words += word
            longest_word = max(longest_word, len(word))
            longest_conseq = max(longest_conseq, CharStatistics.longest_conseq(word))

            been_latin = False
            been_non_latin = False
            for c in word:
                chrs[c] += 1

                if not been_latin or not been_non_latin:
                    if c == '-':
                        been_latin = False
                        been_non_latin = False
                    elif c.isalpha():
                        if ord(c) < 128:
                            been_latin = True
                        elif c.lower() in self.russian_alphabet:
                            been_non_latin = True

            if been_latin and been_non_latin:
                been_mixed += 1

            stats = CharStatistics.stats(word)
            for k, v in stats.items():
                sum[k] += v

        revs = self.revs(raw)
        curr_text = (revs["current"]['text'] if revs['current'] is not None else '')  or ''
        prev_text = (revs['prev_user']['text'] if revs['prev_user'] is not None else '') or ''

        curr_text = curr_text.replace("\r\n","\n")
        prev_text = prev_text.replace("\r\n", "\n")
        nl_diff = (curr_text.count('\n') - prev_text.count('\n'))
        nl2_diff = (curr_text.count('\n\n') - prev_text.count('\n\n'))

        dbr_diff_o = (curr_text.count('{{') - prev_text.count('{{'))
        dbr_diff_c = (curr_text.count('}}') - prev_text.count('}}'))

        return {
            't_cap': sum['capitalized'] / (1 + sum['alpha']),
            't_lgt_w': longest_word,
            't_cmpr': 1 if added_words == "" else len(compressor.compress(bytes(added_words, 'utf-8')) + compressor.flush())/(len(added_words) + 1),
            't_c_div': len(added_words) / (1 + len(chrs)),
            't_numalpha': sum['num'] / (1 + sum['alpha'] + sum['num']),
            't_lat': sum['latin'] / (1 + sum['alpha']),
            't_lgt_cs': longest_conseq,
            't_szdiff': (len(curr_text)- len(prev_text)),
            't_w_total': sign_sums[1] - sign_sums[0],
            't_w_added': sign_sums[1],
            't_w_deleted': sign_sums[0],
            't_mdf_wrds': min(sign_sums),
            't_nl_diff': nl_diff,
            't_nl2_diff': nl2_diff,
            't_nl_wrds': nl_diff / (1 + sign_sums[1]),
            't_dbr_o_diff': dbr_diff_o,
            't_dbr_c_diff': dbr_diff_c,
            't_dbr_diff': abs(dbr_diff_o-dbr_diff_c),
            't_w_mixed': been_mixed / (1 + sign_sums[1])
        }