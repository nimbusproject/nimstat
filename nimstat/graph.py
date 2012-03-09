import matplotlib
matplotlib.use('Agg')

from pylab import arange
from pylab import *
import numpy as np
import pylab



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
    fig.subplots_adjust(bottom=0.3)
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
        xticks( x + 0.5,  labels, rotation=30, size='x-small')
    if ylabel:
        ax.set_ylabel(ylabel)
    if xlabel:
        ax.set_xlabel(xlabel, verticalalignment="bottom")
    if subtitle:
        pylab.title(subtitle, size='small')
    if title:
        suptitle(title)

    savefig(filename, format='png' )


def make_bar_percent(data, labels, filename, denom, maxdenom, title=None, xlabel=None, ylabel=None, legend=None, subtitle=None):
    if len(denom) != len(data):
        print data
        print denom
        raise Exception("The numerator and demonimator have different lengths %d %d" % (len(denom), len(data)))

    pdata = []
    for i in range(0, len(data)):
        pdata.append((data[i]/denom[i]) * 100.0)
    data = pdata

    # utilization data
    udata = []
    for i in range(0, len(maxdenom)):
        udata.append((denom[i]/maxdenom[i]) * 100.0)

    cla()

    x = arange(len(data))
    fig = plt.figure()
    fig.subplots_adjust(bottom=0.3)
    c = "bgrcmy"
    ax = fig.add_subplot(111)
    legs = []
    for i in range(0, len(data)):
        color = c[i % len(c)]
        r = ax.bar([x[i],], [data[i],], color=color)
        legs.append(r[0])
    ax.plot(x + 0.5, udata, "r", label='uptime percent', linewidth=2, marker='o')

    ylabels = ["", "20%", "40%", "60%", "80%", "100%"]
    
    ax.set_yticklabels(ylabels)
    ax.set_ylim(0, 100)

    if legend:
        ax.legend(legs, legend)
    else:
        xticks( x + 0.5,  labels, rotation=30, size='x-small')
    if ylabel:
        ax.set_ylabel(ylabel)
    if xlabel:
        ax.set_xlabel(xlabel, verticalalignment="bottom", size='small')
    if subtitle:
        pylab.title(subtitle, size='small')
    if title:
        suptitle(title)

    savefig(filename, format='png' )

def make_stack_bar_percent(data, labels, filename, uptime, maxdenom, title=None, xlabel=None, ylabel=None, legend=None, subtitle=None):
    if len(uptime) != len(data):
        print uptime
        print data
        raise Exception("The numerator and demonimator have different lengths %d %d" % (len(uptime), len(data)))

    #sanitize
    print maxdenom
    print data
    print uptime
    for i in range(0, len(uptime)):
        if uptime[i] < data[i]:
            uptime[i] = data[i]
            print 'warning santizingdata at %d' % (i)
    pdata = []
    for i in range(0, len(data)):
        pdata.append((float(data[i])/float(maxdenom[i])) * 100.0)
    data = pdata

    # utilization data
    updata = []
    for i in range(0, len(maxdenom)):
        updata.append(100.0 - ((uptime[i]/float(maxdenom[i])) * 100.0))

    cla()

    x = arange(len(data))
    fig = plt.figure()
    fig.subplots_adjust(bottom=0.3)
    c = "bgrcmy"
    ax = fig.add_subplot(111)
    legs = []
    for i in range(0, len(data)):
        color = c[i % len(c)]
        r = ax.bar([x[i],], [data[i],], color=color)
        r2 = ax.bar([x[i],], [updata[i],], color="gray", bottom=[data[i],])
        legs.append(r[0])

    ylabels = ["", "20%", "40%", "60%", "80%", "100%"]

    ax.set_yticklabels(ylabels)
    ax.set_ylim(0, 100)

    if legend:
        ax.legend(legs, legend)
    else:
        xticks( x + 0.5,  labels, rotation=30, size='x-small')
    if ylabel:
        ax.set_ylabel(ylabel)
    if xlabel:
        ax.set_xlabel(xlabel, verticalalignment="bottom", size='small')
    if subtitle:
        pylab.title(subtitle, size='small')
    if title:
        suptitle(title)

    savefig(filename, format='png' )
