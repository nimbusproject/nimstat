#!/usr/bin/env python
import shlex
import sys
import logging

__author__ = 'bresnaha'

def parse_funky_line(line, event):
    line = line.strip()
    if not line:
        return None
    line = line.replace(event, "", 1)
    l_a = shlex.split(line)
    attr_dict = {}
    attr_dict['time'] = None
    attr_dict['uuid'] = None
    attr_dict['eprkey'] = None
    attr_dict['dn'] = None
    attr_dict['requestMinutes'] = None
    attr_dict['charge'] = None
    attr_dict['CPUCount'] = None
    attr_dict['memory'] = None
    attr_dict['vmm'] = None
    attr_dict['clientLaunchName'] = None
    attr_dict['network'] = None

    for l in l_a:
        l = l.strip()
        if l[-1:] == ",":
            l = l[:-1]
        (key, val) = l.split('=', 1)
        attr_dict[key] = val
    return attr_dict

def parse_created(line):
    attr = parse_funky_line(line, "CREATED:")
    return attr

def parse_removed(line):
    attr = parse_funky_line(line, "REMOVED:")
    return attr

g_parse_functions = {}
g_parse_functions["CREATED"] = parse_created
g_parse_functions["REMOVED"] = parse_removed

def parse_line(line):
    if not line:
        return

    l_a = line.split()
    if len(l_a) < 1:
        return
    global g_parse_functions
    event = l_a[0].replace(":", "").strip()
    func = g_parse_functions[event]
    attr = func(line)
    attr['type'] = event
    return attr


def parse_file(fname, db, log=logging):
    f = open(fname, "r")
    for line in f:
        attr = parse_line(line)
        if attr:
            db.add_event(attr)
            sys.stdout.write(".")
            sys.stdout.flush()
