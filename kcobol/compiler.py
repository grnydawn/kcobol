# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

import os
import logging
from abc import ABCMeta, abstractmethod, abstractproperty

class COBOLCompiler(object):

    __metaclass__ = ABCMeta

    @abstractproperty
    def names(self):
        pass

    @abstractproperty
    def _D(self):
        pass

    @abstractproperty
    def _I(self):
        pass

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
           return (splitmacro[0], '')
        elif len(splitmacro)==2:
            return tuple(splitmacro)
        else:
            raise

    def parse_flags(self, opts):

        Cmark = False
        Imark = False
        Dmark = False

        for item in opts:

            if Cmark:
                Cmark = False
                continue

            if Imark:
                for p in item.split(':'):
                    if p[0]=='/':
                        self.incs.append(p)
                    else:
                        self.incs.append(os.path.realpath('%s/%s'%(self.pwd,p)))
                Imark = False
                continue

            if Dmark:
                self.macros.append(self._getmacro(item))
                Dmark = False
                continue

            if item.startswith(self._I):
                if len(item)>2:
                    for p in item[2:].split(':'):
                        if p[0]=='/':
                            self.incs.append(p)
                        else:
                            self.incs.append(os.path.realpath('%s/%s'%(self.pwd,p)))
                else: Imark = True

            elif item.startswith(self._D):
                if len(item)>2:
                    self.macros.append(self._getmacro(item[2:]))
                else: Dmark = True

            elif item.startswith('-'):
                if item in self.discard_opts_noarg:
                    pass
                elif any( item.startswith(f) for f in self.discard_opts_arg ):
                    for f in self.discard_opts_arg:
                        if item==f:
                            if len(item)==len(f):
                                Cmark = True
                            break
                else:
                    self.flags.append(item)

            elif self.file_exts and item.split('.')[-1] in self.file_exts:
                if item[0]=='/':
                    self.srcs.append(item)
                else:
                    self.srcs.append(os.path.realpath('%s/%s'%(self.pwd,item)))
            else:
                self.flags.append(item)


class GnuCOBOL(COBOLCompiler):

    names = ("cobc", )
    _D = "-D"
    _I = "-I"
    file_exts = ['cob']
    discard_opts_noarg = []
    discard_opts_arg = []

    def __init__(self, path, pwd, flags):

        self.path = path
        self.pwd = pwd
        self.flags = []
        self.srcs = []
        self.incs = []
        self.macros = []

        self.parse_flags(flags)

    @property
    def source(self):
        if len(self.srcs) > 0:
            return self.srcs[0]

def get_compiler(cmd, pwd, args):
    try:
        path, name = os.path.split(cmd)

        assert name == args[0]

        matched = False
        for subcls in COBOLCompiler.__subclasses__():
            matched = subcls.match(name)
            if matched:
                return subcls(cmd, pwd, args[1:])
    except:
        return None
