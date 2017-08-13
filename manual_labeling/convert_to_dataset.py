from pymongo import MongoClient, collection, ASCENDING
import json
from random import random, seed
from common.counter import Counter


COLLECTION_ORIG = 'manual_new_raw'
COLLECTION_INTO = 'manual_new'


client = MongoClient('localhost', 27017)
db = client.wiki
db_coll = db[COLLECTION_INTO] # type: collection.Collection

db_coll.delete_many({})

seed()
for item in db[COLLECTION_ORIG].find({"is_auto": False, "status": {"$in": [1,2]}}):
    src = item["info"]
    src.update({
        "r": random(),
        "vandal": item["status"] == 2
    })

    db_coll.insert_one(src)


