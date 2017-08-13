import pickle, random, math
from sklearn import metrics
from sklearn.metrics import roc_curve, auc, precision_recall_curve
from sklearn.model_selection import KFold

def shuffle(first, second):
    combined = list(zip(first, second))
    random.shuffle(combined)

    a, b = zip(*combined)
    return (a,b)

def split(first, second, take):
    return ((first[:take], second[:take]), (first[take:], second[take:]))

def merge(first, second):
    return (
        (first[0][0] + second[0][0], first[0][1] + second[0][1]),
        (first[1][0] + second[1][0], first[1][1] + second[1][1])
    )

def filter_res(tuple, needed):
    res = [x for (x,y) in zip(tuple[0], tuple[1]) if y == needed]
    return (res, [needed] * len(res))


f = open('datasets.pickle', 'rb')
obj = pickle.load(f)

train_tuple = obj["train"]
test_tuple = obj["test"]

train_vandals = shuffle(*filter_res(train_tuple, 1))
train_goods = shuffle(*filter_res(train_tuple, 0))

test_vandals = shuffle(*filter_res(test_tuple, 1))
test_goods = shuffle(*filter_res(test_tuple, 0))

# TEST, TRAIN
PAIR_1 = (test_tuple, train_tuple)
PAIR_2 = merge(split(*train_vandals, 2000), split(*train_goods, 2000))
PAIR_3 = merge(split(*test_vandals, 700), split(*test_goods, 1000))


def normalize_curve(x, y):
    res_y = [0]
    pos_higher = 0
    pos_less = 0

    for i in range(1, 1000, 1):
        float_val = i / 1000

        while pos_higher + 1 < len(x) and x[pos_higher] < float_val:
            pos_higher += 1

        while pos_less + 1 < len(x) and x[pos_less + 1] < float_val:
            pos_less += 1

        curr = (x[pos_less], y[pos_less])

        y_val = curr[1] + (y[pos_higher] - curr[1]) / (x[pos_higher] - curr[0]) * (float_val - curr[0])
        res_y.append(y_val)

    res_x = [i/1000 for i in range(0,1000)]
    return (res_x, res_y)

def cnt(arr : list):
    return (arr.count(0), arr.count(1))

def generate_upper(x : list, y : list, cnts):
    new_x = x.copy()
    new_y = y.copy()

    x_interval = 1.645 / (2 * math.sqrt(cnts[0]))
    y_interval = 1.645 / (2 * math.sqrt(cnts[1]))

    for i in range(0, len(new_x)):
        # go left
        j = i - 1
        while j >= 0 and x[j] >= (x[i] - x_interval):
            new_y[j] = max(new_y[j], y[i] + y_interval)
            j -= 1

        # go right
        j = i
        while j < len(x) and x[j] <= (x[i] + x_interval):
            new_y[j] = max(new_y[j], y[i] + y_interval)
            j += 1

    for i in range(0, len(new_x)):
        new_y[i] = min(new_y[i], 1)

    return (new_x, new_y)

def generate_lower(x : list, y : list, cnts):
    new_x = x.copy()
    new_y = y.copy()

    x_interval = 1.645 / (2 * math.sqrt(cnts[0]))
    y_interval = 1.645 / (2 * math.sqrt(cnts[1]))

    for i in range(0, len(new_x)):
        # go left
        j = i - 1
        while j >= 0 and x[j] >= (x[i] - x_interval):
            new_y[j] = min(new_y[j], y[i] - y_interval)
            j -= 1

        # go right
        j = i
        while j < len(x) and x[j] <= (x[i] + x_interval):
            new_y[j] = min(new_y[j], y[i] - y_interval)
            j += 1

    for i in range(0, len(new_x)):
        new_y[i] = max(new_y[i], 0)

    return (new_x, new_y)

def auc2(fpr, tpr):
    return str(round(auc(fpr, tpr), 3))

def get_intervals(fpr, tpr, cnts):
    res = "auc=" + auc2(fpr, tpr)+";"

    nmz = normalize_curve(fpr, tpr)

    res += auc2(*generate_lower(*nmz, cnts))+"-"
    res += auc2(*generate_upper(*nmz, cnts))
    quit()
    return res

def _test_bayes(test, train):
    from sklearn.naive_bayes import GaussianNB
    from common.plot_utils import draw_roc

    g = GaussianNB()
    g.fit(train[0], train[1])
    pred = g.predict_proba(test[0])
    fpr, tpr, thresholds = metrics.roc_curve(test[1], pred[:, 1],
                                             pos_label=1)
    return get_intervals(fpr, tpr, cnt(test[1]))# auc(fpr, tpr)


