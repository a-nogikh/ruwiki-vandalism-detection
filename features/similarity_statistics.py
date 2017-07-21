from .feature import Feature
from text.char_statistics import CharStatistics
from collections import defaultdict
import re


class PronounStatistics(Feature):
    pronouns={"я","мне","моей","моим","моему",
              "мы","наш","нашему", "наше", "наша",
              "ты","вы","тебе","вам","твой","твоему","твоей","твоим", "ваша", "ваше", "твое", "вашему"}

    def extract(self, raw):
        collection = raw["rwords"] if "rwords" in raw else {}

        revs = self.revs(raw)
        curr_text = (revs["current"]['text'] if revs['current'] is not None else '') or ''
        prev_text = (revs['prev_user']['text'] if revs['prev_user'] is not None else '') or ''

        diff_pronouns = defaultdict(int)
        added_words = 0

        for word, diff in collection.items():  # type: str,int
            if diff > 0:
                added_words += 1

            lower = word.lower()
            if lower not in self.pronouns:
                continue

            diff_pronouns[word.upper()] += diff

        before_cnt = 0
        for word in re.findall('[\w]+', prev_text):
            lower = word.lower()
            if lower in self.pronouns:
                before_cnt += 1

        total_pronouns_diff = sum(diff_pronouns.values())
        total_pronouns_diff_pos = total_pronouns_diff if total_pronouns_diff > 0 else 0

        return {
            'prn_diff': total_pronouns_diff,
            'prn_rel': (total_pronouns_diff_pos + before_cnt) / (before_cnt + 1),
            'prn_rel_edit': total_pronouns_diff_pos / (added_words + 1)
        }
