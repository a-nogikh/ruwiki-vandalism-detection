
class Feature:
    def extract(self, raw):
        raise Exception()

    @staticmethod
    def revs(raw):
        answer = {
            "current": None,
            "prev_user": None,
            "trusted": None,
            "flagged": None
        }

        revs = raw["revs"]
        if len(revs) == 0:
            return answer

        last_rev = revs[-1]
        answer["current"] = last_rev
        if raw["last_flagged"] is not None:
            answer["flagged"] = raw["last_flagged"]

        for rev in reversed(revs):
            if answer["prev_user"] is None and \
                            rev["user"]["name"] != last_rev["user"]["name"]:
                answer["prev_user"] = rev

            if rev["id"] == raw["last_trusted"]:
                answer["trusted"] = rev

            if answer["prev_user"] is not None and \
                    (answer["trusted"] is not None or raw["last_trusted"] is None):
                break

        return answer

    def last_rev(self, raw):
        return raw["revs"][-1] or None

