# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

import os
import re
import logging
import subprocess
from abc import ABCMeta, abstractmethod, abstractproperty
from stemcobol import FREE_FORMAT, FIXED_FORMAT, VARIABLE_FORMAT

from .config import config
from .util import runcmd, hash_sha1, istext, re_ws, re_dotfs

# TODO: handles combining multiple options as one line -lr???
# one dash : can combine multiple options, just keep adding them
#        it seems also depends on if it requires argument or not
# two dashes : no cobining feature, search if it can find only one option
#             if multiple options found, display it

#progid_pattern = r"P{0}R{0}O{0}G{0}R{0}A{0}M{0}-{0}I{0}D{0}{1}{0}(?P<progid>[a-z0-9]+([-_]+[a-z0-9]+)*)"
#_re_cobol_progid = re.compile(progid_pattern.format(re_ws, re_dotfs), re.I)

class COBOLSource(object):

    __metaclass__ = ABCMeta

#    @abstractproperty
#    def source(self):
#        pass

#    def _getmacro(self, macro):
#        splitmacro = macro.split('=')
#        if len(splitmacro)==1:
#           self.macros.append((splitmacro[0], '1'))
#        elif len(splitmacro)==2:
#            self.macros.append(tuple(splitmacro))
#        else:
#            raise Exception('Wrong macro definiton on compiler option.')
#
#    def _getinc(self, inc):
#        for p in inc.split(':'):
#            if os.path.isabs(p):
#                self.incs.append(os.path.realpath(p))
#            else:
#                realpath = os.path.realpath(os.path.join(self.pwd, p))
#                self.incs.append(realpath)
#
#    def _is_cobol_source(self, path):
#
#        if not istext(path):
#            return False
#
#        with open(path) as f:
#            return True if _re_cobol_src.search(f.read()) else False

class GnuSource(COBOLSource):

#    filearg_opts = ['-T', '-t', '-P', '-l', '-conf']
#
#    # well-known options and commands
#    _D = '-D'           # macro compileroption
#    _I = '-I'           # include compiler option
#    _S = '-std'         # cobol standard option
#    _FREE = ('-free', '-F')
#    _FIXED = ('-fixed', )

    def __init__(self, path, compiler):

        self.path = path
        self.format = compiler.format
        self.standard = compiler.standard

    @classmethod
    def match(cls, path, compiler):
        # TODO: actually check source file
        #import pdb; pdb.set_trace()
        return True

#    @property
#    def source(self):
#        if len(self.srcs) > 0:
#            return self.srcs[0]
#
#    def normalize_flags(self, _flags):
#        # handles combined flags, equal sign, and double dashes
#        flags = []
#        for _flag in _flags:
#            if _flag.startswith('--'):
#                _flag = _flag[1:]
#            if _flag.startswith('-'):
#                flags.extend(_flag.split('=', 1))
#                # TODO: handle combined flags
#            else:
#                flags.append(_flag)
#        return flags
#
#    def parse_flags(self, opts):
#
#        Cmark = False
#        Imark = False
#        Dmark = False
#        Smark = False
#
#        for prev_item, item in zip(['']+opts[:-1], opts):
#
#            if Cmark:
#                Cmark = False
#                continue
#
#            if Imark:
#                self._getinc(item)
#                Imark = False
#                continue
#
#            if Dmark:
#                self._getmacro(item)
#                Dmark = False
#                continue
#
#            if Smark:
#                self.standard = '%s:%s'%(self.__class__.__name__, item)
#                Smark = False
#                continue
#
#            if item.startswith(self._I):
#                if len(item)>2:
#                    self._getinc(item[2:])
#                else: Imark = True
#
#            elif item.startswith(self._D):
#                if len(item)>2:
#                    self.macros.append(self._getmacro(item[2:]))
#                else: Dmark = True
#
#            elif item in self._FREE:
#                self.format = FREE_FORMAT
#
#            elif item in self._FIXED:
#                self.format = FIXED_FORMAT
#
#            elif item.startswith(self._S):
#                Smark = True
#
#            elif not item.startswith('-'):
#                if not os.path.isabs(item):
#                    item = os.path.join(self.pwd, item)
#                if os.path.isfile(item):
#                    if any(prev_item.startswith(opt) for opt in self.filearg_opts):
#                        pass
#                    elif self._is_cobol_source(item):
#                        self.srcs.append(item)

def get_source(path, compiler):

    for subcls in COBOLSource.__subclasses__():
        if subcls.match(path, compiler):
            return subcls(path, compiler)
