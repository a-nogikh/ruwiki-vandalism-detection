from pymongo import MongoClient, collection
from common.counter import Counter

client = MongoClient('localhost', 27017)

OK_FEATURES = {
    "t_biscore",
    "t_charscore",
    "c_len",
    # BAD "c_cap",
    # BAD "c_lgt_w",
   # "c_wrd_c",
    # BAD "c_numalpha",
    # BAD "c_lgt_cs",
    "t_cap",
    "t_lgt_w",
    "t_cmpr",
    "t_c_div",
    "t_numalpha",
    "t_lat",

    #'t_lgt_cs',
    # BAD 't_lgt_cs_rel',
    #'t_lgt_up',
    # BAD 't_lgt_up_rel',

    "t_szdiff",
    #"t_w_total",
    "t_w_added",
    "t_w_deleted",
    #"h_prevhrs",
    #"h_hasflagged",
    #"h_guest_p",
    #"h_beenflagged",
    "lr_minor",
    "t_mdf_wrds",
    "t_nl_diff",
  #  "t_nl_wrds",
    "t_title_diff",
    "h_otheredits",
    "t_dbr_o_diff",
    "t_dbr_c_diff",
    "t_dbr_diff",
    # BAD "t_dbr_curr",
    "t_nl2_diff",
    "t_w_mixed",
    #"t_rbr_o_diff",
    "t_rbr_c_diff",
    "t_rbr_diff",
    # BAD "t_rbr_curr",
    #"lr_guest",
    #"t_cut", #  low outcomes
    'c_def_wrds',
   # 'c_wrd_avg',
    't_punct_diff',
    't_punct_words',
    't_sz_rel',
    't_cap_to_lwr',
    'h_otheredits_p',
    #'lr_since_reg',
    't_main_diff',
    #'t_diff_rel',
    't_wikificated',
    #'lr_hour',
    'lr_usr_contr',
    'lr_usr_contr_pg',
    #'lr_wday',
    #'prn_diff',
    #'prn_rel',
    'prn_rel_edit',
    'sb_added',
    #'lr_advflag',
    'url_diff'
}

F_EXCLUDED = [
    "c_cap",
    "c_lgt_w",
    "c_wrd_c",
    "c_numalpha",
    "c_lgt_cs",
    't_lgt_cs',
    't_lgt_cs_rel',
    't_lgt_up',
    't_lgt_up_rel',
    "h_prevhrs",
    "h_hasflagged",
    "h_guest_p",
    "h_beenflagged",
    "t_nl_wrds",
    "t_dbr_curr",
    "t_rbr_o_diff",
    "t_rbr_curr",
    "lr_guest",
    "t_cut",
    'lr_since_reg',
    't_diff_rel',
    'lr_hour',
    'lr_wday',
   # 'prn_diff',
    #'prn_rel',
   # 'prn_rel_edit',
    'lr_advflag',
    'url_diff'
]

OK_F_LIST = list(OK_FEATURES)

ind = 0
for name in OK_FEATURES:
    print("[{}] = {}".format(ind,name))
    ind += 1


from common.prior_calculator import PriorCalculator

priors = PriorCalculator()

raw_list = []
raw_res = []
raw_orig = []
cnt = Counter(100)


from dependencies import DepRepo
flagsW = DepRepo.flags()

for raw in client.wiki['new_big_train'] .find({}): #new_big_train,train_combiner,any_train
    if "f" not in raw or len(raw["f"]) < 25:
        continue

    if "rwords" not in raw:
        continue

    if raw["page"]["ns"] != 0:
        continue

    if any(f not in raw["f"] for f in OK_FEATURES):
        continue


    #raw["f"].pop('t_biscore', None)
    tmp = []
    for f in OK_F_LIST:
        tmp.append(raw["f"][f])
 #   raw_list.append([x for n, x in raw["f"].items() if n in OK_FEATURES])
    raw_list.append(tmp)
    raw_res.append(1 if raw["vandal"] else 0)
    #priors.train_one(raw)
    cnt.tick()


from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from numpy import matrix
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

big_raw_list = raw_list
big_raw_res = raw_res
big_raw_orig = raw_orig


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
    vandal_score = 0.1216 if raw["f"]["lr_guest"] else 0.11
    day_score = 1 if raw["revs"][-1]["timestamp"].weekday() <= 4 else 0.97
    raw_sec.append([day_score]) #
    #pv = priors.test(raw)
    #raw_sec.append([raw["f"]["t_biscore"]*pv])
    raw_chr.append([raw["f"]["t_charscore"]])

    tmp = []
    for f in OK_F_LIST:
        tmp.append(raw["f"][f])
        #   raw_list.append([x for n, x in raw["f"].items() if n in OK_FEATURES])
    raw_list.append(tmp)
    #raw_list.append([x for n, x in raw["f"].items() if n in OK_FEATURES])
    raw_orig.append(raw)
    raw_res.append(1 if raw["vandal"] else 0)

