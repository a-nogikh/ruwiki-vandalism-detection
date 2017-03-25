from collections import defaultdict


class PartsDiff:
    @staticmethod
    def words_sum(list_before: [str], list_after: [str]):
        ans = defaultdict(int)
        for item in list_before:
            ans[item] -= 1

        for item in list_after:
            ans[item] += 1

        res = dict()
        for key in ans:
            val = ans[key]
            if val == 0: continue
            res[key] = 1 if val >= 0 else -1

        return res
