from pymongo import MongoClient, collection
from common.counter import Counter

client = MongoClient('localhost', 27017)

raw_list = []
raw_res = []
cnt = Counter(100)
for raw in client.wiki['train_small'] .find({}):
    if "f" not in raw or len(raw["f"]) < 19:
        continue

    raw_list.append([x for x in raw["f"].values()])
    raw_res.append(1 if raw["vandal"] else 0)
    cnt.tick()


from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestClassifier
from numpy import matrix
from sklearn.svm import LinearSVC


frst = RandomForestClassifier(n_estimators=1500, verbose=1, max_features=7)
frst.fit(matrix(raw_list), raw_res)
lc = LinearSVC(verbose=1, max_iter=1000, C=0.05)
#lc.fit(matrix(raw_list), raw_res)

raw_list = []
raw_res = []
for raw in client.wiki['test_small'] .find({}):
    if "tmp" not in raw or len(raw["tmp"]) == 0:
        continue

    if len(raw["revs"]) <= 1 or "f" not in raw or len(raw["f"]) < 19:
        continue

    raw_list.append([x for x in raw["f"].values()])
    raw_res.append(1 if raw["vandal"] else 0)

print(len(raw_list))

from sklearn.metrics import confusion_matrix
from sklearn import metrics

pred = frst.predict_proba(raw_list)
fpr, tpr, thresholds = metrics.roc_curve(raw_res, pred[:, 1], pos_label=1)

#pred = lc.decision_function(raw_list)
#fpr, tpr, thresholds = metrics.roc_curve(raw_res, pred, pos_label=1)

from common.plot_utils import draw_roc

draw_roc(fpr, tpr)

cm = confusion_matrix(raw_res, frst.predict(matrix(raw_list)))
print(cm)