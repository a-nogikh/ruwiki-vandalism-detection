from pymongo import MongoClient
from sklearn.feature_extraction import FeatureHasher
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

from dependencies import DepRepo
from common.utils import get_url

from difflib import SequenceMatcher
from common.utils import query_yes_no
from features.feature import Feature

collection = DepRepo.mongo_collection('new_big_train')  # type: collection.Collection
flags2 = DepRepo.flags()

TRUSTED_GROUPS = ['editor', 'autoeditor', 'rollbacker', 'reviewer', 'sysop', 'bureaucrat']
users = 0
total=0
for item in collection.find({"f.link_avg_new":0,"vandal":True}, no_cursor_timeout=True):
    if len(item["revs"]) < 2:
        continue

    revs = Feature.revs(item)
    print(get_url(revs))


import pymorphy2

morph = pymorphy2.MorphAnalyzer()

test = morph.parse('')

print("http://google.com")
sys.exit(0)

client = MongoClient('localhost', 27017)

raw_list = []
raw_res = []
for raw in client.wiki['new_train'] .find({}):
    if "bigram_stemmed" not in raw or len(raw["bigram_stemmed"]) == 0:
        continue

    if len(raw["revs"]) <= 1:
        continue

    filtered = {x:y for x,y in raw["bigram_stemmed"].items() if y > 0 and not x.isdigit()}
    raw_list.append(filtered)
    #raw_list.append({key: value * -1 for key, value in raw["tmp"].items()})
    raw_res.append(1 if raw["vandal"] else 0)
    #raw_res.append(1 if not raw["vandal"] else 0)

print(len(raw_list))

fh = FeatureHasher(2000000)
matrix = fh.transform(raw_list)

lr = LogisticRegression(solver='sag', verbose=1, max_iter=200, C=0.2)
lc = LinearSVC(verbose=1, max_iter=1000, C=0.05)

lr.fit(matrix, raw_res)
#lc.fit(matrix, raw_res)

raw_list = []
raw_res = []
for raw in client.wiki['manual_dataset'] .find({}):
    if "bigram_stemmed" not in raw or len(raw["bigram_stemmed"]) == 0:
        continue

    if len(raw["revs"]) <= 1:
        continue

    filtered = {x: y for x, y in raw["bigram_stemmed"].items() if y > 0 and not x.isdigit()}
    raw_list.append(filtered)
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