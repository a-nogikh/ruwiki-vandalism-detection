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
for raw in client.wiki['new_train'] .find({}):
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

raw_list = []
raw_res = []
for raw in client.wiki['manual_dataset'] .find({}):
    if len(raw["revs"]) <= 1:
        continue
    revs = Feature.revs(raw)
    if revs["prev_user"] is None:
        continue

    distr = calculate(revs)

    raw_list.append(distr)
    #raw_list.append(raw["tmp"])
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