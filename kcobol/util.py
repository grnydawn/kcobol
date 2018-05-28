# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

import sys
import subprocess
import logging
import hashlib
import click

try:
    from html.parser import HTMLParser
except:
    from HTMLParser import HTMLParser

from .exception import UsageError

KCOBOL_CHARSET = 'utf-8'

#logger = logging.getLogger('kcobol')

def exit(exitno=0, msg="", usage=False):

    if msg:
        prefix = u"INFO: " if exitno == 0 else u"ERROR: "
        click.echo(prefix+msg)
    if exitno < 0:
        logging.critical(msg)
    else:
        logging.info(msg)
        #import pdb; pdb.set_trace()
    sys.exit(exitno)

def runcmd_old(cmd, cwd=None, env=None):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, cwd=cwd, env=env, shell=True)
    while(True):
      retcode = p.poll()
      line = p.stdout.readline()
      if line: yield line.decode(KCOBOL_CHARSET)
      if(retcode is not None):
        break

def runcmd(cmd, cwd=None, env=None):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=cwd, env=env,
        stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
    for stdout_line in iter(popen.stdout.readline, ''):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def hash_sha1(text):
    try:
        text = text.encode(KCOBOL_CHARSET)
    except (UnicodeError, AttributeError) as e:
        pass
    return hashlib.sha1(text).hexdigest()

def istext(path):
    out = ''.join([l.strip() for l in runcmd('file '+path)])
    return out.endswith('text') or out.endswith('text, with CRLF line terminators')

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

def parse_kcobol_directive(text):

    class MyParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            self.direct = dict(attrs)

    parser = MyParser()
    parser.feed('<dummy %s >'%text)
    return parser.direct
