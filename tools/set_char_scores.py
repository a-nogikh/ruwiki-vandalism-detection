from pymongo import MongoClient, collection
import math
from features.feature import Feature
import collections
from common.counter import Counter


def calculate(revs):
    prev_text = revs["prev_user"]["text"] or ''
    curr_text = revs["current"]["text"] or ''
    prev_distr = collections.Counter(prev_text.lower())
    distr = collections.Counter(curr_text.lower())

    for c in distr:
        if c in prev_distr:
            distr[c] -= prev_distr[c]

    for c in prev_distr:
        if c not in distr:
            distr[c] = -prev_distr[c]

    distr = {x:y for x,y in distr.items() if y > 0}
    total_diff = sum(abs(x) for x in distr.values() )

    if total_diff != 0:
        for c in distr:
            distr[c] /= total_diff

    return distr


def KLdist(distr, prior):
    ans = 0
    for c,pr in distr.items():
        if c in prior:
            ans += pr * math.log2(pr / prior[c])

    return ans

client = MongoClient('localhost', 27017)

allowed="abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя0123456789+-~.,?!:;=\"|{} \n\r\t"

vandal_distr = dict()
good_distr = dict()
for c in allowed:
    vandal_distr[c] = 0
    good_distr[c] = 0

total_cnt = 0

raw_list = []
raw_res = []
cnt = Counter(50)
for raw in client.wiki['train_combiner'] .find({}):
    if len(raw["revs"]) <= 1:
        continue

    revs = Feature.revs(raw)
    if revs["prev_user"] is None:
        continue

    distr = calculate(revs)

    if raw["vandal"]:
        pass
        #for c,k in distr.items():
        #    if c in vandal_distr:
        #        vandal_distr[c] += k
    else:
        for c,k in distr.items():
            if c in good_distr:
                good_distr[c] += k
        
    total_cnt += 1

    raw_list.append({key: value for key, value in distr.items() })
    raw_res.append(1 if raw["vandal"] else 0)
    cnt.tick()

for c in vandal_distr:
    vandal_distr[c] /= total_cnt
    good_distr[c] /= total_cnt
    print("{}: {} / {}".format(c, vandal_distr[c], good_distr[c] ))

from sklearn.feature_extraction import FeatureHasher
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

print(len(raw_list))

fh = FeatureHasher(2000000)
matrix = fh.transform(raw_list)

lr = LogisticRegression(solver='sag', verbose=1, max_iter=100, C=0.5)
lc = LinearSVC(verbose=1, max_iter=1000, C=0.05)

#lr.fit(matrix, raw_res)
#lc.fit(matrix, raw_res)


def set_features(collection_name):
    raw_list = []
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

        collection.update_one({"_id": raw["_id"]}, {"$set": {
            "f.t_charscore": KLdist(distr, good_distr)
        }})

        raw_list.append({key: value for key, value in distr.items()})
        raw_ids.append(raw["_id"])
        counter.tick()

    '''
    pred = lr.predict_proba(fh.transform(raw_list))
    for i, x in enumerate(pred[:, 1]):
        collection.update_one({"_id": raw_ids[i]}, {"$set": {
            "f.t_charscore": x
        }})
    '''

print("Test..")
set_features('manual_dataset')

#print("Combiner..")
#set_features('train_combiner')

print("Train..")
set_features('new_big_train')

