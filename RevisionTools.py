
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

        if not [x for x in CANCEL_STRINGS if x in comment]:
            return None

        nums = [int(s) for s in comment.split() if s.isdigit()]
        return nums[0]

    @staticmethod
    def is_reverting(comment):
        if comment is None:
            return None
        return [x for x in REVERT_STRINGS if x in comment]