def _test_bayes2(list2):
    from sklearn.naive_bayes import GaussianNB

    a,b=shuffle(*list2)
    zipped = list(zip(a,b))
    n = len(zipped)//10

    results = []
    for i in range(0, len(zipped), n):
        if abs(len(zipped) - i) < 15:
            continue

        if i + 2*n > len(zipped):
            n *= 2

        train = zipped[:i] + zipped[i+n:]
        test = zipped[i:i+n]


        train_a, train_b = zip(*train)
        test_a, test_b = zip(*test)

        g = GaussianNB()
        g.fit(train_a, train_b)
        pred = g.predict_proba(test_a)
        fpr, tpr, thresholds = metrics.roc_curve(test_b, pred[:, 1],
                                                 pos_label=1)
        results.append(auc(fpr, tpr))



    return sum(results) / 10

def _test_gb(list2, max_features, max_depth, min_samples_leaf):
    from sklearn.ensemble import GradientBoostingClassifier, AdaBoostClassifier

    a,b=shuffle(*list2)
    zipped = list(zip(a,b))
    n = len(zipped)//10

    results = []
    for i in range(0, len(zipped), n):
        if abs(len(zipped) - i) < 15:
            continue

        if i + 2*n > len(zipped):
            n *= 2

        train = zipped[:i] + zipped[i+n:]
        test = zipped[i:i+n]


        train_a, train_b = zip(*train)
        test_a, test_b = zip(*test)

        g = GradientBoostingClassifier(max_features=max_features, min_samples_leaf=min_samples_leaf, learning_rate=0.05, n_estimators=1000,
                                          max_depth=max_depth, verbose=False)
        g.fit(train_a, train_b)
        pred = g.predict_proba(test_a)
        fpr, tpr, thresholds = metrics.roc_curve(test_b, pred[:, 1],
                                                 pos_label=1)
        results.append(auc(fpr, tpr))



    return sum(results) / 10



def _test_rf(list2):
    from sklearn.ensemble import RandomForestClassifier

    a,b=shuffle(*list2)
    zipped = list(zip(a,b))
    n = len(zipped)//10

    results = []
    for i in range(0, len(zipped), n):
        if abs(len(zipped) - i) < 15:
            continue

        if i + 2*n > len(zipped):
            n *= 2

        train = zipped[:i] + zipped[i+n:]
        test = zipped[i:i+n]


        train_a, train_b = zip(*train)
        test_a, test_b = zip(*test)

        g =  RandomForestClassifier(n_estimators=1000, bootstrap =True,max_depth=25,class_weight="balanced", verbose=1,  n_jobs = 2,
                                          min_samples_leaf = 2, max_features=3) #class_weight={0:0.7,1:0.2},

        g.fit(train_a, train_b)
        pred = g.predict_proba(test_a)
        fpr, tpr, thresholds = metrics.roc_curve(test_b, pred[:, 1],
                                                 pos_label=1)
        results.append(auc(fpr, tpr))



    return sum(results) / 10


def test_bayes():
    res = {
        "bayes_1": _test_bayes(*PAIR_1),
        "bayes_2": _test_bayes(*PAIR_2),
        "bayes_3": _test_bayes2(test_tuple)
    }
    print(res)

def _test_svm(test, train, c):
    from sklearn.svm import SVC
    from sklearn.preprocessing import StandardScaler

    ss = StandardScaler()
    ss.fit(train[0])

    g = SVC(C=c,kernel='linear',verbose=1,shrinking=False, max_iter=10000)

    scaled_train = ss.transform(train[0])
    scaled_test = ss.transform(test[0])
    g.fit(scaled_train, train[1])
    pred = g.decision_function(scaled_test)
    fpr, tpr, thresholds = metrics.roc_curve(test[1], pred,
                                             pos_label=1)
    return get_intervals(fpr, tpr, cnt(test[1]))# auc(fpr, tpr)

def _test_svm_rbf(test, train, gamma, c):
    from sklearn.svm import SVC
    from sklearn.preprocessing import StandardScaler

    ss = StandardScaler()
    ss.fit(train[0])

    g = SVC(C=c,gamma=gamma,kernel='rbf',verbose=1,shrinking=False, max_iter=10000)

    scaled_train = ss.transform(train[0])
    scaled_test = ss.transform(test[0])
    g.fit(scaled_train, train[1])
    pred = g.decision_function(scaled_test)
    fpr, tpr, thresholds = metrics.roc_curve(test[1], pred,
                                             pos_label=1)
    return get_intervals(fpr, tpr, cnt(test[1]))# auc(fpr, tpr)



