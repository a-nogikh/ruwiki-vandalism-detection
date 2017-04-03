from pymongo import MongoClient, collection, ASCENDING
import json
from random import random, seed
from common.counter import Counter


COLLECTION_ORIG = 'labeled'
COLLECTION_INTO = 'manual_dataset'


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

