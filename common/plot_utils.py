from sklearn.metrics import roc_curve, auc
import matplotlib
import matplotlib.pyplot as plt
import numpy

def draw_roc(fpr, tpr):
    plt.ion()
    matplotlib.interactive(True)
    fig = plt.figure()
    ax = fig.gca()
    ax.set_xticks(numpy.arange(0, 1, 0.1))
    ax.set_yticks(numpy.arange(0, 1., 0.1))
    plt.grid()

    lw = 2
    plt.plot(fpr, tpr, color='darkorange',
             lw=lw, label='ROC curve (area = %0.3f)' % auc(fpr, tpr))
    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])



    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic')
    plt.legend(loc="lower right")
    plt.savefig('tmp.png')
    plt.show()
