#!/usr/bin/env python
from datetime import datetime
import uuid
import nimstat
from nimstat.cmdopts import bootOpts
from nimstat.db import NimStatDB
from nimstat.graph import max_pie_data, make_pie, make_bar
from nimstat.parser import *
from optparse import OptionParser
import os

__author__ = 'bresnaha'

def parse_commands(argv):
    global g_verbose

    u = """[options] <db file>"""

    version = "nimstat " + (nimstat.Version)
    parser = OptionParser(usage=u, version=version)

    opt = bootOpts("graph", "G", "Make graphs as well", True, flag=True)
    opt.add_opt(parser)
    opt = bootOpts("delim", "D", "Delimiter between csv fields", ',')
    opt.add_opt(parser)
    opt = bootOpts("verbose", "v", "Print more output", 1, count=True)
    opt.add_opt(parser)
    opt = bootOpts("quiet", "q", "Print no output", False, flag=True)
    opt.add_opt(parser)
    opt = bootOpts("load", "l", "load an accounting file into the database", None)
    opt.add_opt(parser)
    opt = bootOpts("loglevel", "L", "Controls the level of detail in the log file", "info", vals=["debug", "info", "warn", "error"])
    opt.add_opt(parser)
    opt = bootOpts("logfile", "F", "specify a log file", None)
    opt.add_opt(parser)

    opt = bootOpts("starttime", "s", "Specify the earliest time at which you want data YYYY:MM:DD:HH", None)
    opt.add_opt(parser)
    opt = bootOpts("endtime", "e", "Specify the latest time at which you want data YYYY:MM:DD:HH", None)
    opt.add_opt(parser)

    opt = bootOpts("user_charges", "u", "Request the charges on a per user basis.", False, flag=True)
    opt.add_opt(parser)
    opt = bootOpts("user_count", "U", "Request the count on a per user basis.", False, flag=True)
    opt.add_opt(parser)

    opt = bootOpts("monthly_charges", "m", "Request the charges by month.", False, flag=True)
    opt.add_opt(parser)
    opt = bootOpts("monthly_count", "M", "Request the count by month.", False, flag=True)
    opt.add_opt(parser)

    opt = bootOpts("weekly_charges", "w", "Request the charges by month.", False, flag=True)
    opt.add_opt(parser)
    opt = bootOpts("weekly_count", "W", "Request the count by month.", False, flag=True)
    opt.add_opt(parser)

    opt = bootOpts("max", "x", "The maximum number of results to show in a graph (the least significant data will be grouped as 'other').  Only applies to user based requests", None)
    opt.add_opt(parser)

    opt = bootOpts("outputdir", "o", "The output directory where the graphs and data files will be created", os.path.expanduser("~/.nimstat/%s" % (str(uuid.uuid4()).split('-')[0])))
    opt.add_opt(parser)

    (options, args) = parser.parse_args(args=argv)

    if options.starttime:
        options.starttime = datetime.strptime(options.starttime, "%Y:%m:%d:%H")
    if options.endtime:
        options.endtime = datetime.strptime(options.endtime, "%Y:%m:%d:%H")

    try:
        os.makedirs(options.outputdir)
    except Exception, ex:
        print "Warning, an error happened while trying to make %s: %s" % (options.outputdir, str(ex))

    #if not options.count and not options.charges and not options.load:
    #    print "You must select count charges or load"
    #    sys.exit(1)

    return (args, options)


def _process(opts, db, name, limit=False):

    name_for_files = name.lower().replace(" ", "_")

    if opts.starttime:
        db.set_startdate(opts.starttime)
    if opts.endtime:
        db.set_enddate(opts.endtime)

    res = db.query()
    if limit:
        res = max_pie_data(res, opts.max)

    fname = "%s/%s.csv" % (opts.outputdir, name_for_files)
    f = open(fname, "w")
    print  "Creating the results file %s" % (fname)
    for r in res:
        delim = ""
        for c in r:
            f.write(delim)
            f.write(str(c))
            delim = opts.delim
        f.write(os.linesep)
    f.close()

    if not opts.graph:
        return

    fname = "%s/%s_pie.png" % (opts.outputdir, name_for_files)
    print "creating the file %s" % (fname)
    make_pie(res, fname, title=name)
    fname = "%s/%s_bar.png" % (opts.outputdir, name_for_files)
    print "creating the file %s" % (fname)
    make_bar(res, fname, title=name)

def main(argv=sys.argv[1:]):

    (args, opts) = parse_commands(argv)
    if not args:
        print "You must provide a path to a database file (it can be a new file if loading)"
        return 1

    logger = nimstat.make_logger(opts.loglevel, args[0], logfile=opts.logfile)
    dburl = "sqlite:///%s" % (args[0])
    db = NimStatDB(dburl, log=logger)
    if opts.load:
        if not os.path.exists(opts.load):
            print "The accounting file %s does not exist." % (opts.load)
            return 1
        print "loading the DB from %s" % (opts.load)
        parse_file(opts.load, db, log=logger)
        pass

    if opts.user_charges:
        db.query_charges()
        _process(opts, db, "User Charges", limit=True)

    if opts.user_count:
        db.query_charges()
        _process(opts, db, "User Requests", limit=True)

    if opts.monthly_charges:
        db.query_montly_charges()
        _process(opts, db, "Monthly Charges")

    if opts.monthly_count:
        db.query_montly_charges()
        _process(opts, db, "Monthly Count")

    if opts.weekly_charges:
        db.query_weekly_charges()
        _process(opts, db, "Weekly Charges")

    if opts.weekly_count:
        db.query_weekly_charges()
        _process(opts, db, "Weekly Count")



    print "\nSuccess"


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)

