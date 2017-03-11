import re

REVERT_STRINGS = [
    "откат]]", "]] Откат", ") откачены к версии"
]

CANCEL_STRINGS = [
    "|отмена]]", "]] Отмена", "Отмена правки "
]

find_numbers = re.compile('(\d+)')


class RevisionTools:
    @staticmethod
    def cancels_id(comment):
        if comment is None:
            return None

        if not any(x in comment for x in CANCEL_STRINGS):
            return None

        lst = find_numbers.search(comment)
        if lst is None:
            return None
        return int(lst.group(0))

    @staticmethod
    def is_reverting(comment):
        if comment is None:
            return None
        return any(x in comment for x in REVERT_STRINGS)
