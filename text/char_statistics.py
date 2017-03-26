
class CharStatistics:

    @staticmethod
    def stats(text: str) -> dict:
        res = {
            'num': 0,
            'alpha': 0,
            'capitalized': 0
        }
        for c in text:
            if c.isalpha():
                res['alpha'] += 1
                if c.isupper():
                    res['capitalized'] += 1

            if c.isnumeric():
                res['num'] += 1

        return res

    @staticmethod
    def longest_conseq(text: str) -> int:
        prev = None
        current_len = 0
        max_len = 0

        for c in text:
            if c == prev:
                current_len += 1
            else:
                current_len = 1

            if not c.isalnum():
                current_len = 0
                prev = None
            else:
                prev = c

            max_len = max(max_len, current_len)

        return max_len
