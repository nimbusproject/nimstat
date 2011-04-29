#!/usr/bin/env python
from datetime import datetime
import uuid
import nimstat
from nimstat.cmdopts import bootOpts
from nimstat.db import NimStatDB
from nimstat.graph import max_pie_data, make_pie, make_bar
from nimstat.parser import *
from optparse import OptionParser, SUPPRESS_HELP
import os

__author__ = 'bresnaha'

def parse_commands(argv):
    global g_verbose

    u = """[options] <db file>"""

    version = "nimstat " + (nimstat.Version)
    parser = OptionParser(usage=u, version=version)

    opt = bootOpts("delim", "d", "Delimiter between csv fields", ',')
    opt.add_opt(parser)
    opt = bootOpts("verbose", "v", "Print more output", 1, count=True)
    opt.add_opt(parser)
    opt = bootOpts("quiet", "q", "Print no output", False, flag=True)
    opt.add_opt(parser)
    opt = bootOpts("load", "i", "load an accounting file into the database", None)
    opt.add_opt(parser)
    opt = bootOpts("loglevel", "l", "Controls the level of detail in the log file", "info", vals=["debug", "info", "warn", "error"])
    opt.add_opt(parser)
    opt = bootOpts("logfile", "F", "specify a log file", None)
    opt.add_opt(parser)

    opt = bootOpts("starttime", "s", "Specify the earliest time at which you want data YYYY:MM:DD:HH", None)
    opt.add_opt(parser)
    opt = bootOpts("endtime", "e", "Specify the latest time at which you want data YYYY:MM:DD:HH", None)
    opt.add_opt(parser)

    opt = bootOpts("remotedebug", "x", SUPPRESS_HELP, False, flag=True)
    opt.add_opt(parser)

    opt = bootOpts("max", "m", "The maximum number of results to show in a graph (the least significant data will be grouped as 'other').  Only applies to user based requests", None)
    opt.add_opt(parser)

    opt = bootOpts("outputdir", "o", "The output directory where the graphs and data files will be created", os.path.expanduser("~/.nimstat/%s" % (str(uuid.uuid4()).split('-')[0])))
    opt.add_opt(parser)

    # graph options
    opt = bootOpts("xaxis", "X", "The x axis label", None)
    opt.add_opt(parser)
    opt = bootOpts("yaxis", "Y", "The y axis label", None)
    opt.add_opt(parser)
    opt = bootOpts("title", "T", "The Title of the Graph", None)
    opt.add_opt(parser)
    opt = bootOpts("subtitle", "S", "The Subtitle of the Graph", None)
    opt.add_opt(parser)
    opt = bootOpts("xtics", "W", "Show X tic labels", False, flag=True)
    opt.add_opt(parser)
    opt = bootOpts("legend", "L", "Make a legend", False, flag=True)
    opt.add_opt(parser)
    opt = bootOpts("labellen", "Q", "Make a legend", None)
    opt.add_opt(parser)


    opt = bootOpts("column", "c", "Select the column", None,
                    vals=["user.dn",
                          "create_events.request_minutes",
                          "create_events.charge",
                          "create_events.cpu_count",
                          "create_events.memory",
                          "remove_events.charge",
                          ])
    opt.add_opt(parser)

    opt = bootOpts("function", "f", "The function to perform on the selected data set", None,
                    vals=["count",
                          "sum"
                          ])
    opt.add_opt(parser)

    opt = bootOpts("aggregator", "a", "The field to group by", None,
                    vals=["weekly",
                          "monthly",
                          "user"
                          ])
    opt.add_opt(parser)

    opt = bootOpts("graph", "G", "The type of graph to make", None,
                    vals=["pie",
                          "bar",
                          "line"
                          ])
    opt.add_opt(parser)


    (options, args) = parser.parse_args(args=argv)

    if options.remotedebug:
        try:
            from pydev import pydevd
            debug_cs = os.environ['NIMSTAT_DEBUG_CS'].split(':')
            debug_host = debug_cs[0]
            debug_port = int(debug_cs[1])
            pydevd.settrace(debug_host, port=debug_port, stdoutToServer=True, stderrToServer=True)
        except ImportError, e:
            print "Could not import remote debugging library: %s\n" % str(e)
        except KeyError:
            print "If you want to do remote debugging please set the env NIMSTAT_DEBUG_CS to the contact string of you expected debugger.\n"
        except:
            print "Please verify the format of your contact string to be <hostname>:<port>.\n"

    if not options.logfile:
        options.logfile = options.outputdir + "/" + datetime.strftime(datetime.now(), "%m-%d-%Y__%H-%M") + ".log"

    if options.starttime:
        options.starttime = datetime.strptime(options.starttime, "%Y:%m:%d:%H")
    if options.endtime:
        options.endtime = datetime.strptime(options.endtime, "%Y:%m:%d:%H")

    try:
        os.makedirs(options.outputdir)
    except Exception, ex:
        print "Warning, an error happened while trying to make %s: %s" % (options.outputdir, str(ex))

    if not options.title and options.column:
        options.title = options.column + "__" + str(datetime.now())

    #if not options.count and not options.charges and not options.load:
    #    print "You must select count charges or load"
    #    sys.exit(1)

    return (args, options)



