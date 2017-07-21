import pickle
from common.plot_utils_small import draw_roc, draw_precision_recall
#from common.plot_utils import draw_roc, draw_precision_recall

with open('best_1.pickle', 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    data = pickle.load(f)
    tpr = data["tpr"]
    fpr = data["fpr"]

    draw_roc(fpr, tpr, "tests/res_1_roc.png")

    recall = tpr
    cc = 0.07 / 0.93
    precision = [
        x * cc / (x * cc + fpr[i] * 0.4) for i, x in enumerate(recall)
    ]

    precision[-1] = 0
    # precision, recall, thr = metrics.precision_recall_curve(raw_res, pred[:,1], 1)
    draw_precision_recall(precision, recall, "tests/res_1_prc.png")
    #draw_precision_recall(fpr, tpr, "tests/res_1_prc.png")
