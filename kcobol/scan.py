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

def initialize_scan(node):

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

    _cache['scans'] = {}
    _cache['scan_stack'] = []

def finalize_scan():
    _cache.clear()

def reg_scan(name, tasks, ops, hidden_task):
    scan = {'tasks': tasks, 'ops': ops, 'hidden_task': hidden_task}
    _cache['scans'][name] = scan

def has_scan(name):
    return name in _cache['scans']

def get_scans():
    return _cache['scans'].keys()

def get_scan(name):
    return _cache['scans'][name]

def del_scan(name):
    del _cache['scans'][name]

def get_tasks(name):
    return _cache['scans'][name]['tasks']

def get_hidden_task(name):
    return _cache['scans'][name]['hidden_task']

def get_ops(name):
    return _cache['scans'][name]['ops']

def push_scan(name):
    _cache['scan_stack'].append(name)

def pop_scan():
    _cache['scan_stack'].pop()

def upward_scan(node, basket):

    scan_type = _cache['scan_stack'][-1]

    if node.name == 'hidden':

        hidden_task = get_hidden_task(scan_type)
        hidden_task(node, basket)

    elif node.name == 'terminal':

        path = [node]
        node = node.uppernode

        task_attrs = {}
        task_result = {}
        for task in get_tasks(scan_type):
            task_attrs[task] = dict(basket)
            task_result[task] = None

        while node is not None:

            for task in get_tasks(scan_type):
                if task_result[task] is False:
                    continue

                rulename = task + '_' + node.name

                if rulename not in get_ops(scan_type):
                    exit(exitno=1, msg='%s rule key, "%s", is not found.'%(scan_type, rulename))

                subrules = get_ops(scan_type)[rulename]

                if path[-1].name == 'terminal':

                    if path[-1].token in _cache['skiptokens']:
                        task_result[task] = False
                    else:
                        if path[-1].token not in subrules:
                            exit(exitno=1, msg='%s subrule token, "%s / %s",'
                            ' is not found.'%(scan_type, rulename, _cache['invtokenmap'][path[-1].token]))
                        for func in subrules[path[-1].token]:
                            task_result[task] = func(node, path, task_attrs[task])
                else:

                    if path[-1].name not in subrules:
                        exit(exitno=1, msg='%s subrule name, "%s / %s", '
                        'is not found.'%(scan_type, rulename, path[-1].name))

                    for func in subrules[path[-1].name]:
                        task_result[task] = func(node, path, task_attrs[task])

            if all(result is False for result in task_result.values()):
                break
            else:
                path.append(node)
                node = node.uppernode
