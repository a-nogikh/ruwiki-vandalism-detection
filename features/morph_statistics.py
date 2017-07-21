from .feature import Feature
from text.char_statistics import CharStatistics
from collections import defaultdict
import re
import pymorphy2


class MorphStatistics(Feature):
    morph = pymorphy2.MorphAnalyzer()
    def extract(self, raw):

        data = raw["rwords"] if "rwords" in raw else {}
        data_lower = defaultdict(int)
        for k,v in data.items():
            data_lower[k] += v

        has_1per = 0
        has_indc = 0
        has_supr = 0
        has_abbr = 0

        for word, diff in data_lower.items(): # type: str
            if diff <= 0:
                continue

            if not word.islower() or any(x.isdigit() for x in word):
                continue

            parsed_all = self.morph.parse(word)

            if 'Dist' in parsed_all[0].tag :
                print(word + ":: "+str(parsed_all[0].tag) + " ! " +  str(raw["vandal"]))
            continue
            if 'Abbr' in parsed_all[0].tag :
                has_abbr = 1
                #print(word + ":: "+str(parsed_all[0].tag) + " ! " +  str(raw["vandal"]))
            continue


            skip_v = 0
            all_1per = 1
            for one in parsed_all:
                if not any (x in one.tag for x in ['NPRO','VERB']):
                    skip_v = 1
                    continue

                if '1per' not in one.tag:
                    all_1per = 0

            parsed = parsed_all[0].tag
            if skip_v == 0 and all_1per:
                print(word )
                has_1per = 1

            if 'indc' in parsed:
                has_indc = 1

            if 'Supr' in parsed:
                has_supr = 1


        return {
            'mf_abbr': has_abbr,
            'mf_1per': has_1per,
            'mf_indc': has_indc,
            'mf_supr': has_supr
        }
