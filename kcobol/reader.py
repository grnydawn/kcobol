# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

import os

from stemtree import Node
from .config import config
from .tree import SourceLineTree
from .application import survey_application_strace
from .util import exit

def _parse_argument():

    # parse target source argument
    items = config['opts/extract/target'].split(':')
    filepath, namepath, linespan = None, None, None

    if len(items) == 3:
        filepath, namepath, linespan = items
    elif len(items) == 2:
        if items[1][0].isdigit():
            filepath, linespan = items
        else:
            filepath, namepath = items
    elif len(items) == 1:
        filepath = items[0]
    else:
        exit(-1, msg=u"Wrong number of extraction arguments", usage=True)

    if os.path.isfile(filepath):
        config['opts/extract/target/filepath'] = filepath
    else:
        exit(-1, msg=u"'%s' is not a source file."%filepath, usage=True)

    if namepath:
        namepath = namepath.split("/")
    config['opts/extract/target/namepath'] = namepath

    if linespan:
        linespan = list(int(n) for n in linespan.split("-") )
    config['opts/extract/target/linespan'] = linespan

    if config['opts/extract/clean'] is None:
        exit(-1, msg=u"'clean' command is not found..", usage=True)

    if config['opts/extract/clean'] is None:
        exit(-1, msg=u"'build' command is not found..", usage=True)

    if config['opts/extract/clean'] is None:
        exit(-1, msg=u"'run' command is not found..", usage=True)


def _preprocess_source():
    pass

def _parse_source():

    _preprocess_source()

    # parse

def read_source():

    _parse_argument()

    survey_application_strace()

    _parse_source()

    #tree = SourceLineTree(config['opts/extract/target/filepath'])


