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
    def __init__(self, rev_id: int, user: User, time: datetime, comment: str):
        self.rev_id = rev_id
        self.user = user
        self.time = time
        self.comment = comment
