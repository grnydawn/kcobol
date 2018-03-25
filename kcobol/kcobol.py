# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

"""Main module."""

import logging
import click
from .config import read_config, config
from .reader import read_source

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
    tree = read_source()

    # transformers


    # writer

    #import pdb; pdb.set_trace()
    logging.debug('Leaving "on_extract_command"')
    return 0
