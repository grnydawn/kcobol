# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

"""Main module."""

import logging
import click
from .config import read_config, config
from .reader import read_source

logger = logging.getLogger('kcobol')

def on_main_command(opts):

    # save command-line options in config
    for k, v in opts.items():
        config[u'opts/main/%s'%k] = v

    # read configuration file
    read_config()

    return 0

def on_extract_command(opts):

    # save command-line options in config
    for k, v in opts.items():
        config[u'opts/extract/%s'%k] = v
    #click.echo(str(config))

    # reader
    tree = read_source()

    # transformers


    # writer

    #import pdb; pdb.set_trace()
    return 0
