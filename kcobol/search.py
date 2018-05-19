# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *
from collections import OrderedDict

#from .exception import SearchError
from .util import exit

def _debug(node, path, attrs):
    import pdb; pdb.set_trace()

def _break(node, path, attrs):
    return False

def _continue(node, path, attrs):
    return True

def search(node, basket):

    if node.name == 'hidden':
        return

    if node.name == 'terminal':

        path = [node]
        node = node.uppernode

        task_attrs = {}
        task_result = {}
        for task in node.root.analysis_tasks:
            task_attrs[task] = dict(basket)
            task_result[task] = None


        while node is not None:

            for task in node.root.analysis_tasks:
                if task_result[task] is False:
                    continue
                rulename = task + '_' + node.name

                if rulename not in node.root.operators:
                    exit(exitno=1, msg='Analyzer rule key, "%s", is not found.'%rulename)

                subrules = node.root.operators[rulename]

                if path[-1].name == 'terminal':

                    if path[-1].token in node.root.skip_tokens:
                        task_result[task] = False
                    else:
                        if path[-1].token not in subrules:
                            exit(exitno=1, msg='Analyzer subrule token, "%s / %s",'
                            ' is not found.'%(rulename, node.root.revtokenmap[path[-1].token]))
                        for func in subrules[path[-1].token]:
                            task_result[task] = func(node, path, task_attrs[task])
                else:

                    if path[-1].name not in subrules:
                        exit(exitno=1, msg='Analyzer subrule name, "%s / %s", '
                        'is not found.'%(rulename, path[-1].name))

                    for func in subrules[path[-1].name]:
                        task_result[task] = func(node, path, task_attrs[task])

            if all(result is False for result in task_result.values()):
                break
            else:
                path.append(node)
                node = node.uppernode
