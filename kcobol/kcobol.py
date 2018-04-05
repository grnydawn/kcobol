# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

"""Main module."""

import re
import logging
import click
from stemtree import DFS_LF
from .config import read_config, config
from .reader import read_target

_re_kcobol_begin = re.compile(r'\s*\*>\s+<\s*kcobol\s+(?P<command>[0-9_a-z]+)', re.I)
_re_kcobol_end = re.compile(r'/\s*kcobol\s*>', re.I)

def collect_kernel_statements(obj, basket):

    if hasattr(obj, 'text'):

        begin_match = _re_kcobol_begin.match(obj.text)
        if begin_match:
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

def on_main_command(opts):
    logging.debug('Entering "on_main_command"')

    # save command-line options in config
    for k, v in opts.items():
        config[u'opts/main/%s'%k] = v

    # read configuration file
    read_config()

    logging.debug('Leaving "on_main_command"')
    return 0

def on_extract_command(opts):
    logging.debug('Entering "on_extract_command"')

    # save command-line options in config
    for k, v in opts.items():
        config[u'opts/extract/%s'%k] = v
    #click.echo(str(config))

    # reader
    tree = read_target()
    tree.kernel_group = []
    tree.kernel_flag = False
    basket = {}
    tree.search(collect_kernel_statements, DFS_LF, basket=basket)

    # transformers


    # writer

    import pdb; pdb.set_trace()
    logging.debug('Leaving "on_extract_command"')
    return 0
