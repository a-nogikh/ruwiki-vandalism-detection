from pymongo import MongoClient, collection
from sklearn.feature_extraction import FeatureHasher
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from features.feature import Feature
import collections
from common.counter import Counter


def calculate(revs):
    prev_distr = collections.Counter(revs["prev_user"]["text"])
    distr = collections.Counter(revs["current"]["text"])

    for c in distr:
        if c in prev_distr:
            distr[c] -= prev_distr[c]

    for c in prev_distr:
        if c not in distr:
            distr[c] = -prev_distr[c]

    total_diff = sum(abs(x) for x in distr.values())

    #if total_diff != 0:
    #    for c in prev_distr:
    #        distr[c] /= total_diff

    return distr

client = MongoClient('localhost', 27017)

raw_list = []
raw_res = []
for raw in client.wiki['new_big_train'] .find({}):
    if len(raw["revs"]) <= 1:
        continue

    revs = Feature.revs(raw)
    if revs["prev_user"] is None:
        continue

    distr = calculate(revs)

    raw_list.append(distr)
    raw_list.append({key: value * -1 for key, value in distr.items()})
    raw_res.append(1 if raw["vandal"] else 0)
    raw_res.append(1 if not raw["vandal"] else 0)

print(len(raw_list))

fh = FeatureHasher(2000000)
matrix = fh.transform(raw_list)

lr = LogisticRegression(solver='sag', verbose=1, max_iter=200, C=1)
lc = LinearSVC(verbose=1, max_iter=1000, C=0.05)

lr.fit(matrix, raw_res)
#lc.fit(matrix, raw_res)


def set_features(collection_name):
    raw_list = []
    raw_res = []
    raw_ids = []
    counter = Counter(100)
    collection = client.wiki[collection_name]  # type: collection.Collection
    for raw in collection.find({}):
        if len(raw["revs"]) <= 1:
            continue

        revs = Feature.revs(raw)
        if revs["prev_user"] is None:
            continue

        distr = calculate(revs)

        raw_list.append(distr)
        raw_res.append(1 if raw["vandal"] else 0)
        raw_ids.append(raw["_id"])
        counter.tick()

    pred = lr.predict_proba(fh.transform(raw_list))
    for i, x in enumerate(pred[:, 1]):
        collection.update_one({"_id": raw_ids[i]}, {"$set": {
            "f.t_charscore": x
        }})


print("Test..")
set_features('manual_dataset')

print("Combiner..")
set_features('train_combiner')

#print("Train..")
#set_features('new_train')

