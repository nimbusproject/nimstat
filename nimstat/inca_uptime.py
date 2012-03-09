import urllib2
from xml.dom.minidom import parseString
from datetime import datetime
from nimstat.db import ServiceAvailableDB

def getText(nodelist):
    rc = []
    for node in nodelist:
        for n in node.childNodes:
            if n.nodeType == n.TEXT_NODE:
                return n.data
    print "WHAT?"


def get_url(start_date, end_date):

    table = {}


    test_name="nimbus-clientStatus_to_"
    #test_name="nimbus-external-telnet_to_"
    u="http://inca.futuregrid.org:8080/inca/jsp/graph.jsp?printXML=true&series=%shotel,inca,inca&startDate=%s&endDate=%s" % (test_name, start_date, end_date)

    f = urllib2.urlopen(u)
    data = f.read()
    dom3 = parseString(data)

    rows = dom3.getElementsByTagName("row")

    for r in rows:
        time = r.getElementsByTagName('collected')
        res = r.getElementsByTagName('exit_status')

        val = getText(res).lower()
        if val == "success":
            tm_str = getText(time)
            ndx = tm_str.rfind(':')
            tm_str = tm_str[0:ndx]

            ndx = tm_str.rfind(':')
            tm_str = tm_str[0:ndx]
            ndx = tm_str.rfind(':')
            tm_str = tm_str[0:ndx]
            #tm = datetime.strptime(tm_str, "%Y-%m-%dT%H:%M:%S")

            # make the key
            table[tm_str] = 60

    total = 0
    for k in table:
        total = total + table[k]
    return total

def get_url_load_db(db, start_date, end_date, host, test_name="nimbus-clientStatus"):

    #test_name="nimbus-external-telnet"
    u="http://inca.futuregrid.org:8080/inca/jsp/graph.jsp?printXML=true&series=%s_to_%s,inca,inca&startDate=%s&endDate=%s" % (test_name, host, start_date, end_date)

    print "getting data from %s" % (u)
    f = urllib2.urlopen(u)
    data = f.read()
    dom3 = parseString(data)

    rows = dom3.getElementsByTagName("row")
    for r in rows:
        time = r.getElementsByTagName('collected')
        res = r.getElementsByTagName('exit_status')

        val = getText(res).lower()
        if val == "success":
            tm_str = getText(time)
            ndx = tm_str.rfind('.')
            tm_str = tm_str[0:ndx]
            tm = datetime.strptime(tm_str, "%Y-%m-%dT%H:%M:%S")

            db_obj = ServiceAvailableDB()
            db_obj.time = tm
            db_obj.test_name = test_name

            try:
                db.add_db_object(db_obj)
                db.commit()
            except Exception, ex:
                print "Failed to add object (it probably already exists: %s" % (str(ex))
                db.rollback()


def get_uptime_in_period(db, start_date, end_date, test_name="nimbus-clientStatus"):
    res = db.get_tests_in_period(start_date, end_date, test_name)

    # bucket the results into hours to avoid repeats
    buckets = {}
    for e in res:
        tm_str = e.time.strftime("%m%d%y%H")
        buckets[tm_str] = 60

    total = 0
    for k in buckets:
        total = total + buckets[k]
    return total

def get_uptime_week_buckets(db, start_date, end_date, test_name="nimbus-clientStatus"):
    res = db.get_tests_in_period(start_date, end_date, test_name)

    ntime="%W%y"
    # bucket the results into hours to avoid repeats
    buckets = {}
    for e in res:
        tm_str = e.time.strftime("%m%d%y%H-"+ntime)
        buckets[tm_str] = 60

    week_buckets = {}
    # zero allentries out
    start_week = start_date.isocalendar()[1]
    end_week = end_date.isocalendar()[1]
    y = start_date.year - 2000
    print "SDFSDFDSFDSFSDFDSF"
    print start_week
    print end_week
    for i in range(start_week, end_week):
        nk = "%02d%s" % (i, y)
        print nk
        week_buckets[nk] = 0

    for k in buckets:
        nk = k.split('-')[1]
        if nk not in week_buckets:
            week_buckets[nk] = 0
        week_buckets[nk] = week_buckets[nk] + 60

    order_list = []
    keys = sorted(week_buckets.keys())
    for k in keys:
        order_list.append(week_buckets[k])

    return order_list

def get_uptime_month_buckets(db, start_date, end_date, test_name="nimbus-clientStatus"):
    res = db.get_tests_in_period(start_date, end_date, test_name)

    # bucket the results into hours to avoid repeats
    buckets = {}
    for e in res:
        tm_str = e.time.strftime("%m%d%y%H")
        buckets[tm_str] = 60

    total = 0
    for k in buckets:
        total = total + buckets[k]
    return total