print(len(raw_list))

from sklearn.metrics import confusion_matrix
from sklearn import metrics
import numpy as np
from common.plot_utils import draw_roc
from features.feature import Feature
from sklearn.tree import DecisionTreeClassifier
import sklearn.tree
from sklearn.metrics import roc_curve, auc

other = np.array(raw_sec)
other_char = np.array(raw_chr)
frts = dict()

'''
ind = 0
for f in F_EXCLUDED:

    test_big_train = []
    for raw in big_raw_list:
        if f not in raw:
            continue
        tmp = []
        for ff in OK_F_LIST:
            tmp.append(raw[ff])
        tmp.append(raw[f])
        #del tmp[ind]
        test_big_train.append(tmp)

    frst = RandomForestClassifier(n_estimators=2500, max_depth=20, verbose=1, n_jobs=2, min_samples_leaf=5,
                                  max_features=3)  # class_weight={0:0.7,1:0.2},

    if len(test_big_train) < 5:
        continue

    frst.fit(matrix(test_big_train), big_raw_res)
    del test_big_train

    test_raw_list = []
    for raw in raw_list:
        if f not in raw:
            continue
        tmp = []
        for ff in OK_F_LIST:
            tmp.append(raw[ff])
        tmp.append(raw[f])
        test_raw_list.append(tmp)

    if len(test_raw_list) < 5:
        continue

    pred = frst.predict_proba(test_raw_list)
    fpr, tpr, thresholds = metrics.roc_curve(raw_res, pred[:, 1],
                                                 pos_label=1)  # *other[:, 0]pred[:,1]*np.minimum(other[:, 0],other_char[:,0])

    del test_raw_list
    frts[f] = auc(fpr, tpr)
    print("{} = {} |||||".format(f, frts[f]))

    for f, p in frts.items():
        print("{} = {}".format(f, p))

    ind += 1


for f,p in frts.items():
    print("{} = {}".format(f,p))
sys.exit(0)

'''

ind = 0
for f in OK_F_LIST:

    test_big_train = []
    for raw in big_raw_list:
        tmp = raw.copy()
        del tmp[ind]
        test_big_train.append(tmp)

    frst = RandomForestClassifier(n_estimators=2500, max_depth=20, verbose=1, n_jobs=2, min_samples_leaf=5,
                                  max_features=3)  # class_weight={0:0.7,1:0.2},

    frst.fit(matrix(test_big_train), big_raw_res)
    del test_big_train

    test_raw_list = []
    for raw in raw_list:
        tmp = raw.copy()
        del tmp[ind]
        test_raw_list.append(tmp)

    pred = frst.predict_proba(test_raw_list)
    fpr, tpr, thresholds = metrics.roc_curve(raw_res, pred[:, 1],
                                                 pos_label=1)  # *other[:, 0]pred[:,1]*np.minimum(other[:, 0],other_char[:,0])

    del test_raw_list
    frts[f] = auc(fpr, tpr)
    print("{} = {} |||||".format(f, frts[f]))

    for f, p in frts.items():
        print("{} = {}".format(f, p))

    ind += 1


for f,p in frts.items():
    print("{} = {}".format(f,p))

sys.exit(0)


for mx_ftrs in [3]:# [2,4,5,7,9,15]:
    for smpls_leaf in [10]: # [3, 7, 15, 25, 35]:
        frst = RandomForestClassifier(n_estimators=2500, max_depth=15, verbose=1,  n_jobs = 2, min_samples_leaf = smpls_leaf, max_features=mx_ftrs) #class_weight={0:0.7,1:0.2},
        #frst = DecisionTreeClassifier(min_samples_leaf=40)
        frst.fit(matrix(big_raw_list), big_raw_res)
        '''
        with open('dots/complete_new.dot', 'w') as my_file:
            my_file = sklearn.tree.export_graphviz(frst, out_file=my_file)

       
        i_tree = 0

        for tree_in_forest in frst.estimators_:  # type: DecisionTreeClassifier
            with open('dots/tree_' + str(i_tree) + '.dot', 'w') as my_file:
                my_file = sklearn.tree.export_graphviz(tree_in_forest, out_file=my_file)
            i_tree = i_tree + 1
            if i_tree > 10:
                break
 '''
        pred = frst.predict_proba(raw_list)
        #path = frst.decision_path(raw_list)

        fpr, tpr, thresholds = metrics.roc_curve(raw_res, pred[:,1], pos_label=1) #pred[:,1]*np.minimum(other[:, 0],other_char[:,0])

        draw_roc(fpr, tpr, "tests/features_"+str(mx_ftrs)+"_samples_"+str(smpls_leaf)+"_new.png")
    break
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