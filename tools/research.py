from dependencies import DepRepo
import matplotlib.pyplot as plt
import numpy
from collections import defaultdict
from common.counter import Counter


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

    # 't_lgt_cs',
    # BAD 't_lgt_cs_rel',
    # 't_lgt_up',
    # BAD 't_lgt_up_rel',

    "t_szdiff",
    # "t_w_total",
    "t_w_added",
    "t_w_deleted",
    # "h_prevhrs",
    # "h_hasflagged",
    # "h_guest_p",
    # "h_beenflagged",
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
    # "t_rbr_o_diff",
    "t_rbr_c_diff",
    "t_rbr_diff",
    # BAD "t_rbr_curr",
    # "lr_guest",
    # "t_cut", #  low outcomes
    'c_def_wrds',
    # 'c_wrd_avg',
    't_punct_diff',
    't_punct_words',
    't_sz_rel',
    't_cap_to_lwr',
    'h_otheredits_p',
    # 'lr_since_reg',
    't_main_diff',
    # 't_diff_rel',
    't_wikificated',
    # 'lr_hour',
    'lr_usr_contr',
    'lr_usr_contr_pg',
    # 'lr_wday',
    # 'prn_diff',
    # 'prn_rel',
    'prn_rel_edit',
    'sb_added',
    # 'lr_advflag'
}

OK_FEATURES={'url_diff'}


axarr = []
bins = numpy.linspace(-15, 15, 50)

def draw_hists(id, good, bad):
    #histogram = plt.figure()

    axarr[id].hist(good, bins, alpha=0.5, normed=True,color="green")
    axarr[id].hist(bad, bins, alpha=0.5, normed=True,color="red")

    #histogram.savefig(filename)


train_vandal = defaultdict(list)
train_good = defaultdict(list)
cnt = Counter(100)
mongo = DepRepo.mongo_connection()

def load_features(collection, vandal, good):
    for raw in mongo.wiki[collection].find({}):
        if "f" not in raw:
            continue

        if any(f not in raw["f"] for f in OK_FEATURES):
            continue
        for f in OK_FEATURES:
            (vandal if raw["vandal"] else good)[f].append(raw["f"][f])
        cnt.tick()

test_vandal = defaultdict(list)
test_good =  defaultdict(list)
load_features('new_big_train', train_vandal, train_good)
load_features('manual_dataset', test_vandal, test_good)

for feature in OK_FEATURES:
    f, axarr = plt.subplots(2, sharex=True, figsize=(12,6))
    mins = []
    maxs = []
    for arr in [train_good[feature], train_vandal[feature],test_good[feature],test_vandal[feature]]:
        if len(arr) == 0:
            continue

        mins.append(min(arr))
        maxs.append(max(arr))

    if len(mins) == 0:
        continue
    bins = numpy.linspace(min(mins), max(maxs), 80)

    draw_hists(0, train_good[feature], train_vandal[feature])
    draw_hists(1, test_good[feature], test_vandal[feature])

    plt.savefig("feature_stats/"+feature+".png")
    plt.close()
