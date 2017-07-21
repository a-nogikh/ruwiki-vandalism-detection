from pymongo import MongoClient, collection
from common.counter import Counter

client = MongoClient('localhost', 27017)

OK_FEATURES = {
    #"t_biscore",
    #"t_charscore",
    "c_len",
    # BAD "c_cap",
    # BAD "c_lgt_w",
    "c_wrd_c",
    # BAD "c_numalpha",
    # BAD "c_lgt_cs",
    "t_cap",
    "t_lgt_w",
    "t_cmpr",
    "t_c_div",
    "t_numalpha",
    "t_lat",

    #'t_lgt_cs',
    't_lgt_cs_rel',
    #'t_lgt_up',
    # BAD 't_lgt_up_rel',

    "t_szdiff",
    "t_w_total",
    "t_w_added",
    "t_w_deleted",
    "h_prevhrs",
    #"h_hasflagged",
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
    # BAD "t_dbr_curr",
    "t_nl2_diff",
    "t_w_mixed",
    "t_rbr_o_diff",
    "t_rbr_c_diff",
    "t_rbr_diff",
    # BAD "t_rbr_curr",
   # "lr_guest",
    #"t_cut", #  low outcomes
    'c_def_wrds',
    'c_wrd_avg',
    't_punct_diff',
    't_punct_words',
    't_sz_rel',
    't_cap_to_lwr',
    'h_otheredits_p',
    'lr_since_reg',
    't_main_diff',
    #'t_diff_rel',
    't_wikificated',
    #'lr_hour',
    'lr_usr_contr',
    'lr_usr_contr_pg',
    #'lr_wday',
    #'prn_diff',
    #'prn_rel',
    #'prn_rel_edit',
    'sb_added'
}

raw_list = []
raw_res = []
cnt = Counter(100)
for raw in client.wiki['new_big_train'] .find({}): #new_big_train,train_combiner
    if "f" not in raw or len(raw["f"]) < 25:
        continue

    if any(f not in raw["f"] for f in OK_FEATURES):
        continue

    #raw["f"].pop('t_biscore', None)
    raw_list.append([x for n, x in raw["f"].items() if n in OK_FEATURES])
    raw_res.append(1 if raw["vandal"] else 0)
    cnt.tick()


from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestClassifier
from numpy import matrix
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

big_raw_list = raw_list
big_raw_res = raw_res

#frst = GradientBoostingClassifier(n_estimators=1000, learning_rate=0.3,
#    max_depth=2, random_state=0, verbose=1,max_features = 2,loss='exponential')
#frst = GaussianNB()
lc = LinearSVC(verbose=1, max_iter=1000, C=0.05)
#lc.fit(matrix(raw_list), raw_res)

raw_list = []
raw_res = []
raw_sec = []
raw_chr = []
raw_orig = []

for raw in client.wiki['manual_dataset'] .find({}):
    if "rwords" not in raw or len(raw["rwords"]) == 0:
        continue

    if len(raw["revs"]) <= 1 or "f" not in raw or len(raw["f"]) < 25:
        continue

    if any(f not in raw["f"] for f in OK_FEATURES):
        continue

    if "t_biscore" not in raw["f"] or "t_charscore" not in raw["f"]:
        continue

    #raw["f"].pop('t_biscore', None)
    vandal_score = 0.1216 if raw["f"]["lr_guest"] else 0.10
    day_score = 1 if raw["revs"][-1]["timestamp"].weekday() <= 4 else 0.97
    raw_sec.append([raw["f"]["t_biscore"]*day_score*vandal_score])
    raw_chr.append([raw["f"]["t_charscore"]])
    raw_list.append([x for n, x in raw["f"].items() if n in OK_FEATURES])
    raw_orig.append(raw)
    raw_res.append(1 if raw["vandal"] else 0)

print(len(raw_list))

from sklearn.metrics import confusion_matrix
from sklearn import metrics
import numpy as np
from common.plot_utils import draw_roc
from features.feature import Feature

other = np.array(raw_sec)
other_char = np.array(raw_chr)

for mx_ftrs in range(3, 7):
    for smpls_leaf in [3, 7, 15, 25, 35]:
        frst = RandomForestClassifier(n_estimators=2500, verbose=1, min_samples_leaf = smpls_leaf, max_features=mx_ftrs)
        frst.fit(matrix(big_raw_list), big_raw_res)
        pred = frst.predict_proba(raw_list)

        fpr, tpr, thresholds = metrics.roc_curve(raw_res, pred[:,1]*other[:, 0], pos_label=1) #pred[:,1]*np.minimum(other[:, 0],other_char[:,0])

        draw_roc(fpr, tpr, "tests/features_"+str(mx_ftrs)+"_samples_"+str(smpls_leaf)+"_less.png")
#for k in range(0,len(raw_list)):
#    raw_orig[k]["score"] = pred[k,1] * other[k,0] * other_char[k, 0]

'''
for obj in sorted(raw_orig, key=lambda x: x["score"], reverse=False):
    if obj["vandal"] == 1:
        revs = Feature.revs(obj)
        print("https://ru.wikipedia.org/w/index.php?type=revision&diff={}&oldid={}".format(
            revs["current"]["id"], revs["prev_user"]["id"]
        ))
        print(obj)
'''
#*other_char[:,0]

#pred = lc.decision_function(raw_list)
#fpr, tpr, thresholds = metrics.roc_curve(raw_res, pred, pos_label=1)





#cm = confusion_matrix(raw_res, frst.predict(matrix(raw_list)))
#print(cm)