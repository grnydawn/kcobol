# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *
from collections import OrderedDict

#from .exception import SearchError
from .util import exit

_cache = OrderedDict()

def _debug(node, path, attrs):
    import pdb; pdb.set_trace()

def _break(node, path, attrs):
    return False

def _continue(node, path, attrs):
    return True

def initialize_search(node):

    if 'tokenmap' not in _cache:
        _cache['tokenmap'] = node.tokenmap

    if 'invtokenmap' not in _cache:
        _cache['invtokenmap'] = node.rtokenmap

    if 'skiptokens' not in _cache:
        _cache['skiptokens'] = (
            _cache['tokenmap']['DOT_FS'],
            _cache['tokenmap']['DIVISION'],
            _cache['tokenmap']['SECTION'],
            -1, # EOF
        )

    _cache['searches'] = {}
    _cache['search_stack'] = []

def finalize_search():
    _cache.clear()

def reg_search(name, tasks, ops):
    search = {'tasks': tasks, 'ops': ops}
    _cache['searches'][name] = search

def has_search(name):
    return name in _cache['searches']

def get_searches():
    return _cache['searches'].keys()

def get_search(name):
    return _cache['searches'][name]

def del_search(name):
    del _cache['searches'][name]

def get_tasks(name):
    return _cache['searches'][name]['tasks']

def get_ops(name):
    return _cache['searches'][name]['ops']

def push_search(name):
    _cache['search_stack'].append(name)

def pop_search():
    _cache['search_stack'].pop()

def search(node, basket):

    if node.name == 'hidden':
        return

    if node.name == 'terminal':

        path = [node]
        node = node.uppernode

        search_type = _cache['search_stack'][-1]

        task_attrs = {}
        task_result = {}
        for task in get_tasks(search_type):
            task_attrs[task] = dict(basket)
            task_result[task] = None

        while node is not None:

            for task in get_tasks(search_type):
                if task_result[task] is False:
                    continue

                rulename = task + '_' + node.name

                if rulename not in get_ops(search_type):
                    exit(exitno=1, msg='%s rule key, "%s", is not found.'%(search_type, rulename))

                subrules = get_ops(search_type)[rulename]

                if path[-1].name == 'terminal':

                    if path[-1].token in _cache['skiptokens']:
                        task_result[task] = False
                    else:
                        if path[-1].token not in subrules:
                            exit(exitno=1, msg='%s subrule token, "%s / %s",'
                            ' is not found.'%(search_type, rulename, _cache['invtokenmap'][path[-1].token]))
                        for func in subrules[path[-1].token]:
                            task_result[task] = func(node, path, task_attrs[task])
                else:

                    if path[-1].name not in subrules:
                        exit(exitno=1, msg='%s subrule name, "%s / %s", '
                        'is not found.'%(search_type, rulename, path[-1].name))

                    for func in subrules[path[-1].name]:
                        task_result[task] = func(node, path, task_attrs[task])

            if all(result is False for result in task_result.values()):
                break
            else:
                path.append(node)
                node = node.uppernode
