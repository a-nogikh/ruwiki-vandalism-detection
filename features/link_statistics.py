from .feature import Feature
import re
from difflib import SequenceMatcher


class LinkStatistics(Feature):
    link_regexp = re.compile('\[\[([^\|\]]+)\|([^\]]+)\]\]')  #   \[\[([\:\d\w\s\-\_]+)\|([\:\d\-\_\w\s]+)\]\]
    link_single = re.compile('\[\[([^\]]+)\]\]')

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def check_illogical(self, a, b):
        if len(a) > 5 or len(b) > 5:
            return 1

        a_has_digits = False
        for x in a:
            if x.isdigit():
                a_has_digits = True
                break

        min_score = 1
        for x in b:
            if x.isdigit() and x not in a and a_has_digits:
                return 0

            if x in a:
                min_score = 1
                continue

            max_score = 0
            for a_item in a:
                max_score = max(max_score, self.similar(x, a_item))

            min_score = max(min_score, max_score)

        return min_score

    def extract(self, raw):
        revs = self.revs(raw)
        curr_text = (revs["current"]['text'] if revs['current'] is not None else '') or ''
        prev_text = (revs['prev_user']['text'] if revs['prev_user'] is not None else '') or ''

        curr_text = curr_text.lower()
        prev_text = prev_text.lower()

        #if raw["page"]["id"] == 6737949:
        #    print("ello")

        worst_new_link = 1
        avg_new_link = list()
        prev_links = { x for x in self.link_regexp.findall(prev_text)}
        prev_firsts = { x[0].strip() for x in prev_links } | {x.strip() for x in self.link_single.findall(prev_text)}


        for new_link in self.link_regexp.findall(curr_text):
            if new_link in prev_links:
                continue

            first = new_link[0].strip()
            if first not in prev_firsts:
                continue

            second = new_link[1].strip()
            #print(first)
            if first.startswith(":") or len(first) < 4 or len(second) < 4:
                continue

            #print(new_link)
            link = list(re.findall("[^\s,]+", first))
            title = list(re.findall("[^\s,]+", second))
            #print("_".join(link) + " / " + "_".join(title))

            score = self.check_illogical(link, title)
            if score < 0.3 and revs["current"] is not None and revs["prev_user"] is not None:
                url = "https://ru.wikipedia.org/w/index.php?type=revision&diff={}&oldid={}".format(
                    revs["current"]["id"], revs["prev_user"]["id"]
                )
                #print(str(new_link) + " :: " + str(raw["vandal"]))
                #print(url)

            worst_new_link = min(worst_new_link, score)
            avg_new_link.append(score)

        return {
            'link_worst': worst_new_link,
            'link_avg_new': 1 if len(avg_new_link) == 0 else sum(avg_new_link) / len(avg_new_link)
        }
