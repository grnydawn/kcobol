# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *
from collections import OrderedDict

from stemtree import DFS_LF
from .search import search, _debug, _break, _continue
from .collect import pre_collect, post_collect
from .exception import ResolveError
from .util import exit

resolve_tasks = (
    'resolve',
)

def _collect_name(node, path, attrs):
    if 'name' in attrs:
        exit(exitno=1, msg='_collect_name: "name" key already exists.')
    attrs['name'] = path[0]

def _resolve_name(node, path, attrs):
    if 'name' not in attrs:
        exit(exitno=1, msg='_resolve_name at "%s": "name" key does not exists.'%node.name)
    name_node = attrs['name']
    res_node = None
    if name_node.text in node.program_node.namespace:
        res_node = node.program_node.namespace[name_node.text]
    elif name_node.text in node.rununit_node.namespace:
        res_node = node.rununit_node.namespace[name_node.text]
    else:
        node.rununit_node.unresolved.add(name_node)

    if res_node is not None:
        attrs['nodes'].add(res_node)
        res_node.search(search, DFS_LF, basket=attrs, premove=pre_collect,
            postmove=post_collect)

_operators = {

#    #### IdentificationDivision ####
#
#    'resolve_IdentificationDivision': {
#        'IDENTIFICATION': [_break],
#    },
#
#    'resolve_ProgramIdParagraph': {
#        'PROGRAM_ID': [_break],
#        'ProgramName': [_add_name, _break],
#    },
#
#    'resolve_ProgramName': {
#        'CobolWord': [_collect_name, _continue],
#    },
#
#    #### DataDivision ####
#
#    'resolve_DataDivision': {
#        'DATA': [_break],
#    },
#
#    'resolve_WorkingStorageSection': {
#        'WORKING_STORAGE': [_break],
#    },
#
#    'resolve_DataDescriptionEntryFormat1': {
#        'INTEGERLITERAL': [_break],
#        'DataName': [_add_name, _break],
#    },
#
    'resolve_DataName': {
        'CobolWord': [_collect_name, _continue],
    },
#
#    'resolve_DataPictureClause': {
#        'PIC': [_break],
#    },
#
#    'resolve_DataValueClause': {
#        'VALUE': [_break],
#    },
#
#    'resolve_PictureChars': {
#        'IDENTIFIER': [_break],
#        'LPARENCHAR': [_break],
#        'RPARENCHAR': [_break],
#    },
#
#    #### ProcedureDivision ####
#
#    'resolve_ProcedureDivision': {
#        'PROCEDURE': [_break],
#    },
#
#    'resolve_Paragraph': {
#        'ParagraphName': [_add_name, _break],
#    },
#

    'resolve_PerformStatement': {
        'PERFORM': [_break],
    },

    'resolve_PerformProcedureStatement': {
        'ProcedureName': [_resolve_name,_break],
    },

    'resolve_DisplayStatement': {
        'DISPLAY': [_break],
    },

    'resolve_MoveStatement': {
        'MOVE': [_break],
    },

    'resolve_MoveToStatement': {
        'TO': [_break],
    },

#    'resolve_GobackStatement': {
#        'GOBACK': [_break],
#    },
#
    'resolve_PerformInlineStatement': {
        'END_PERFORM': [_break],
    },
#
#    'resolve_DisplayOperand': {
#
#        'Identifier': [_break],
#    },
#
#    'resolve_QualifiedDataName': {
#        'QualifiedDataNameFormat1': [_continue],
#    },
#
    'resolve_QualifiedDataNameFormat1': {
        'DataName': [_resolve_name, _break]
    },

    'resolve_PerformVaryingClause': {
        'VARYING': [_break],
    },
#
#    'resolve_PerformVaryingPhrase': {
#        'Identifier': [_break],
#    },
#
    'resolve_PerformFrom': {
        'FROM': [_break],
    },

    'resolve_PerformBy': {
        'BY': [_break],
    },

    'resolve_PerformUntil': {
        'UNTIL': [_break],
    },

    'resolve_ParagraphName': {
        'CobolWord': [_collect_name, _continue],
    },

#    #### Common ####
#
    'resolve_RunUnit': {
        'ProgramUnit': _debug,
    },
#
#    'resolve_Sentence': {
#    },
#

    'resolve_ProcedureName': {
        'ParagraphName': [_continue],
    },

    'resolve_RelationalOperator': {
        'MORETHANCHAR': [_break],
    },

#    'resolve_Basis': {
#        'Identifier': [_break],
#    },
#
#    'resolve_Identifier': {
#        'QualifiedDataName': [_continue],
#        'TableCall': [_continue],
#    },
#
#    'resolve_TableCall': {
#        'QualifiedDataName': [_continue],
#    },
#
    'resolve_ReferenceModifier': {
        'LPARENCHAR': [_break],
        'RPARENCHAR': [_break],
        'COLONCHAR': [_break],
    },

    'resolve_Literal': {
        'NONNUMERICLITERAL': [_break],
    },

    'resolve_IntegerLiteral': {
        'INTEGERLITERAL': [_break],
    },

    'resolve_CobolWord': {
        'IDENTIFIER': [_continue],
    },
}

