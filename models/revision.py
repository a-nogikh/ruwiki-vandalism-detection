from datetime import datetime


class User:
    pass


class RegisteredUser(User):
    def __init__(self, user_id: int, user_name: str):
        self.user_id = user_id
        self.user_name = user_name

    def __eq__(self, other):
        return self.user_id == other.user_id


class Guest(User):
    def __init__(self, ip: str):
        self.ip = ip

    def __eq__(self, other):
        return self.ip == other.ip


class Revision:
    def __init__(self,
                 rev_id: int,
                 user: User,
                 timestamp: datetime,
                 comment: str,
                 is_minor: bool = False,
                 is_reviewed: bool = False):
        self.rev_id = rev_id
        self.user = user
        self.timestamp = timestamp
        self.comment = comment
        self.is_minor = is_minor
        self.is_reviewed = is_reviewed

    def __eq__(self, other):
        return self.rev_id == other.rev_id \
            and self.user == other.user \
            and self.timestamp == other.timestamp \
            and self.comment == other.comment \
            and self.is_minor == other.is_minor \
            and self.is_reviewed == other.is_reviewed
