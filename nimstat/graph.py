from pylab import *
import numpy as np
import pylab


__author__ = 'bresnaha'

# take a load of data and only return the top max members, the remainder will be returned as other
def max_pie_data(array, maxrows=None):
    a = sorted(array, key=lambda x: x[1], reverse=True)
    l = len(a)

    if not maxrows:
        return a
    maxrows = int(maxrows)
    if l < maxrows:
        return a
    other = 0
    for i in a[maxrows:]:
        other = other + i[1]
    a = a[:maxrows]
    a.append(("other", other))
    return a


def make_pie(array, filename, title=None):
    cla()
    figure(1, figsize=(6,6))
    labels = [x[0] for x in array]
    data = [x[1] for x in array]
    pie(data, labels=labels)
    if title:
        pylab.title(title)
    savefig(filename, format='png' )


def make_bar(array, filename, title=None, width=0.35, barcolor='r', xlabel=None, ylabel=None):
    cla()
    labels = [x[0] for x in array]
    data = [x[1] for x in array]
    N = len(array)
    ind = np.arange(N)  # the x locations for the groups
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.bar(ind, data, width, color=barcolor)
    if ylabel:
        ax.set_ylabel(ylabel)
    if xlabel:
        ax.set_xlabel(xlabel)
    if title:
        ax.set_title(title)
    ax.set_xticks(ind+width)
    ax.set_xticklabels(labels)
    savefig(filename, format='png' )

