# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

import sys
import subprocess
import logging
import click

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
    logging.basicConfig( filename="%s/kcobol.log"%outdir,
        level=logging.DEBUG, format="%(levelname)s:%(message)s")

