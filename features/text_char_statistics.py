from .feature import Feature
from text.char_statistics import CharStatistics
from collections import defaultdict
from lzma import LZMACompressor, FORMAT_ALONE
from common.utils import strip_accents
from collections import Counter

def check_cut(orig: str, cut:str):
    if len(orig) <= len(cut):
        return False

    diff_pos = 0
    for i, c in enumerate(orig):
        if i >= len(cut) or cut[i] != c:
            diff_pos = i
            break

    orig_left = orig[diff_pos:]
    cut_left = cut[diff_pos:]

    len_diff = len(orig_left) - len(cut_left)
    orig_left = orig_left[len_diff:]
    return orig_left == cut_left


class TextCharStatistics(Feature):
    russian_alphabet = {x for x in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"}
    abbrs = {'ОАО','ЗАО','АО','ТАСС','ЦБ','РФ','США','СССР','НАТО','КБК','ISDN'}
    allowed_rgb = {'0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'}

    def check_rgb(self, rgb:str):
        if len(rgb) != 8:
            return False
        for c in rgb.upper():
            if c not in self.allowed_rgb:
                return False

        return True

    def detect_wikification(self, prev, now):
        prev_cnt = Counter(prev)
        curr_cnt = Counter(now)

        good_inc = [u"\u00A0", u"\u00C2", "«", "»", "“", "”", "„", "±", "…"]
        return any(prev_cnt[x] < curr_cnt[x] for x in good_inc)

    def extract(self, raw):
        sum = CharStatistics.stats('')
        compressor = LZMACompressor(format=FORMAT_ALONE)

        longest_word = 0
        #longest_conseq = 0
        collection = raw["rwords"] if "rwords" in raw else {}
        chrs = defaultdict(int)
        added_words = ""
        sign_sums = [0, 0]
        been_mixed = 0

        dropped_upper = defaultdict(int)
        added_upper = defaultdict(int)
        for word, diff in collection.items():  # type: str,int
            if diff < 0:
                dropped_upper[word.upper()] -= diff
            elif diff > 0:
                added_upper[word.upper()] += diff

        for word, diff in collection.items():  # type: str,int
            upper = word.upper()
            if dropped_upper[upper] == added_upper[upper]:
                continue

            if diff < 0:
                sign_sums[0] += -diff
                continue


            sign_sums[1] += diff

            added_words += word
            longest_word = max(longest_word, len(word))
            #longest_conseq = max(longest_conseq, CharStatistics.longest_conseq(word))

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

            if word not in self.abbrs and not self.check_rgb(word):
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

        curr_cbr = [curr_text.count('{{'), curr_text.count('}}')]
        dbr_diff_o = (curr_cbr[0] - prev_text.count('{{'))
        dbr_diff_c = (curr_cbr[1] - prev_text.count('}}'))

        curr_rb = [curr_text.count('[['), curr_text.count(']]')]
        rbr_diff_o = (curr_rb[0] - prev_text.count('[['))
        rbr_diff_c = (curr_rb[1] - prev_text.count(']]'))

        punct_prev = 0
        for c in prev_text:
            if c in ['.', ',', '!', '?', ':']:
                punct_prev += 1

        punct_now = 0
        for c in curr_text:
            if c in ['.', ',', '!', '?', ':']:
                punct_now += 1

        main_curr = curr_text.count("{{main|")
        main_prev = prev_text.count("{{main|")

        longest_conseq = [CharStatistics.longest_conseq(prev_text), CharStatistics.longest_conseq(curr_text)]
        longest_conseq_upper = [CharStatistics.longest_upper(prev_text), CharStatistics.longest_upper(curr_text)]

        return {
            't_cap': sum['capitalized'] / (1 + sum['alpha']),
            't_cap_to_lwr': (sum['capitalized'] / (1 + sum['alpha'] - sum['capitalized'])),
            't_lgt_w': longest_word,
            #'t_cmpr': 1 if added_words == "" else len(compressor.compress(bytes(added_words, 'utf-8')) + compressor.flush())/(len(added_words) + 1),
            't_c_div': len(added_words) / (1 + len(chrs)),
            't_numalpha': sum['num'] / (1 + sum['alpha'] + sum['num']),
            't_lat': sum['latin'] / (1 + sum['alpha']),
            't_lgt_cs': longest_conseq[1],
            't_lgt_cs_rel': longest_conseq[1] / (longest_conseq[0] + 1),
            't_lgt_up': longest_conseq_upper[1],
            't_lgt_up_rel': longest_conseq_upper[1] / (longest_conseq_upper[0]  + 1),
            't_szdiff': (len(curr_text)- len(prev_text)),
            't_sz_rel': (1  + len(curr_text)) / (1+len(prev_text)),
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
            't_dbr_curr': abs(curr_cbr[0] - curr_cbr[1]),
            't_rbr_o_diff': rbr_diff_o,
            't_rbr_c_diff': rbr_diff_o,
            't_rbr_diff': abs(rbr_diff_o - rbr_diff_c),
            't_rbr_curr': abs(curr_rb[0] - curr_rb[1]),
            't_w_mixed': been_mixed / (1 + sign_sums[1]),
            't_cut': 1 if check_cut(prev_text, curr_text) else 0,
            't_punct_diff': punct_now - punct_prev,
            't_punct_words': (punct_now - punct_prev)/(sign_sums[1] - sign_sums[0] + 0.9),
            't_main_diff': (main_curr - main_prev),
            't_diff_rel': (sign_sums[1] - sign_sums[0]) / (1 + min(sign_sums)),
            't_wikificated': 1 if self.detect_wikification(prev_text, curr_text) else 0
        }
