from dependencies import DepRepo


OK_FEATURES = {
    "t_biscore",
#"t_biscore_opp",
    #"t_charscore",
    "c_len",
    "c_cap",
    # BAD "c_lgt_w",
   # "c_wrd_c",
    "c_numalpha",
    # BAD "c_lgt_cs",
    "t_cap",
    "t_lgt_w",
   # "t_cmpr",
    "t_numalpha",
    "t_lat",

    #'t_lgt_cs',
    # BAD 't_lgt_cs_rel',
    #'t_lgt_up',
    # BAD 't_lgt_up_rel',

    "t_szdiff",
    #"t_w_total",
    "t_w_added",
    #"t_w_deleted",
    #"h_prevhrs",
    #"h_hasflagged",
    #"h_guest_p",
    #"h_beenflagged",
    "lr_minor",
    "t_mdf_wrds",
    "t_nl_diff",
  #  "t_nl_wrds",
    "t_title_diff",

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
    #"lr_guest",
    #"t_cut", #  low outcomes
    'c_def_wrds',
   # 'c_wrd_avg',
    't_punct_diff',
  ###################  't_punct_words',
    't_sz_rel',
    #'t_cap_to_lwr',
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
    'url_diff',
    'lr_guest', ###########
    'ss_added',
    'h_beencancelled',
    'lr_is_cancelling',

    't_diff_rel',
    't_lgt_cs',
     't_lgt_cs_rel',
'link_avg_new',
     "t_dbr_curr",
    'lr_usr_contr_rel',
    #'lr_since_last'
    'url_minadded',
    'url_diversity',

    "t_w_total",
    #"t_cut", #@###############
    #'h_beenflagged' ###################
}

F_EXCLUDED = [
    "t_charscore",
     "c_cap",
    "c_lgt_w",
   "c_wrd_c",
  "c_numalpha",
 "c_lgt_cs",
    "t_cmpr",
    't_lgt_up',
     't_lgt_up_rel',
    "t_c_div",
    "h_prevhrs",
    "h_guest_p",
"h_otheredits",
   "t_nl_wrds",
    "t_rbr_o_diff",
    "t_rbr_curr",
    "lr_guest",
    "t_cut", #  low outcomes
    'c_wrd_avg',
    't_cap_to_lwr',
    'lr_since_reg',
    'lr_hour',
    'lr_usr_contr',
    'lr_wday',
    'prn_diff',
    'prn_rel',
    'lr_advflag',
    'lr_is_redirect',
    'link_avg_new',
'h_beencancelled',
"t_cut",
    'lr_advflag',
    'lr_is_redirect',
    "h_hasflagged",
    "h_beenflagged",
]


F_EXCLUDED = [x for x in F_EXCLUDED if x not in OK_FEATURES]

OK_F_LIST = list(OK_FEATURES)

ind = 0
for name in sorted(OK_FEATURES):
    print("[{}] = {}".format(ind,name))
    ind += 1



HEADER_ATTRS = [
    (x, 'REAL') for x in OK_FEATURES
]

HEADER_ATTRS.append( ('vandal', ['True', 'False']))


from common.prior_calculator import PriorCalculator

priors = PriorCalculator()

raw_list = []
raw_res = []
raw_orig = []
cnt = DepRepo.counter(100)


from dependencies import DepRepo
flagsW = DepRepo.flags()

TRAIN_SET = {
    'description': 'Wiki train',
    'relation': 'wiki',
    'attributes': HEADER_ATTRS,
    'data': []
}

for raw in DepRepo.mongo_collection('new_big_train').find({}): #new_big_train,train_combiner,any_train
    if "f" not in raw or len(raw["f"]) < 25 :
        continue

    if "rwords" not in raw:# or "ignore" in raw:
        continue

    if raw["page"]["ns"] != 0 or "ignore3" in raw:
        continue

    if any(f not in raw["f"] for f in OK_FEATURES):
        continue


    #raw["f"].pop('t_biscore', None)
    tmp = []
    for f in OK_F_LIST:
        tmp.append(raw["f"][f])
 #   raw_list.append([x for n, x in raw["f"].items() if n in OK_FEATURES])
    raw_list.append(tmp)
    #tmp.append(str(raw["vandal"]))

    tmp2 = [x for x in tmp]
    tmp2.append("True" if raw["vandal"] else "False")
    TRAIN_SET['data'].append(tmp2)
   # raw_list.append(raw["f"])
    raw_res.append(1 if raw["vandal"] else 0)
    #priors.train_one(raw)
    cnt.tick()

import arff

#fo = open("new_train.arff","w")
#arff.dump(TRAIN_SET, fo)

#quit()


from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestClassifier
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
TEST_SET = {
    'description': 'Wiki test',
    'relation': 'wiki',
    'attributes': HEADER_ATTRS,
    'data': []
}

