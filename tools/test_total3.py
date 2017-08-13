from pymongo import MongoClient, collection
from common.counter import Counter

client = MongoClient('localhost', 27017)

OK_FEATURES = {
    "t_biscore",
    "t_charscore",
    "forest_score"
}

OK_FEATURES = {
    "t_biscore",
    "t_charscore",
    "c_len",
    "c_cap",
    "c_lgt_w",
    "c_wrd_c",
    "c_numalpha",
    "c_lgt_cs",
    "t_cap",
    "t_lgt_w",
    "t_cmpr",
    "t_c_div",
    "t_numalpha",
    "t_lat",
    "t_lgt_cs",
    "t_szdiff",
    "t_w_total",
    "t_w_added",
    "t_w_deleted",
    "h_prevhrs",
    "h_hasflagged",
    "h_guest_p",
    "h_beenflagged",
    "lr_minor",
    "t_mdf_wrds",
    "t_nl_diff",
    "t_nl_wrds",
    "t_title_diff",
    "h_otheredits",
    "t_dbr_o_diff",
    "t_dbr_c_diff",
    "t_dbr_diff",
    "t_dbr_curr",
    "t_nl2_diff",
    "t_w_mixed",
    "t_rbr_o_diff",
    "t_rbr_c_diff",
    "t_rbr_diff",
    "t_rbr_curr",
    "lr_guest",
    "t_cut",
    'c_def_wrds',
    'c_wrd_avg',
    't_punct_diff',
    't_punct_words',
    't_sz_rel',
    't_cap_to_lwr',
    'h_otheredits_p',
    'lr_since_reg',
    't_main_diff',
    't_diff_rel',
    't_wikificated',
   # 'lr_hour'
}


raw_list = []
raw_res = []
cnt = Counter(100)
for raw in client.wiki['train_combiner'] .find({}):
    if "f" not in raw or len(raw["f"]) < 25:
        continue

    if any(f not in raw["f"] for f in OK_FEATURES):
        continue

    raw_list.append([x for n, x in raw["f"].items() if n in OK_FEATURES])
    raw_res.append(1 if raw["vandal"] else 0)
    cnt.tick()


from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestClassifier
from numpy import matrix
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC

frst = RandomForestClassifier(n_estimators=1500, verbose=1, min_samples_leaf = 15,  max_features=4)

#frst = GaussianNB()
#frst= MLPClassifier(solver='adam', alpha=1,hidden_layer_sizes=(8,8), random_state=12,
#                    activation="tanh",verbose=1,tol=1e-6,max_iter=300)

#frst = SVC(max_iter=200, verbose=True, kernel='linear', probability=True)
frst.fit(matrix(raw_list), raw_res)


lc = LinearSVC(verbose=1, max_iter=1000, C=0.05)
#lc.fit(matrix(raw_list), raw_res)

raw_list = []
raw_res = []
raw_sec = []
raw_chr = []

for raw in client.wiki['manual_dataset'] .find({}):
    if "rwords" not in raw or len(raw["rwords"]) == 0:
        continue

    if len(raw["revs"]) <= 1 or "f" not in raw or len(raw["f"]) < 25:
        continue

    if any(f not in raw["f"] for f in OK_FEATURES):
        continue

    raw_list.append([x for n, x in raw["f"].items() if n in OK_FEATURES])
    raw_res.append(1 if raw["vandal"] else 0)

print(len(raw_list))

from sklearn.metrics import confusion_matrix
from sklearn import metrics
import numpy as np

pred = frst.predict_proba(raw_list)#
fpr, tpr, thresholds = metrics.roc_curve(raw_res, pred[:,1], pos_label=1) #

#pred = lc.decision_function(raw_list)
#fpr, tpr, thresholds = metrics.roc_curve(raw_res, pred, pos_label=1)

from common.plot_utils import draw_roc

draw_roc(fpr, tpr)

cm = confusion_matrix(raw_res, frst.predict(matrix(raw_list)))
print(cm)