# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

import os
import re
import logging
from abc import ABCMeta, abstractmethod, abstractproperty

from .config import config
from .util import runcmd, hash_sha1, istext

# TODO: handles combining multiple options as one line -lr???
# one dash : can combine multiple options, just keep adding them
#        it seems also depends on if it requires argument or not
# two dashes : no cobining feature, search if it can find only one option
#             if multiple options found, display it
# NOTE: it may not need to analyze all compiler options
#       just collect -D and -I options or other required options
#       check if an argument is an actual path to a source file
#       and if this is related to any path required compiler

_re_cobol_src = re.compile(r'(ID|IDENTIFICATION)\s+DIVISION\s*\.', re.I)

class COBOLCompiler(object):

    __metaclass__ = ABCMeta

    @abstractproperty
    def names(self):
        pass

    # well-known options and commands
    _D = '-D'           # macro compileroption
    _I = '-I'           # include compiler option

    @abstractproperty
    def source(self):
        pass

    @classmethod
    def match(cls, name):
        if name in cls.names:
            return True
        return False

    def _getmacro(self, macro):
        splitmacro = macro.split('=')
        if len(splitmacro)==1:
           self.macros.append((splitmacro[0], '1'))
        elif len(splitmacro)==2:
            self.macros.append(tuple(splitmacro))
        else:
            raise Exception('Wrong macro definiton on compiler option.')

    def _getinc(self, inc):
        for p in inc.split(':'):
            if os.path.isabs(p):
                self.incs.append(os.path.realpath(p))
            else:
                realpath = os.path.realpath(os.path.join(self.pwd, p))
                self.incs.append(realpath)

    def _is_cobol_source(self, path):

        if not istext(path):
            return False

        with open(path) as f:
            return True if _re_cobol_src.search(f.read()) else False

    def parse_flags(self, opts):

        Cmark = False
        Imark = False
        Dmark = False

        for prev_item, item in zip(['']+opts[:-1], opts):

            if Cmark:
                Cmark = False
                continue

            if Imark:
                self._getinc(item)
                Imark = False
                continue

            if Dmark:
                self._getmacro(item)
                Dmark = False
                continue

            if item.startswith(self._I):
                if len(item)>2:
                    self._getinc(item[2:])
                else: Imark = True

            elif item.startswith(self._D):
                if len(item)>2:
                    self.macros.append(self._getmacro(item[2:]))
                else: Dmark = True

            elif not item.startswith('-'):
                if not os.path.isabs(item):
                    item = os.path.join(self.pwd, item)
                if os.path.isfile(item):
                    if any(prev_item.startswith(opt) for opt in self.filearg_opts):
                        pass
                    elif self._is_cobol_source(item):
                        self.srcs.append(item)

class GnuCOBOL(COBOLCompiler):

    names = ("cobc", )
    filearg_opts = ['-T', '-t', '-P', '-l', '-conf', '--P', '--conf']


    def __init__(self, path, pwd, flags):

        self.path = path
        self.pwd = pwd
        self.flags = []
        self.srcs = []
        self.incs = []
        self.macros = []

        if not config.has_key('fileconfig/'+hash_sha1(path)):
            self.config_compiler(path)

        self.parse_flags(flags)

    @property
    def source(self):
        if len(self.srcs) > 0:
            return self.srcs[0]

    def config_compiler(self, path):
        #import pdb; pdb.set_trace()
        pass

#    def parse_manual(self, path):
#
#        # per output line
#        for line in runcmd(self._M%path):
#            line = line.strip()
#
#            # if line starts with "-"
#            if line and line[0] == '-':
#                opts = [o.strip() for o in line.split(',')]
#
#                # per seperated items
#                for opt in opts:
#                    if not opt or opt[0] != '-':
#                        continue
#                    items = opt.split()
#
#                    # if no space inbetween
#                    if len(items) == 1:
#                        item = items[0].split('=', 1)
#                        item = item[0].split('[', 1)
#                        self.discard_opts_noarg.append(item[0])
#                    # if one space inbetween
#                    elif len(items) == 2:
#                        name = items[0]
#                        arg = items[1]
#                        if arg[0] == '[' and arg[-1] == ']':
#                            self.discard_opts_optarg.append(name)
#                        else:
#                            self.discard_opts_arg.append(name)
#                    else:
#                        item = item[0].split('[', 1)
#                        self.discard_opts_noarg.append(item[0])
#
#        # manually add options not shown in man page

def get_compiler(cmd, pwd, args):

    path, name = os.path.split(cmd)
    if name != args[0]: return

    matched = False
    for subcls in COBOLCompiler.__subclasses__():
        matched = subcls.match(name)
        if matched:
            return subcls(cmd, pwd, args[1:])
