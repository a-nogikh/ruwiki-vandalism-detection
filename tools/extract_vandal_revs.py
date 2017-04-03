from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient, collection
from common.counter import Counter
from features import FEATURES_LIST
import os
from common.user_flags import UserFlagsTools, UserFlags

client = MongoClient('localhost', 27017)

COLLECTION_NAME_ORIG = 'items'
COLLECTION_NAME_INTO = 'new_big_train'
COUNT = 15000

target_collection = client.wiki[COLLECTION_NAME_INTO]  # type: collection.Collection


cnt = Counter(100, COUNT)
for item in client.wiki[COLLECTION_NAME_ORIG].find({'vandal': True}, no_cursor_timeout=True).sort("r"):
    if len(item["revs"]) < 2:
        continue

    del item["_id"]
    target_collection.insert_one(item)
    cnt.tick()

    if cnt.value() > COUNT:
        break
