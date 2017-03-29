from datetime import datetime
from .user import User


class Revision:
    __slots__ = ['id','comment','timestamp','user','minor','flagged','text']

    def __init__(self,
                 id=None,
                 timestamp=None,
                 comment=None,
                 user=None,
                 minor=False,
                 flagged=False,
                 text=None):
        """
        @type id: int
        @type comment: str
        @type timestamp: datetime
        @type user: User
        @type minor: bool
        @type flagged: bool
        @type text: str
        """

        self.id = id
        self.comment = comment
        self.timestamp = timestamp
        self.user = user
        self.minor = minor
        self.flagged = flagged
        self.text = text

    def to_object(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "comment": self.comment,
            "flagged": self.flagged,
            "minor": self.minor,
            "user": None if self.user is None else self.user.to_object(),
            "text": self.text
        }
