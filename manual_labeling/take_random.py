from pymongo import MongoClient, collection, ASCENDING
import json
import random
from common.counter import Counter

SOURCE_FILE = '/media/sf_parts/revids.txt'
TAKE_SAMPLES = 20000
COLLECTION_NAME = 'labeled'
APPEND_TO_COLLECTION = True


client = MongoClient('localhost', 27017)
db = client.wiki
db_coll = db[COLLECTION_NAME] # type: collection.Collection

if not APPEND_TO_COLLECTION:
    db_coll.delete_many({})
    db_coll.drop_indexes()
    db_coll.create_index([("flagged_user", ASCENDING)])
    db_coll.create_index([("status", ASCENDING)])

random.seed()
with open(SOURCE_FILE) as data_file:
    array = json.load(data_file)
    if len(array) < TAKE_SAMPLES:
        print("The file contains only {} samples!".format(len(array)))
        exit()

    if APPEND_TO_COLLECTION:
        existing_ids = {x["q"]["id"] for x in db_coll.find({})}
        array = [(a,b) for a,b in array if a not in existing_ids]
        print("Items are filtered with {} existing ids!".format(len(existing_ids)))

    random.shuffle(array)
    bucket_array = []
    cnt = Counter(100)
    for k in range(0, TAKE_SAMPLES):
        bucket_array.append({
            'q': {
                "id": array[k][0],
                "title": array[k][1]
            },
            'info': None,
            'flagged_user': 0,
            'status': 0,
            'is_auto': False,
            'is_skipped': False,
            'is_trusted': False
        })

        if len(bucket_array) > 100:
            db_coll.insert_many(bucket_array)
            bucket_array.clear()

        cnt.tick()

    if len(bucket_array) > 0:
        db_coll.insert_many(bucket_array)
