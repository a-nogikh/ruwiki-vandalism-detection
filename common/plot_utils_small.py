from sklearn.metrics import roc_curve, auc, average_precision_score
import matplotlib
import matplotlib.pyplot as plt
import numpy

def draw_precision_recall(precision, recall, filename):
    plt.ion()
    matplotlib.interactive(True)
    # plt.style.use('presentation')

    font = {'family': 'normal',
            # 'weight': 'bold',
            'size': 16}

    matplotlib.rc('font', **font)

    fig = plt.figure(figsize=(11, 8))
    ax = fig.gca()

    # plt.setp(ax.spines.values(), linewidth=4)

    ax.axhline(linewidth=3, color="b")  # inc. width of x-axis and color it green
    ax.axvline(linewidth=3, color="b")

    ax.tick_params(width=2)
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(3)

    ax.set_xticks(numpy.arange(0, 1, 0.1))
    ax.set_yticks(numpy.arange(0, 1., 0.1))

    # ax.tick_params('both',  width=2, which='major')
    # ax.tick_params('both',width=1, which='minor')
    plt.grid()

    lw = 3
    plt.plot(recall,precision, color='darkorange',
             lw=lw)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])

    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-recall')
    plt.legend(loc="lower right")
    plt.savefig(filename)
    plt.show()


def draw_roc(fpr, tpr, filename):
    plt.ion()
    matplotlib.interactive(True)
   # plt.style.use('presentation')

    font = {'family': 'normal',
           # 'weight': 'bold',
            'size': 16}

    matplotlib.rc('font', **font)

    fig = plt.figure(figsize=(11,8))
    ax = fig.gca()

    #plt.setp(ax.spines.values(), linewidth=4)

    ax.axhline(linewidth=3,color="b")  # inc. width of x-axis and color it green
    ax.axvline(linewidth=3,color="b")

    ax.tick_params(width=2)
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(3)


    ax.set_xticks(numpy.arange(0, 1, 0.1))
    ax.set_yticks(numpy.arange(0, 1., 0.1))

    #ax.tick_params('both',  width=2, which='major')
    #ax.tick_params('both',width=1, which='minor')
    plt.grid()

    lw = 3
    plt.plot(fpr, tpr, color='darkorange',
             lw=lw, label='ROC curve (area = %0.3f)' % auc(fpr, tpr))
    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])

    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic')
    plt.legend(loc="lower right")
    plt.savefig(filename)
    plt.show()