def _writeit(opts, res, name):
    name_for_files = name.lower().replace(" ", "_")

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

def make_sql(opts):

    ag_table = {}
    ag_table['weekly'] = ("strftime('%W', create_events.time)", "strftime('%Y-%W', create_events.time)")
    ag_table['monthly'] = ("strftime('%Y-%m', create_events.time)", "strftime('%Y-%m', create_events.time)")
    ag_table['user'] = ("user.dn", "user.dn")

    if not opts.column:
        raise Exception("You need to select some column")

    if opts.function:
        columns = "%s(%s) " % (opts.function, opts.column)
    else:
        columns = "%s" % (opts.column)

    if opts.aggregator:
        ag = ag_table[opts.aggregator]
        columns = "%s, %s" % (ag[0], columns)
        group_by = "group by %s" % (ag[1])
    else:
        columns = "%s, %s" % (opts.column, columns)
        group_by = ""

    from_clause = "create_events, remove_events, user where create_events.user_id = user.id and create_events.uuid = remove_events.uuid"

    if opts.starttime:
        from_clause = "%s and create_events.time >= '%s'" % (from_clause, str(opts.starttime))
    if opts.endtime:
        from_clause = "%s and remove_events.time >= '%s'" % (from_clause, str(opts.endtime))

    select = "select %s from %s %s" % (columns, from_clause, group_by)

    return select


def main(argv=sys.argv[1:]):

    (args, opts) = parse_commands(argv)
    if not args:
        print "You must provide a path to a database file (it can be a new file if loading)"
        return 1

    logger = nimstat.make_logger(opts.loglevel, args[0], logfile=opts.logfile)
    dburl = "sqlite:///%s" % (os.path.expanduser(args[0]))
    print "using database %s" % (dburl)
    db = NimStatDB(dburl, log=logger)
    if opts.load:
        if not os.path.exists(opts.load):
            print "The accounting file %s does not exist." % (opts.load)
            return 1
        print "loading the DB from %s" % (opts.load)
        parse_file(opts.load, db, log=logger)
        pass

    if opts.column:
        select = make_sql(opts)
        logger.info("query: %s" % (select))
        res = db.raw_sql(select)
        if opts.max:
            res = max_pie_data(res, opts.max)
        logger.info("results:")
        for r in res:
            logger.info("\t%s" % (str(r)))

        _writeit(opts, res, opts.title)
        if opts.graph:
            graph_name = opts.outputdir + "/" + opts.title.lower().replace(" ", "_") + ".png"
            data = [x[1] for x in res]
            if opts.xtics:
                labels = [x[0] for x in res]
                if opts.labellen:
                    labels = [x[-int(opts.labellen):] for x in labels]
            else:
                labels = ["" for x in res]
            print "creating the graph %s" % (graph_name)
            if opts.graph == "bar":
                make_bar(data, labels, graph_name, title=opts.title, xlabel=opts.xaxis, ylabel=opts.yaxis, subtitle=opts.subtitle)
            if opts.graph == "pie":
                make_pie(data, labels, graph_name, title=opts.title, subtitle=opts.subtitle)
            if opts.graph == "line":
                pass


    print "\nSuccess"
    return 0


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)

