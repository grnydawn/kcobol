# -*- coding: utf-8 -*-

"""Console script for kcobol."""
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

import os
import datetime

try:
    import configparser
except:
    import ConfigParser as configparser

import click

from .config import config

FILE_PROJECT = "project.ini"

def _write_project(prj_dir):
    if not os.path.exists(prj_dir):
        os.makedirs(prj_dir)
    cfg = os.path.join(prj_dir, FILE_PROJECT)
    parser = configparser.RawConfigParser()
    parser.optionxform = str
    if config.has_subtrie(u'prjconfig'):
        for sec in config.get_subkeys(u'prjconfig'):
            parser.add_section(sec)
            for opt, value in config.get_subitems(u'prjconfig/%s'%sec):
                parser.set(sec, opt, value)
    with click.open_file(cfg, u'w') as f:
        parser.write(f)

def _read_project(prj_dir):
    cfg = os.path.join(prj_dir, FILE_PROJECT)
    if os.path.exists(cfg):
        parser = configparser.RawConfigParser()
        parser.optionxform = str
        parser.read([cfg])
        rv = {}
        for section in parser.sections():
            for key, value in parser.items(section):
                config[u'prjconfig/%s/%s'%(section, key)] = value
    else:
        _write_project(prj_dir)


def initialize_project():

    outdir = config['opts/main/output']
    prjdir = os.path.join(outdir, ".kcobol")
    config['project/topdir'] = prjdir

    # create directories and read projects
    if not os.path.exists(outdir):
        os.makedirs(prjdir)

    if os.path.isdir(outdir):
        if os.path.exists(prjdir):
            if os.path.isdir(prjdir):
                _read_project(prjdir)
            else:
                exit(-1, "'%s' is not a directory."%outdir)
        else:
            _write_project(prjdir)
    else:
        exit(-1, "'%s' is not a directory."%outdir)

    # configuration setup
    subcmd = config['opts/main/subcommand']
    now = datetime.datetime.now()
    nowstr = now.replace(microsecond=0)

    config['%s/started_at'%subcmd] = now
    config['prjconfig/%s/last_execution_started_at'%subcmd] = nowstr

    _write_project(prjdir)
