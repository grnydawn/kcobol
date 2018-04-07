# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

import os
import re
import logging

from stemtree import Node
from stemcobol import parse, EOF
from .config import config
from .tree import SourceLineTree
from .application import survey_application_strace
from .util import exit

#_re_kcobol_begin = re.compile(r'\s*\*>\s+<\s*kcobol\s+(?P<command>[0-9_a-z]+)', re.I)
_re_kcobol_begin = re.compile(r'<\s*kcobol\s+(?P<command>[0-9_a-z]+)', re.I)
_re_kcobol_end = re.compile(r'/\s*kcobol\s*>', re.I)

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


def preprocess_source():
    pass

def parse_source(path, compiler):

    preprocess_source()

    # parse
    with open(path) as f:
        tree = parse(f.read(), compiler.format, compiler.standard)
        tree._shared_attrs['source_path'] = path
        return tree

def read_target():

    _parse_argument()

    survey_application_strace()

    target = config['opts/extract/target/filepath']
    compiler = config['strace/compile/source/%s'%target]

    return parse_source(target, compiler)

def collect_kernel_statements(obj, basket):

    if hasattr(obj, 'text'):

        begin_search = _re_kcobol_begin.search(obj.text)
        if begin_search:
            if obj.root.kernel_flag:
                raise Exception('Unbalanced kcobol directive: %s'%obj.text)
            obj.root.kernel_group.append([])
            obj.root.kernel_flag = True
        else:
            end_search = _re_kcobol_end.search(obj.text)
            if end_search:
                if not obj.root.kernel_flag:
                    raise Exception('Unbalanced kcobol directive: %s'%obj.text)
                obj.root.kernel_group[-1].append(obj)
                obj.root.kernel_flag = False

        logging.debug(obj.text)
        if obj.root.kernel_flag:
            obj.root.kernel_group[-1].append(obj)

def remove_eof(obj):
    return '' if obj.token == EOF else obj.text

