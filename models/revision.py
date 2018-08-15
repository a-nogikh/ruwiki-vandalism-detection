from datetime import datetime, timedelta


class User:
    pass


class RegisteredUser(User):
    def __init__(self, user_id: int, user_name: str):
        self.user_id = user_id
        self.user_name = user_name

    def __eq__(self, other):
        return self.user_id == other.user_id

    def __repr__(self):
        return "RegisteredUser(user_id: {!r}, user_name: {!r})".format(
            self.user_id,
            self.user_name)

    def __str__(self):
        return self.user_name


class Guest(User):
    def __init__(self, ip: str):
        self.ip = ip

    def __eq__(self, other):
        return self.ip == other.ip

    def __repr__(self):
        return "Guest(ip: {!r})".format(self.ip)

    def __str__(self):
        return self.ip


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
        
    def timedelta_with(self, other: "Revision") -> timedelta:
        return self.timestamp - other.timestamp

    def __eq__(self, other):
        return self.rev_id == other.rev_id \
            and self.user == other.user \
            and self.timestamp == other.timestamp \
            and self.comment == other.comment \
            and self.is_minor == other.is_minor \
            and self.is_reviewed == other.is_reviewed

    def __repr__(self):
        return "Revision(rev_id: {!r}, user: {!r}, timestamp: {!r}, comment: {!r})".format(
            self.rev_id,
            self.user,
            self.timestamp,
            self.comment)
