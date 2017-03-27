from pymongo import MongoClient, collection
from sklearn.feature_extraction import FeatureHasher
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from common.counter import Counter

TEXT_FEATURE_KEY = 'bigram_stemmed'

client = MongoClient('localhost', 27017)

raw_list = []
raw_res = []
counter = Counter(100)
for raw in client.wiki['train_small'] .find({}, {'vandal': 1,  TEXT_FEATURE_KEY: 1}):
    if TEXT_FEATURE_KEY not in raw or len(raw[TEXT_FEATURE_KEY]) == 0:
        continue

    #if len(raw["revs"]) <= 1:
    #    continue

    filtered = {x: y for x, y in raw[TEXT_FEATURE_KEY].items() if not x.isdigit()}
    raw_list.append(filtered)
    #raw_list.append(raw[TEXT_FEATURE_KEY])
    raw_list.append({key: value * -1 for key, value in filtered.items()})
    raw_res.append(1 if raw["vandal"] else 0)
    raw_res.append(1 if not raw["vandal"] else 0)
    counter.tick()

print(len(raw_list))

fh = FeatureHasher(2000000)
matrix = fh.transform(raw_list)

lr = LogisticRegression(solver='sag', verbose=1, max_iter=100, C=0.5)
#lc = LinearSVC(verbose=1, max_iter=1000, C=0.05)

lr.fit(matrix, raw_res)

def set_features(collection_name):
    raw_list = []
    raw_res = []
    raw_ids = []
    counter = Counter(100)
    collection = client.wiki[collection_name]  # type: collection.Collection
    for raw in collection.find({}, {"_id": 1, TEXT_FEATURE_KEY: 1, "vandal": 1}):
        if TEXT_FEATURE_KEY not in raw or len(raw[TEXT_FEATURE_KEY]) == 0:
            continue

        filtered = {x: y for x, y in raw[TEXT_FEATURE_KEY].items() if not x.isdigit()}
        raw_list.append(filtered)
        #raw_list.append(raw[TEXT_FEATURE_KEY])
        raw_res.append(1 if raw["vandal"] else 0)
        raw_ids.append(raw["_id"])
        counter.tick()

    pred = lr.predict_proba(fh.transform(raw_list))
    for i, x in enumerate(pred[:, 1]):
        collection.update_one({"_id": raw_ids[i]}, {"$set": {
            "f.t_biscore": x
        }})


print("Test..")
set_features('test_small')
print("Train..")
set_features('train_small')