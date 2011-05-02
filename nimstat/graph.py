import matplotlib
matplotlib.use('Agg')

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

def make_pie(data, labels, filename, title=None, subtitle=None):
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
        pylab.suptitle("%s : Total %d" % (title, sum))
    if subtitle:
        pylab.title(subtitle, size='small')


    savefig(filename, format='png' )


def make_bar(data, labels, filename, title=None, width=0.35, xlabel=None, ylabel=None, legend=None, subtitle=None):
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

    if legend:
        ax.legend(legs, legend)
    else:
        xticks( x + 0.5,  labels, rotation=30, size='small')
    if ylabel:
        ax.set_ylabel(ylabel)
    if xlabel:
        ax.set_xlabel(xlabel)
    if subtitle:
        pylab.title(subtitle, size='small')
    if title:
        suptitle(title)

    savefig(filename, format='png' )


def make_bar_percent(data, labels, filename, total, title=None, xlabel=None, ylabel=None, legend=None, subtitle=None):
    pdata = [(d/total)*100.0 for d in data]
    data = pdata
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


    ylabels = ["", "20%", "40%", "60%", "80%", "100%"]
    
    ax.set_yticklabels(ylabels)
    ax.set_ylim(0, 100)

    if legend:
        ax.legend(legs, legend)
    else:
        xticks( x + 0.5,  labels, rotation=30, size='small')
    if ylabel:
        ax.set_ylabel(ylabel)
    if xlabel:
        ax.set_xlabel(xlabel)
    if subtitle:
        pylab.title(subtitle, size='small')
    if title:
        suptitle(title)

    savefig(filename, format='png' )