def test_svm():
    res = {}
    for c in [10, 100, 1000]:
        res["svm_1_c="+str(c)]= _test_svm(*PAIR_1,c)
        res["svm_2_c="+str(c)] = _test_svm(*PAIR_2,c)
    print(res)
    for a,b in res.items():
        print("{} = {}\n".format(a,b))

def test_svm_rbf():
    res = {}
    for c in [0.01, 0.1, 1, 10]:
        for gamma in [0.0001, 0.001, 0.01, 0.1, 1, 10]:
            #res["svm_1_c="+str(c)+"_g="+str(gamma)]= _test_svm_rbf(*PAIR_1,gamma, c)
            res["svm_2_c="+str(c)+"_g="+str(gamma)] = _test_svm_rbf(*PAIR_2,gamma,c)

    print(res)
    for a,b in res.items():
        print("{} = {}\n".format(a,b))


def _test_rf(test, train, max_depth, max_features, min_samples_leaf):
    from sklearn.ensemble import RandomForestClassifier


    g = RandomForestClassifier(n_estimators=1000, bootstrap = True,
                               max_depth=max_depth, class_weight="balanced", verbose=0,  n_jobs = 2,
                               min_samples_leaf = min_samples_leaf, max_features=max_features)

    g.fit(train[0], train[1])
    pred = g.predict_proba(test[0])
    fpr, tpr, thresholds = metrics.roc_curve(test[1], pred[:,1],
                                             pos_label=1)
    return get_intervals(fpr, tpr, cnt(test[1]))  # auc(fpr, tpr)

def test_rf():
    res = {}
    for md in [25]:#[5,10,15,20,25,30]:
        for mf in [2,3,4,5,6]:
            for msl in [2,5,10,20]:
                res["rf_2_mf="+str(mf)+"_msl="+str(msl)]= _test_rf(*PAIR_2,md, mf,msl)
                print(str(mf)+" "+str(msl))
            #res["rf_2_nd="+str(c)+"_g="+str(gamma)] = _test_rf(*PAIR_2,md,mf)

    print(res)
    for a,b in res.items():
        print("{} = {}\n".format(a,b))

def _test_ab(test, train, n_estimators, max_depth):
    from sklearn.ensemble import AdaBoostClassifier
    from sklearn.linear_model import Perceptron
    from sklearn.tree import DecisionTreeClassifier

    g = AdaBoostClassifier(n_estimators=n_estimators,
                           base_estimator=DecisionTreeClassifier(max_depth=max_depth,max_features=6) )

    g.fit(train[0], train[1])
    pred = g.predict_proba(test[0])
    fpr, tpr, thresholds = metrics.roc_curve(test[1], pred[:,1],
                                             pos_label=1)
    return get_intervals(fpr, tpr, cnt(test[1]))  # auc(fpr, tpr)


def test_ada():
    res = {}
    for md in [3]:#[5,10,15,20,25,30]:
         res["ada_2_md="+str(md)]= _test_ab(*PAIR_2,500,md)
         res["ada_1_md="+str(md)]= _test_ab(*PAIR_1,500,md)
         #print(str(mf)+" "+str(msl))
         #res["rf_2_nd="+str(c)+"_g="+str(gamma)] = _test_rf(*PAIR_2,md,mf)

    print(res)
    for a,b in res.items():
        print("{} = {}\n".format(a,b))




def _test_gb0(test, train, learning_rate, estimators,max_features,max_depth,fn):
    from sklearn.naive_bayes import GaussianNB
    from sklearn.ensemble import GradientBoostingClassifier, AdaBoostClassifier


    g = GradientBoostingClassifier(max_features=max_features, min_samples_leaf=2, learning_rate=learning_rate, n_estimators=estimators,
                                          max_depth=max_depth, verbose=False)
    g.fit(train[0], train[1])
    pred = g.predict_proba(test[0])
    fpr, tpr, thresholds = metrics.roc_curve(test[1], pred[:, 1],
                                             pos_label=1)
    #with open('raw/'+fn, 'wb') as f:
    #    pickle.dump({"fpr": fpr, "tpr": tpr}, f)

    return get_intervals(fpr, tpr, cnt(test[1]))


def test_gb():
    res = {}
    for lr in [0.2]:
        for est in [750]:
            for mf in [2,3,4,5,6]:
                for md in [1,2,3,4]:
                    nn ="gb_1_mf="+str(mf)+"_md="+str(md)
                    res[nn] = _test_gb0(*PAIR_1, lr, est, mf, md, nn+".png")
                    print("1")

    print(res)
    for a,b in res.items():
        print("{} = {}\n".format(a,b))


test_gb()
#test_gb()
print("He")