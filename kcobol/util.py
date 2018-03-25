# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

import sys
import subprocess
import logging
import click

#logger = logging.getLogger('kcobol')

def exit(exitno=0, msg="", usage=False):

    if msg:
        prefix = u"INFO: " if exitno == 0 else u"ERROR: "
        click.echo(prefix+msg)
    if exitno < 0:
        logging.critical(msg)
    else:
        logging.info(msg)
    sys.exit(exitno)

def runcmd(cmd, cwd=None, env=None):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, cwd=cwd, env=env, shell=True)
    while(True):
      retcode = p.poll()
      line = p.stdout.readline()
      if line: yield line
      if(retcode is not None):
        break

def initialize_logging(outdir):

    # root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    shortfmt = logging.Formatter('%(levelname)s: %(message)s')
    longfmt = logging.Formatter('%(levelname)-8s [%(filename)s:%(lineno)s] %(message)s')

    fh = logging.FileHandler("%s/kcobol.log"%outdir, mode='w')
    fh.setFormatter(longfmt)
    fh.setLevel(logging.DEBUG)
    #fh.setLevel(logging.WARNING)

    ch = logging.StreamHandler()
    ch.setFormatter(shortfmt)
    ch.setLevel(logging.DEBUG)
    #ch.setLevel(logging.ERROR)

    logger.addHandler(fh)
    logger.addHandler(ch)
