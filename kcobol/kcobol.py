# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

"""Main module."""

import os
import re
import logging
import click
from stemtree import DFS_LF
from .config import read_config, config
from .reader import read_target, collect_kernel_statements, remove_eof

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

    # reader
    tree = read_target()
    tree.kernel_group = []
    tree.kernel_flag = False
    basket = {}
    tree.search(collect_kernel_statements, DFS_LF, basket=basket)

    import pdb; pdb.set_trace()
    # transformers


    # writer

    outfile = os.path.basename(config['opts/extract/target'])
    outpath = os.path.join(config['opts/main/output'], outfile)

    with open(outpath, 'w') as f:
        f.write(tree.tocobol(revise=remove_eof))

    logging.debug('Leaving "on_extract_command"')
    return 0
