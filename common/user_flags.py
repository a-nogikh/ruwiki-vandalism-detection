import json
import pickle

from collections import defaultdict


class UserFlags:
    def __init__(self, json_file: str):
        self.lists = defaultdict(list)
        with open(json_file) as file:
            data = json.load(file)
            for item in data:
                self.lists[int(item["ug_user"])].append(item["ug_group"])

    def get_flags(self, user_id):
        return self.lists[user_id] if user_id in self.lists else None


class UserFlagsTools:
    @staticmethod
    def save(instance: UserFlags, name: str):
        output = open(name, 'wb')
        pickle.dump(instance, output)

    @staticmethod
    def load(name: str) -> UserFlags:
        pkl_file = open(name, 'rb')
        return pickle.load(pkl_file)
