from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient, collection
from common.counter import Counter
from features import FEATURES_LIST
import os
from common.user_flags import UserFlagsTools, UserFlags

client = MongoClient('localhost', 27017)
load_dotenv(find_dotenv())

COLLECTION_NAME_ORIG = 'items'
COLLECTION_NAME_INTO = 'new_big_train'
COUNT = 15000

target_collection = client.wiki[COLLECTION_NAME_INTO]  # type: collection.Collection

TRUSTED_GROUPS = ['editor', 'rollbacker', 'reviewer', 'sysop', 'bureaucrat']
users = UserFlagsTools.load(os.environ['USER_FLAGS'])

cnt = Counter(100, COUNT)
for item in client.wiki[COLLECTION_NAME_ORIG].find({'vandal': False}, no_cursor_timeout=True).sort("r"):
    if len(item["revs"]) < 2:
        continue

    last_rev = item["revs"][-1]
    if not last_rev["flagged"]:
        continue

    if last_rev["user"]["id"] is not None:
        flags = users.get_flags(last_rev["user"]["id"])
        if flags is not None and any(1 for x in flags if x in TRUSTED_GROUPS):
            continue

    del item["_id"]
    target_collection.insert_one(item)
    cnt.tick()

    if cnt.value() > COUNT:
        break
