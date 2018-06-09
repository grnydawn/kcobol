# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

"""Main module."""

import os
import click
import pygtrie
try:
    import configparser
except:
    import ConfigParser as configparser

# constants
APP_NAME = u'kcobol'
FILE_CONFIG = u'config.ini'

class StemTrie(pygtrie.StringTrie):

    def get_subkeys(self, key):
        node, trace = self._get_node(key)
        if node:
            return iter(node.children.keys())
        else:
            raise StopIteration()

    def get_subitems(self, key, with_value=False):
        split_key = key.split(self._separator)
        try:
            for subkey in self.keys(prefix=key):
                split_subkey = subkey.split(self._separator)
                yield self._separator.join(split_subkey[len(split_key):]
                    ), self[subkey]
        except:
            raise StopIteration()

    def has_key(self, key):
        try:
            node, trace = self._get_node(key)
            return True
        except KeyError:
            return False

    def __str__(self):
        lines = []
        for path, value in self.iteritems():
            lines.append(u"%s = %s"%(path, str(value)))
        return u"\n".join(lines)

# global variables
config = StemTrie()

## default configuration

# fileconfig
config[u'fileconfig/general/app_name'] = APP_NAME


## public functions

def write_config():
    app_dir = click.get_app_dir(APP_NAME)
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    cfg = os.path.join(app_dir, FILE_CONFIG)
    parser = configparser.RawConfigParser()
    parser.optionxform = str
    if config.has_subtrie(u'fileconfig'):
        for sec in config.get_subkeys(u'fileconfig'):
            parser.add_section(sec)
            for opt, value in config.get_subitems(u'fileconfig/%s'%sec):
                parser.set(sec, opt, value)
    with click.open_file(cfg, u'w') as f:
        parser.write(f)

def read_config():
    app_dir = click.get_app_dir(APP_NAME)
    cfg = os.path.join(app_dir, FILE_CONFIG)
    if os.path.exists(cfg):
        parser = configparser.RawConfigParser()
        parser.optionxform = str
        parser.read([cfg])
        rv = {}
        for section in parser.sections():
            for key, value in parser.items(section):
                config[u'fileconfig/%s/%s'%(section, key)] = value
    else:
        write_config(app_dir)


def get_source_by_program_id(pid):

    # get source path
    path = config[u"prjconfig/source/%s"%pid]

    # compiler
    compiler = config[u"prjconfig/build/compiler/%s"%path]

    return path, compiler
