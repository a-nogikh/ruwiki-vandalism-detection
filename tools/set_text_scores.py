from pymongo import MongoClient, collection
from sklearn.feature_extraction import FeatureHasher
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from common.counter import Counter

TEXT_FEATURE_KEY = 'bigram_stemmed'

client = MongoClient('localhost', 27017)

def sign(x: int) -> int:
    return 1 if x > 0 else -1


allowed_rgb = {'0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'}


def check_rgb(rgb: str):
    if len(rgb) != 8:
        return False
    for c in rgb.upper():
        if c not in allowed_rgb:
            return False

    return True

raw_list = []
raw_res = []

raw_list_opp = []

counter = Counter(100)
for raw in client.wiki['new_big_train'] .find({}, {'vandal': 1,  TEXT_FEATURE_KEY: 1}): #strict_train
    if TEXT_FEATURE_KEY not in raw or len(raw[TEXT_FEATURE_KEY]) == 0:
        continue

    #if len(raw["revs"]) <= 1:
    #    continue

    filtered = {x: sign(y) for x, y in raw[TEXT_FEATURE_KEY].items() if not x.isdigit()}
    filtered2 = {x:y for x,y in filtered.items() if y > 0 and not check_rgb(x) and ' ' not in x}
    #filtered3 = {x: y *(-1) for x, y in filtered.items() if y < 0 and not check_rgb(x)}

    raw_list.append(filtered2)
    raw_res.append(1 if raw["vandal"] else 0)

    raw_list_opp.append({x:y*(-1) for x,y in filtered.items() if y < 0 and not check_rgb(x) and ' ' not in x})

    counter.tick()

print(len(raw_list))
from sklearn.naive_bayes import GaussianNB
fh = FeatureHasher(2000000)
matrix = fh.transform(raw_list)
matrix_opp = fh.transform(raw_list_opp)

lr = LogisticRegression(solver='sag', verbose=1, max_iter=100, C=0.1)
#lr = GaussianNB()
lr.fit(matrix, raw_res)

lr2 = LogisticRegression(solver='sag', verbose=1, max_iter=100, C=0.1)
#lr2 = GaussianNB()
lr2.fit(matrix_opp, raw_res)



def set_features(collection_name):
    raw_list = []
    raw_res = []
    raw_ids = []
    raw_list_opp = []
    counter = Counter(100)
    collection = client.wiki[collection_name]  # type: collection.Collection
    for raw in collection.find({}, {"_id": 1, TEXT_FEATURE_KEY: 1, "vandal": 1}):
        if TEXT_FEATURE_KEY not in raw or len(raw[TEXT_FEATURE_KEY]) == 0:
            continue

        filtered = {x: sign(y)  for x, y in raw[TEXT_FEATURE_KEY].items() if not x.isdigit()}
        filtered2 = {x: y for x, y in filtered.items() if y > 0 and not check_rgb(x) and ' ' not in x}

        raw_list.append(filtered2)
        raw_list_opp.append({x: y * (-1) for x, y in filtered.items() if y < 0 and not check_rgb(x) and ' ' not in x})
        #raw_list.append(raw[TEXT_FEATURE_KEY])
        raw_res.append(1 if raw["vandal"] else 0)
        raw_ids.append(raw["_id"])
        counter.tick()

    pred = lr.predict_proba(fh.transform(raw_list))
    pred2 = lr2.predict_proba(fh.transform(raw_list_opp))
    for i, x in enumerate(pred[:, 1]):
        collection.update_one({"_id": raw_ids[i]}, {"$set": {
            "f.t_biscore": max(x,pred2[i,1])
        }})


print("Test..")
set_features('manual_dataset')

print("Combiner..")
set_features('train_combiner')

#print("Train..")
#set_features('new_train')