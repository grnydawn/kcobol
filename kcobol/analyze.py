# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *
from collections import OrderedDict

from .exception import AnalyzeError
from .util import exit

analysis_tasks = (
    'name',
)

def _debug(node, path, attrs):
    import pdb; pdb.set_trace()

def _break(node, path, attrs):
    return False

def _continue(node, path, attrs):
    return True

def _reg_name(node, path, attrs):
    if 'name' not in attrs:
        exit(exitno=1, msg='_reg_name at "%s": "name" key does not exists.'%node.name)
    node.program_node.add_name(attrs['name'])

def _collect_name(node, path, attrs):
    if 'name' in attrs:
        exit(exitno=1, msg='_collect_name: "name" key already exists.')
    attrs['name'] = path[0]

# NOTE
# - break as early as possible if not necessary

_operators = {

    #### IdentificationDivision ####

    'name_IdentificationDivision': {
        'IDENTIFICATION': _break,
    },

    'name_ProgramIdParagraph': {
        'PROGRAM_ID': _break,
        'ProgramName': (_reg_name, _break),
    },

    'name_ProgramName': {
        'CobolWord': (_collect_name, _continue),
    },

    #### DataDivision ####

    'name_DataDivision': {
        'DATA': _break,
    },

    'name_WorkingStorageSection': {
        'WORKING_STORAGE': _break,
    },

    'name_DataDescriptionEntryFormat1': {
        'INTEGERLITERAL': _break,
        'DataName': (_reg_name, _break),
    },

    'name_DataName': {
        'CobolWord': (_collect_name, _continue),
    },

    'name_DataPictureClause': {
        'PIC': _break,
    },

    'name_DataValueClause': {
        'VALUE': _break,
    },

    'name_PictureChars': {
        'IDENTIFIER': _break,
        'LPARENCHAR': _break,
        'RPARENCHAR': _break,
    },

    #### ProcedureDivision ####

    'name_ProcedureDivision': {
        'PROCEDURE': _break,
    },

    'name_Paragraph': {
        'ParagraphName': (_reg_name, _break),
    },

    'name_PerformStatement': {
        'PERFORM': _break,
    },

    'name_DisplayStatement': {
        'DISPLAY': _break,
    },

    'name_GobackStatement': {
        'GOBACK': _break,
    },

    'name_PerformInlineStatement': {
        'END_PERFORM': _break,
    },

    'name_DisplayOperand': {

        'Identifier': _break,
    },

    'name_QualifiedDataName': {
        'QualifiedDataNameFormat1': _continue,
    },

    'name_QualifiedDataNameFormat1': {
        'DataName': _continue,
    },

    'name_PerformVaryingClause': {
        'VARYING': _break,
    },

    'name_PerformVaryingPhrase': {
        'Identifier': _break,
    },

    'name_PerformFrom': {
        'FROM': _break,
    },

    'name_PerformBy': {
        'BY': _break,
    },

    'name_PerformUntil': {
        'UNTIL': _break,
    },

    'name_ParagraphName': {
        'CobolWord': (_collect_name, _continue),
    },

    #### Common ####

    'name_RunUnit': {
    },

    'name_Sentence': {
    },

    'name_RelationalOperator': {
        'MORETHANCHAR': _break,
    },

    'name_Basis': {
        'Identifier': _break,
    },

    'name_Identifier': {
        'QualifiedDataName': _continue,
        'TableCall': _continue,
    },

    'name_TableCall': {
        'QualifiedDataName': _continue,
    },

    'name_ReferenceModifier': {
        'LPARENCHAR': _break,
        'RPARENCHAR': _break,
        'COLONCHAR': _break,
    },

    'name_Literal': {
        'NONNUMERICLITERAL': _break,
    },

    'name_IntegerLiteral': {
        'INTEGERLITERAL': _break,
    },

    'name_CobolWord': {
        'IDENTIFIER': _continue,
    },
}

def pre_analysis(node, basket):

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
    for pname, subprime in _operators.items():
        subops = {}
        ops[pname] = subops
        for sname, op in subprime.items():
            if sname.isupper():
                subops[tokenmap[sname]]= op
            else:
                subops[sname]= op

    basket['entry_node'] = node

    return node

def post_analysis(node, basket):
    entry_node = basket['entry_node']
    del entry_node.root.skip_tokens
    del entry_node.root.operators
    del entry_node.root.revtokenmap
    return node

def analyze(node, basket):

    if node.name == 'hidden':
        return

    if node.name == 'terminal':

        path = [node]
        node = node.uppernode

        task_attrs = {}
        task_result = {}
        for task in analysis_tasks:
            task_attrs[task] = {}
            task_result[task] = None


        while node is not None:

            for task in analysis_tasks:
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
                        try:
                            for func in subrules[path[-1].token]:
                                task_result[task] = func(node, path, task_attrs[task])
                        except TypeError:
                            task_result[task] = subrules[path[-1].token](node, path, task_attrs[task])

                else:

                    if path[-1].name not in subrules:
                        exit(exitno=1, msg='Analyzer subrule name, "%s / %s", '
                        'is not found.'%(rulename, path[-1].name))

                    try:
                        for func in subrules[path[-1].name]:
                            task_result[task] = func(node, path, task_attrs[task])
                    except TypeError:
                        task_result[task] = subrules[path[-1].name](node, path, task_attrs[task])

            if all(result is False for result in task_result.values()):
                break
            else:
                path.append(node)
                node = node.uppernode
