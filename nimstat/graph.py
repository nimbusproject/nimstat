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

def pie_format(pct):
    if pct < 3.0:
        return ""
    return "%5.1f%%" % (pct)

def make_pie(data, labels, filename, title=None):
    cla()

    sum = 0
    for d in data:
        sum = sum + d

    lbls = labels[:]
    for i in range(0, len(data)):
        pc = float(data[i]) / float(sum)
        if pc < 0.03:
            lbls[i] = ""
            
    figure(1, figsize=(6,6))
    pie(data, autopct=pie_format, labels=lbls)
    if title:
        pylab.title("%s : Total %d" % (title, sum))
    savefig(filename, format='png' )


def make_bar(data, labels, filename, title=None, width=0.35, xlabel=None, ylabel=None):
    cla()

    x = arange(len(data))
    fig = plt.figure()
    c = "bgrcmy"
    ax = fig.add_subplot(111)
    legs = []
    for i in range(0, len(data)):
        color = c[i % len(c)]
        r = ax.bar([x[i],], [data[i],], color=color)
        legs.append(r[0])
    #xticks( x + 0.5,  labels)
    ax.legend(legs, labels)
    if ylabel:
        ax.set_ylabel(ylabel)
    if xlabel:
        ax.set_xlabel(xlabel)
    if title:
        ax.set_title(title)

    savefig(filename, format='png' )


