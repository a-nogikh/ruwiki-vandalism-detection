from sklearn.metrics import roc_curve, auc, average_precision_score
import matplotlib
import matplotlib.pyplot as plt
import numpy, math

def generate_upper(x : list, y : list, cnts=(2232,743)):
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

def generate_lower(x : list, y : list, cnts=(2232,743)):
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
    #plt.plot(recall,precision, color='darkorange',
    #         lw=lw)
    r2, p2 = generate_upper(recall, precision, (743, 743))
    max_auc = auc(r2, p2)
    plt.plot(*generate_upper(recall, precision, (743, 743)), color='gray', lw=lw)
    r2, p2 = generate_lower(recall, precision, (743, 743))
    min_auc = auc(r2, p2)
    plt.plot(*generate_lower(recall, precision, (743, 743)), color='gray', lw=lw)
    plt.plot(recall, precision, color='black',
             lw=lw, label='PR curve (area = %0.3f - %0.3f)' % (min_auc, max_auc))

    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.01])

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
    plt.plot([0, 1], [0, 1], color='black', lw=lw, linestyle='--')
    max_auc = auc(*generate_upper(fpr, tpr))
    plt.plot(*generate_upper(fpr, tpr), color='gray',
             lw=lw)
    min_auc = auc(*generate_lower(fpr, tpr))
    plt.plot(*generate_lower(fpr, tpr), color='gray',
             lw=lw)
    plt.plot(fpr, tpr, color='black',
             lw=lw, label='ROC curve (area = %0.3f - %.3f)' % (min_auc, max_auc))
    #plt.plot(fpr, tpr, color='darkorange',
    #         lw=lw, label='ROC curve (area = %0.3f)' % auc(fpr, tpr))


    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.01])

    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic')
    plt.legend(loc="lower right")
    plt.savefig(filename)
    plt.show()