#def pre_resolve(node, basket):
#
#    tokenmap = node.tokenmap
#
#    node.root.revtokenmap = node.rtokenmap
#
#    node.root.skip_tokens = (
#        tokenmap['DOT_FS'],
#        tokenmap['DIVISION'],
#        tokenmap['SECTION'],
#        -1, # EOF
#    )
#
#    ops = {}
#    node.root.operators = ops
#    for rulename, subrules in _operators.items():
#        subops = {}
#        ops[rulename] = subops
#        for sname, op in subrules.items():
#            if sname.isupper():
#                subops[tokenmap[sname]]= op
#            else:
#                subops[sname]= op
#
#    basket['entry_node'] = node
#
#    return node


def pre_resolve(node, basket):

    tokenmap = node.tokenmap

    node.root.revtokenmap = node.rtokenmap

    node.root.skip_tokens = (
        tokenmap['DOT_FS'],
        tokenmap['DIVISION'],
        tokenmap['SECTION'],
        -1, # EOF
    )

    ops = {}
    node.root.operators = ops
    for pname, snodes in _operators.items():
        subops = {}
        ops[pname] = subops

        for sname, op in snodes.items():

            for task in resolve_tasks:
                analyzer_name = "%s_%s_%s"%(task, pname, sname)
                if analyzer_name in globals():
                    op.insert(0, globals()[analyzer_name])

            if sname.isupper():
                subops[tokenmap[sname]]= op
            else:
                subops[sname]= op

    node.root.analysis_tasks = resolve_tasks

    basket['entry_node'] = node

    return node

def post_resolve(node, basket):
    entry_node = basket['entry_node']
    del entry_node.root.skip_tokens
    del entry_node.root.analysis_tasks
    del entry_node.root.operators
    del entry_node.root.revtokenmap
    return node

#def post_resolve(node, basket):
#    entry_node = basket['entry_node']
#    del entry_node.root.skip_tokens
#    del entry_node.root.operators
#    del entry_node.root.revtokenmap
#    return node

#
#def resolve(node, basket):
#
#    if node.name == 'hidden':
#        return
#
#    if node.name == 'terminal':
#
#        path = [node]
#        node = node.uppernode
#
#        task_attrs = {}
#        task_result = {}
#        for task in resolve_tasks:
#            task_attrs[task] = {'nodes': set()}
#            task_result[task] = None
#
#
#        while node is not None:
#
#            for task in resolve_tasks:
#                if task_result[task] is False:
#                    continue
#
#                rulename = task + '_' + node.name
#
#                if rulename not in node.root.operators:
#                    exit(exitno=1, msg='Resolver rule key, "%s", is not found.'%rulename)
#
#                subrules = node.root.operators[rulename]
#
#                if path[-1].name == 'terminal':
#
#                    if path[-1].token in node.root.skip_tokens:
#                        task_result[task] = False
#                    else:
#                        if path[-1].token not in subrules:
#                            exit(exitno=1, msg='Resolver subrule token, "%s / %s",'
#                            ' is not found.'%(rulename, node.root.revtokenmap[path[-1].token]))
#                        try:
#                            for func in subrules[path[-1].token]:
#                                task_result[task] = func(node, path, task_attrs[task])
#                        except TypeError:
#                            task_result[task] = subrules[path[-1].token](node, path, task_attrs[task])
#
#                else:
#
#                    if path[-1].name not in subrules:
#                        exit(exitno=1, msg='Resolver subrule name, "%s / %s", '
#                        'is not found.'%(rulename, path[-1].name))
#
#                    try:
#                        for func in subrules[path[-1].name]:
#                            task_result[task] = func(node, path, task_attrs[task])
#                    except TypeError:
#                        task_result[task] = subrules[path[-1].name](node, path, task_attrs[task])
#
#            if all(result is False for result in task_result.values()):
#                break
#            else:
#                path.append(node)
#                node = node.uppernode
#
#        for task in resolve_tasks:
#            basket['nodes'] |= task_attrs[task]['nodes']
