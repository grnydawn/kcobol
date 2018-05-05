# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

from .exception import SearchError

##################################################
#   Common searchrs
##################################################
#def _subnode_index(node, org):
#    for idx, subnode in enumerate(node.subnodes):
#        if org is subnode:
#            return idx
#    return -1
#
#def _subnode_len(node):
#    n = 0
#    for sub in node.subnodes:
#        if hasattr(sub, 'name') and sub.name != 'hidden':
#            n += 1
#    return n
#
#def _search(org, node, rpath):
#    org.searchr_path = rpath[1:] + [node]
#    node.kernel_index = org.kernel_index
#    for uppernode in node.get_uppernodes():
#        if uppernode.kernel_index < 0:
#            uppernode.kernel_index = node.kernel_index
#        elif uppernode.kernel_index != node.kernel_index:
#            raise InternalError('Kernel index mismatch: %d != %d'%(\
#                uppernode.kernel_index, node.kernel_index))
#        else:
#            break

def default_searcher(node, rpath, basket):

    org = rpath[0]
    raise SearchError(org, node)

def search_terminal(node, rpath, basket):

    org = rpath[0]
    raise SearchError(org, node)

##################################################
#  Resolvers
##################################################

def search_Sentence(node, rpath, basket):

    org = rpath[0]

    import pdb; pdb.set_trace()
#    if hasattr(org, 'text') and org.text.strip() == '.':
#        _subnode_index(node, org) == _subnode_len(node)-1:
#        _search(org, node, rpath)
#    else:
#        raise SearchError(org, node)

def search_Literal(node, rpath, basket):

    org = rpath[0]

    import pdb; pdb.set_trace()
#    if hasattr(org, 'name') and org.name == 'terminal' and \
#        _subnode_index(node, org) == 0:
#        _search(org, node, rpath)
#    else:
#        raise SearchError(org, node)

def search_DisplayStatement(node, rpath, basket):

    org = rpath[0]

    import pdb; pdb.set_trace()
#    if hasattr(org, 'text') and org.text.upper() == 'DISPLAY' and \
#        _subnode_index(node, org) == 0:
#        _search(org, node, rpath)
#    else:
#        raise SearchError(org, node)

searchers = {}
for name, obj in dict(locals()).items():
    if name.startswith('search_'):
        searchers[name[7:]] = obj
