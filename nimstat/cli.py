#!/usr/bin/env python
import nimstat
from nimstat.cmdopts import bootOpts
from nimstat.db import NimStatDB
from nimstat.parser import *
from optparse import OptionParser


__author__ = 'bresnaha'

def parse_commands(argv):
    global g_verbose

    u = """[options] <db file>"""

    version = "nimstat " + (nimstat.Version)
    parser = OptionParser(usage=u, version=version)

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

    (options, args) = parser.parse_args(args=argv)

    return (args, options)

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
        parse_file(sys.argv[1], db, log=logger)


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)

