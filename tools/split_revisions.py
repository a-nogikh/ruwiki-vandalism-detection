from random import random, seed

import pymongo
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient, collection
from common.counter import Counter
from common.utils import query_yes_no

load_dotenv(find_dotenv())

if not query_yes_no("Do you really want to reset collections?"):
    exit()

KEEP_VANDAL = 100
KEEP_NON_VANDAL = 100
KEEP_TEST_VANDAL = 100
KEEP_TEST_NON_VANDAL = 100
TEST_COLLECTION_NAME = 'test_small'
TRAIN_COLLECTION_NAME = 'train_small'

client = MongoClient('localhost', 27017)

items_collection = client.wiki.items  # type: collection.Collection
test_collection = client.wiki[TEST_COLLECTION_NAME]  # type: collection.Collection
train_collection = client.wiki[TRAIN_COLLECTION_NAME] # type: collection.Collection

for collection in [test_collection, train_collection]:
    collection.delete_many({})
    collection.drop_indexes()
    collection.create_index([("r", pymongo.ASCENDING)])

vandal_items = items_collection.find({'vandal': True}).count()
not_vandal_items = items_collection.find({'vandal': True}).count()

if (KEEP_VANDAL + KEEP_TEST_VANDAL) > vandal_items:
    print("Need more vandal items!")
    exit()

if (KEEP_NON_VANDAL + KEEP_TEST_NON_VANDAL) > not_vandal_items:
    print("Need more good items!")
    exit()

# set random field
seed()
random_counter = Counter(100)
for item in items_collection.find({}, no_cursor_timeout=True):
    items_collection.update_one({'_id': item['_id']}, {
        '$set':{
                'r': random()
            }
        })
    random_counter.tick()

print("Random elements created")
indices = items_collection.index_information()
if 'random' not in indices:
    print("Creating index")
    items_collection.create_index([
            ("vandal", pymongo.ASCENDING),
            ("r", pymongo.ASCENDING)
        ],
        name="random")
    print("Index created")

# getting vandal
print("Processing vandal:true")
cnt = 0; vandal_counter = Counter(100)
for item in items_collection.find({'vandal': True}).sort("r").limit(KEEP_VANDAL + KEEP_TEST_VANDAL):
    cnt += 1
    item["r"] = random()
    del item["_id"]
    if cnt > KEEP_VANDAL:
        test_collection.insert_one(item)
    else:
        train_collection.insert_one(item)

    vandal_counter.tick()

# getting good
print("Processing vandal:false")
cnt = 0; good_counter = Counter(100)
for item in items_collection.find({'vandal': True}).sort("r").limit(KEEP_NON_VANDAL + KEEP_TEST_NON_VANDAL):
    cnt += 1
    item["r"] = random()
    del item["_id"]
    if cnt > KEEP_NON_VANDAL:
        test_collection.insert_one(item)
    else:
        train_collection.insert_one(item)

    good_counter.tick()