for raw in DepRepo.mongo_collection('manual_new').find({}): #manual_new,manual_dataset
    if "rwords" not in raw:# or len(raw["rwords"]) == 0:
        continue

    if len(raw["revs"]) <= 1 or "f" not in raw :
        continue

    if any(f not in raw["f"] for f in OK_FEATURES):
        continue

    if "t_biscore" not in raw["f"] or "ignore" in raw:
        continue

    #raw["f"].pop('t_biscore', None)
    vandal_score = 0.1216 if raw["f"]["lr_guest"] else 0.11
    day_score = 1 if raw["revs"][-1]["timestamp"].weekday() <= 4 else 0.97
    #raw_sec.append([day_score]) #
    #pv = priors.test(raw)
    raw_sec.append([raw["f"]["t_biscore"]])
    #raw_chr.append([raw["f"]["t_charscore"]])

    tmp = []
    for f in OK_F_LIST:
        tmp.append(raw["f"][f])
        #   raw_list.append([x for n, x in raw["f"].items() if n in OK_FEATURES])
   # raw_list.append(raw["f"])
    raw_list.append(tmp)
    #tmp.append(str(raw["vandal"]))
    TEST_SET['data'].append(tmp)
    #raw_list.append([x for n, x in raw["f"].items() if n in OK_FEATURES])
    raw_orig.append(raw)
    raw_res.append(1 if raw["vandal"] else 0)


import random
combined = list(zip(big_raw_list, big_raw_res))
random.shuffle(combined)

big_raw_list[:], big_raw_res[:] = zip(*combined)
'''
raw_list = big_raw_list[0:2000]
raw_res = big_raw_res[0:2000]
big_raw_list = big_raw_list[2000:]
big_raw_res = big_raw_res[2000:]
'''
print(len(raw_list))

from sklearn.metrics import confusion_matrix
from sklearn import metrics
import numpy as np
from common.plot_utils import draw_roc, draw_precision_recall
from features.feature import Feature
from sklearn.tree import DecisionTreeClassifier
import sklearn.tree
from sklearn.svm import LinearSVC, SVC
from sklearn.ensemble import GradientBoostingClassifier, AdaBoostClassifier
from sklearn.metrics import roc_curve, auc, precision_recall_curve
import pickle

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

    frst = RandomForestClassifier(n_estimators=1800, max_depth=30, verbose=1, n_jobs=2, min_samples_leaf=5,
                                  max_features=2, class_weight="balanced")  # class_weight={0:0.7,1:0.2},

    if len(test_big_train) < 5 or len(test_big_train) != len(big_raw_res):
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


