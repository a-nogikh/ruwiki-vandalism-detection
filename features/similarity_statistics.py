from .feature import Feature
from text.char_statistics import CharStatistics
from collections import defaultdict
import re


class SimilarityStatistics(Feature):

    def extract(self, raw):
        collection = raw["rwords"] if "rwords" in raw else {}

        revs = self.revs(raw)
        curr_text = (revs["current"]['text'] if revs['current'] is not None else '') or ''
        prev_text = (revs['prev_user']['text'] if revs['prev_user'] is not None else '') or ''

        curr_text = curr_text.lower()
        prev_text = prev_text.lower()

        bigrams = raw["bigram_stemmed"] if "bigram_stemmed" in raw else {}

        added = [0, 0]
        dropped = [0, 0]
        for word, diff in bigrams.items():
            if ' ' in word:
                continue

            if diff > 0:
                added[1] += 1
                added[0] += 1 if word in prev_text else 0
            else:
                dropped[1] += 1
                dropped[0] += 1 if word in curr_text else 0

        added_score = 0 if added[1] == 0 else added[0] / added[1]
        dropped_score = 0 if dropped[1] == 0 else dropped[0] / dropped[1]



        return {
            'ss_added': added_score,
            'ss_dropped': dropped_score,
            'ss_diff': added_score - dropped_score
        }
