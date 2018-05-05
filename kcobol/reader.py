# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

import os
import re
import logging

from stemtree import Node
from stemcobol import parse, EOF
from .config import config
from .tree import SourceLineTree
from .application import survey_application_strace
from .search import searchers, default_searcher
from .util import exit

#_re_kcobol_begin = re.compile(r'\s*\*>\s+<\s*kcobol\s+(?P<command>[0-9_a-z]+)', re.I)
_re_kcobol_begin = re.compile(r'<\s*kcobol\s+(?P<command>[0-9_a-z]+)', re.I)
_re_kcobol_end1 = re.compile(r'\*>\s(?P<attrs>.*)/\s*kcobol\s*>', re.I)
_re_kcobol_end2 = re.compile(r':(?P<attrs>.*)/\s*kcobol\s*>', re.I)

def _parse_argument():

    # parse target source argument
    items = config['opts/extract/target'].split(':')
    filepath, namepath, linespan = None, None, None

    if len(items) == 3:
        filepath, namepath, linespan = items
    elif len(items) == 2:
        if items[1][0].isdigit():
            filepath, linespan = items
        else:
            filepath, namepath = items
    elif len(items) == 1:
        filepath = items[0]
    else:
        exit(-1, msg=u"Wrong number of extraction arguments", usage=True)

    if os.path.isfile(filepath):
        config['opts/extract/target/filepath'] = filepath
    else:
        exit(-1, msg=u"'%s' is not a source file."%filepath, usage=True)

    if namepath:
        namepath = namepath.split("/")
    config['opts/extract/target/namepath'] = namepath

    if linespan:
        linespan = list(int(n) for n in linespan.split("-") )
    config['opts/extract/target/linespan'] = linespan

    if config['opts/extract/clean'] is None:
        exit(-1, msg=u"'clean' command is not found..", usage=True)

    if config['opts/extract/clean'] is None:
        exit(-1, msg=u"'build' command is not found..", usage=True)

    if config['opts/extract/clean'] is None:
        exit(-1, msg=u"'run' command is not found..", usage=True)


def preprocess_source():
    pass

def parse_source(path, compiler):

    preprocess_source()

    # parse
    tree = parse(path, compiler.format, compiler.standard)
    if tree.subnodes[0].name == 'RunUnit' and \
        tree.subnodes[0].subnodes[0].name == 'CompilationUnit':
        tree.subnodes[0].subnodes[0].source_path = path
        return tree
    else:
        return None


def read_target():

    _parse_argument()

    survey_application_strace()

    target = config['opts/extract/target/filepath']
    compiler = config['strace/compile/source/%s'%target]

    return parse_source(target, compiler)

def collect_kernel_statements(node, basket):

    if hasattr(node, 'text'):

        begin_search = _re_kcobol_begin.search(node.text)
        if begin_search:
            if node.root.kernel_flag:
                raise Exception('Unbalanced kcobol directive: %s'%node.text)
            node.root.kernel_group.append([])
            kcobol_group = [begin_search.group('command'), node.text[begin_search.end():], node]
            node.root.kcobol_group.append(kcobol_group)
            node.root.kernel_flag = True
        else:

            if node.text.find('__stemcobol__') > 0:
                end_search = _re_kcobol_end2.search(node.text)
            else:
                end_search = _re_kcobol_end1.search(node.text)
            if end_search:
                if not node.root.kernel_flag:
                    raise Exception('Unbalanced kcobol directive: %s'%node.text)
                node.root.kernel_group[-1].append(node)
                node.root.kcobol_group[-1][1] += end_search.group('attrs')
                node.root.kcobol_group[-1].append(node)
                curidx = node.uppernode.subnodes.index(node)
                for hnode in node.uppernode.subnodes[curidx+1:]:
                    if hnode.name == 'hidden':
                        node.root.kernel_group[-1].append(hnode)
                    else:
                        break
                node.root.kernel_flag = False

        if hasattr(node, 'root') and node.root.kernel_flag:
            node.kernel_index = len(node.root.kernel_group) - 1
            node.root.kernel_group[-1].append(node)

def remove_eof(node):
    return '' if node.token == EOF else node.text


## try to resolve by this node 
#def collect_resolution(node, basket):
#
#    rpath = basket['resolving_path']
#
#    if node.name in ('hidden', ) or node is rpath[0]:
#        return
#
#    return resolvers.get(node.name, default_resolver)(node, rpath, basket)
#
## move to next resolvable node
#def search_resolution(node, basket):
#
#    rpath = basket['resolving_path']
#
#    if node is rpath[0]:
#        return node.uppernode
#
#    # check if subnodes (except one that orginated) can resolve
#    nextnode = searchers.get(node.name, default_searcher)(node, rpath, basket)
#
#    # defer to uppernode
#    if not isinstance(nextnode, node.__class__):
#        return node.uppernode
#    else:
#        return nextnode