ind = 0
for f in OK_F_LIST:

    test_big_train = []
    for raw in big_raw_list:
        tmp = raw.copy()
        del tmp[ind]
        test_big_train.append(tmp)

    frst = RandomForestClassifier(n_estimators=1000, max_depth=30, verbose=1, n_jobs=2, min_samples_leaf=5,
                                  max_features=2)  # class_weight={0:0.7,1:0.2},

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
'''
results = {}


train_tuple = (big_raw_list, big_raw_res)
test_tuple = (raw_list, raw_res)

with open('datasets.pickle', 'wb') as f:
    pickle.dump({"train": train_tuple, "test": test_tuple}, f)

quit()
for dp in [4,5]:
    for lr in [0.05,0.06]:
        for mx_ftrs in [3,4]:
            frst = GradientBoostingClassifier(max_features=mx_ftrs,min_samples_leaf =2, learning_rate =lr,n_estimators=1000,max_depth=dp,verbose=False)
            frst.fit(matrix(big_raw_list), big_raw_res)
            pred = frst.predict_proba(raw_list)
            fpr, tpr, thresholds = metrics.roc_curve(raw_res, pred[:, 1],
                                                     pos_label=1)  # pred[:,1]*np.minimum(other[:, 0],other_char[:,0])
            #with open('data.pickle', 'wb') as f:
            #    pickle.dump({"fpr": fpr, "tpr": tpr}, f)
            results["gb_" + str(mx_ftrs)+"_"+str(lr)+"_"+str(dp)] = auc(fpr, tpr)
            print("\r\n\r\n")
            for f, p in results.items():
                print("{} = {}".format(f, p))

for lr in [0.1, 0.2, 0.5, 0.7]:
    frst = AdaBoostClassifier( learning_rate =lr,n_estimators=1000)
    frst.fit(matrix(big_raw_list), big_raw_res)
    pred = frst.predict_proba(raw_list)
    fpr, tpr, thresholds = metrics.roc_curve(raw_res, pred[:, 1],
                                             pos_label=1)  # pred[:,1]*np.minimum(other[:, 0],other_char[:,0])
    results["ab_"+str(lr)] = auc(fpr, tpr)
    print("\r\n\r\n")
    for f, p in results.items():
        print("{} = {}".format(f, p))

for gamma in [1/2000,1/100,1/70,1/50,1/40,1/30,1/20,1/10,1/5]:
    frst = SVC(kernel="rbf", C=0.5, max_iter=1000, gamma=gamma, verbose=True)
    frst.fit(matrix(big_raw_list), big_raw_res)
    pred = frst.decision_function(raw_list)
    fpr, tpr, thresholds = metrics.roc_curve(raw_res, pred,
                                             pos_label=1)  # pred[:,1]*np.minimum(other[:, 0],other_char[:,0])
    results["rbf_"+str(gamma)] = auc(fpr, tpr)
    print("\r\n\r\n")
    for f, p in results.items():
        print("{} = {}".format(f, p))


for c in [0.6, 0.4, 0.7]:
    frst = LinearSVC(C=c, verbose=True)
    frst.fit(matrix(big_raw_list), big_raw_res)
    pred = frst.decision_function(raw_list)
    fpr, tpr, thresholds = metrics.roc_curve(raw_res, pred,
                                             pos_label=1)  # pred[:,1]*np.minimum(other[:, 0],other_char[:,0])
    results["lin_"+str(c)] = auc(fpr, tpr)
    print("\r\n\r\n")
    for f, p in results.items():
        print("{} = {}".format(f, p))


for mx_ftrs in [2,3,4,5]:# [2,4,5,7,9,15]:
    for smpls_leaf in [2,5]: # [3, 7, 15, 25, 35]:
        #depth = 30
        #for w in [1,2,3,4,5,6,7,8,9]:
            #weights = {0: w/10, 1:1-w/10}
        for depth in [15,25,30]:
            frst = RandomForestClassifier(n_estimators=1000, bootstrap =True,max_depth=depth,class_weight="balanced", verbose=1,  n_jobs = 2, min_samples_leaf = smpls_leaf, max_features=mx_ftrs) #class_weight={0:0.7,1:0.2},
            #frst = DecisionTreeClassifier(min_samples_leaf=40)
            frst.fit(matrix(big_raw_list), big_raw_res)
            pred = frst.predict_proba(raw_list)
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
            
            #path = frst.decision_path(raw_list)

            tmp_res = []
            rememb = []
            ress = {}
            for ciph in [0,1]:
                for edits in [0,1]:
                    for sb in [0,1]:
                        for beenf in [0,1]:
                            tmp_res = [x for x in pred[:, 1]]
                            if ciph == 1:
                                for i in range(0, len(tmp_res)):
                                    tmp_res[i] = 0.01 if raw_orig[i]["f"]["lr_usr_contr"] >= 99 else tmp_res[i]

                            if edits == 1:
                                for i in range(0, len(tmp_res)):
                                    tmp_res[i] = 0.99 if raw_orig[i]["f"]["link_worst"] == 0 else tmp_res[i]

                            if sb == 1:
                                for i in range(0, len(tmp_res)):
                                    tmp_res[i] = 0.99 if raw_orig[i]["f"]["sb_added"] > 0 else tmp_res[i]

                            if beenf == 1:
                                for i in range(0, len(tmp_res)):
                                    tmp_res[i] = 0.01 if raw_orig[i]["f"]["h_beenflagged"] > 0 else tmp_res[i]

                            fpr, tpr, thresholds = metrics.roc_curve(raw_res, tmp_res, pos_label=1)

                            if edits == 1 and sb == 1 and ciph == 0 and beenf == 0:
                                rememb = tmp_res

                            ress[str(ciph)+str(edits)+str(sb)+str(beenf)] = auc(fpr, tpr)

            #fpr, tpr, thresholds = metrics.roc_curve(raw_res, pred[:,1], pos_label=1) #pred[:,1]*np.minimum(other[:, 0],other_char[:,0])
            #results[str(mx_ftrs)+"_samples_"+str(smpls_leaf)+"_depth_"+str(depth)] = auc(fpr, tpr)
            small_str = ",".join([x+"="+str(round(y, 4)) for x,y in ress.items()])
            results["rf_"+str(mx_ftrs) + "_samples_" + str(smpls_leaf) + "_depth_" + str(depth)] = small_str
            print("\r\n\r\n")
            for f, p in results.items():
                print("{} = {}".format(f, p))
            continue
            fpr, tpr, thresholds = metrics.roc_curve(raw_res, pred[:, 1], pos_label=1) #
            draw_roc(fpr, tpr, "tests/features_"+str(mx_ftrs) + "_samples_" + str(smpls_leaf) + "_depth_" + str(depth)+"_new.png")

            recall = tpr
            cc = 0.07/0.93
            precision = [
               x*cc / (x*cc + fpr[i]*0.4) for i,x in enumerate(recall)
            ]
            #precision, recall, thr = metrics.precision_recall_curve(raw_res, pred[:,1], 1)
            draw_precision_recall(precision, recall,
                                  "tests/features_"+str(mx_ftrs) + "_samples_" + str(smpls_leaf) + "_depth_" + str(depth)+"_prc.png" )

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