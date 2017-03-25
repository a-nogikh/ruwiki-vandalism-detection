from pymongo import MongoClient, collection
from sklearn.feature_extraction import FeatureHasher
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

client = MongoClient('localhost', 27017)

raw_list = []
raw_res = []
for raw in client.wiki['train_small'] .find({}):
    if "tmp" not in raw or len(raw["tmp"]) == 0:
        continue

    if len(raw["revs"]) <= 1:
        continue

    raw_list.append(raw["tmp"])
    raw_list.append({key: value * -1 for key, value in raw["tmp"].items()})
    raw_res.append(1 if raw["vandal"] else 0)
    raw_res.append(1 if not raw["vandal"] else 0)

print(len(raw_list))

fh = FeatureHasher(2000000)
matrix = fh.transform(raw_list)

lr = LogisticRegression(solver='sag', verbose=1, max_iter=200, C=0.2)
lc = LinearSVC(verbose=1, max_iter=1000, C=0.05)

lr.fit(matrix, raw_res)
#lc.fit(matrix, raw_res)

raw_list = []
raw_res = []
for raw in client.wiki['test_small'] .find({}):
    if "tmp" not in raw or len(raw["tmp"]) == 0:
        continue

    if len(raw["revs"]) <= 1:
        continue

    raw_list.append(raw["tmp"])
    raw_res.append(1 if raw["vandal"] else 0)

from sklearn.metrics import confusion_matrix
from sklearn import metrics

pred = lr.predict_proba(fh.transform(raw_list))
fpr, tpr, thresholds = metrics.roc_curve(raw_res, pred[:, 1], pos_label=1)

#pred = lc.decision_function(fh.transform(raw_list))
#fpr, tpr, thresholds = metrics.roc_curve(raw_res, pred, pos_label=1)

from common.plot_utils import draw_roc

draw_roc(fpr, tpr)

cm = confusion_matrix(raw_res, lr.predict(fh.transform(raw_list)))
print(cm)