

class User:
    def __init__(self,
                 id=None,
                 name=None,
                 flags=[]):
        """
        @type id: int
        @type name: str
        @type flags: [str]
        """

        self.id = id
        self.name = name
        self.flags = flags

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_object(self):
        return {
            "id": self.id,
            "name": self.name
        }
