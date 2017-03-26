from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient, collection
from common.counter import Counter
from features import FEATURES_LIST


load_dotenv(find_dotenv())

COLLECTION_NAME = 'test_small'
REQUIRED_FEATURES = ['*']

client = MongoClient('localhost', 27017)
raw_collection = client.wiki[COLLECTION_NAME]  # type: collection.Collection

features_list = dict()
if len(REQUIRED_FEATURES) == 1 and REQUIRED_FEATURES[0] == '*':
    features_list = FEATURES_LIST
else:
    for key, val in enumerate(FEATURES_LIST):
        if key in REQUIRED_FEATURES:
            features_list[key] = val

for key in features_list:
    features_list[key] = features_list[key]()

cnt = Counter(100, raw_collection.count())
for raw in raw_collection.find({}, no_cursor_timeout = True):
    if raw["revs"] is None or len(raw["revs"]) <= 1:
        continue

    f = (raw["f"] if "f" in raw else None) or dict()
    for key in features_list:
        res = features_list[key].extract(raw)
        if type(res) is dict:
            f.update(res)
        else:
            f[key] = res

    raw_collection.update_one({
        "_id": raw["_id"]
    }, {
        "$set": {
            "f": f
        }
    })

    cnt.tick()