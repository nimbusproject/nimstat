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


#print get_url('020112', '030212')