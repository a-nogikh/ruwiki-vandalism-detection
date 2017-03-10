
REVERT_STRINGS = [
    "откат]]", "]] Откат", ") откачены к версии"
]

CANCEL_STRINGS = [
    "|отмена]]", "]] Отмена", "Отмена правки "
]


class RevisionTools:
    @staticmethod
    def cancels_id(comment):
        if comment is None:
            return None

        if not any(x in comment for x in CANCEL_STRINGS):
            return None

        nums = [int(s) for s in comment.split() if s.isdigit()]
        return nums[0]

    @staticmethod
    def is_reverting(comment):
        if comment is None:
            return None
        return any(x in comment for x in REVERT_STRINGS)
