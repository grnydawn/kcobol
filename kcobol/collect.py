# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *
from collections import OrderedDict

from .search import _debug, _break, _continue
from .exception import AnalyzeError
from .util import exit

collect_tasks = (
    'name',
)

#
#def _reg_name(node, path, attrs):
#    if 'name' not in attrs:
#        exit(exitno=1, msg='_reg_name at "%s": "name" key does not exists.'%node.name)
#    if node.program_node is None:
#        if node.name == "ProgramUnit":
#            node.add_name(attrs['name'])
#        else:
#            import pdb; pdb.set_trace()
#    else:
#        node.program_node.add_name(attrs['name'])
#
#def _collect_name(node, path, attrs):
#    if 'name' in attrs:
#        exit(exitno=1, msg='_collect_name: "name" key already exists.')
#    attrs['name'] = path[0]
#
#def _collect_goback(node, path, attrs):
#    curnode = node
#    while curnode is not None:
#        if curnode.name == "Sentence":
#            curnode.goback_stmt = node.uppernode
#            break
#        curnode = curnode.uppernode

# NOTE
# - break as early as possible if not necessary
# - collect name(terminal) as early as possible when it is clearly identified

_operators = {

#    #### IdentificationDivision ####
#
#    'name_IdentificationDivision': {
#        'IDENTIFICATION': [_break],
##        'ProgramIdParagraph': _continue,
#    },
#
#    'name_ProgramIdParagraph': {
#        'PROGRAM_ID': [_break],
#        'ProgramName': [_reg_name, _break],
#    },
#
#    'name_ProgramName': {
#        'CobolWord': [_collect_name, _continue],
#    },
#
#    #### EnvironmentDivision ####
#
#    'name_EnvironmentDivision': {
#        'ENVIRONMENT': [_break],
#    },
#
#    #### DataDivision ####
#
#    'name_DataDivision': {
#        'DATA': [_break],
#    },
#
#    'name_WorkingStorageSection': {
#        'WORKING_STORAGE': [_break],
#    },
#
#    'name_DataDescriptionEntryFormat1': {
#        'INTEGERLITERAL': [_break],
#        'DataName': [_reg_name, _break],
#    },
#
#    'name_DataOccursClause': {
#        'OCCURS': [_break],
#    },
#
#    'name_DataRedefinesClause': {
#        'REDEFINES': [_break],
#        'DataName': [_break],
#    },
#
#    'name_DataUsageClause': {
#        'COMP_5': [_break],
#    },
#
#    'name_DataName': {
#        'CobolWord': [_collect_name, _continue],
#    },
#
#    'name_DataPictureClause': {
#        'PIC': [_break ],
#    },
#
#    'name_DataValueClause': {
#        'VALUE': [_break ],
#    },
#
#    'name_PictureChars': {
#        'IDENTIFIER': [_break ],
#        'LPARENCHAR': [_break ],
#        'RPARENCHAR': [_break ],
#    },
#
#    #### ProcedureDivision ####
#
#    'name_ProcedureDivision': {
#        'PROCEDURE': [_break ],
#    },
#
#    'name_ProcedureSection': {
##        'ProcedureSectionHeader': [_reg_name, _break],
#    },
#
#    'name_ProcedureSectionHeader': {
#        'SectionName': [_reg_name, _break],
#    },
#
#    'name_Sentence': {
#    },
#
#    'name_Statement': {
#        'GobackStatement': [_collect_goback, _break],
#    },
#
#    'name_InitializeStatement': {
#        'INITIALIZE': [_break ],
#        'Identifier': [_break ],
#        'InitializeReplacingPhrase': [_break ],
#    },
#
#    'name_CallStatement': {
#        'CALL': [_break ],
#        'END_CALL': [_break ],
#    },
#
#    'name_MoveStatement': {
#        'MOVE': [_break ],
#    },
#
#    'name_MoveToStatement': {
#        'TO': [_break ],
#        'Identifier': [_break ],
#    },
#
#    'name_PerformStatement': {
#        'PERFORM': [_break ],
#    },
#
#    'name_DisplayStatement': {
#        'DISPLAY': [_break ],
#    },
#
#    'name_DivideStatement': {
#        'DIVIDE': [_break ],
#        'END_DIVIDE': [_break ],
#        'Identifier': [_break ],
#    },
#
#    'name_AddStatement': {
#        'ADD': [_break ],
#        'END_ADD': [_break ],
#        'Identifier': [_break ],
#    },
#
#    'name_AddToStatement': {
#        'TO': [_break ],
#    },
#
#    'name_DivideByGivingStatement': {
#        'BY': [_break ],
#    },
#
#    'name_GobackStatement': {
#        'GOBACK': [_continue ],
#    },
#
#    'name_PerformProcedureStatement': {
#        'THROUGH': [_break ],
#        'THRU': [_break ],
#        'ProcedureName': [_break ],
#        'PerformType': [_break ],
#    },
#
#    'name_PerformInlineStatement': {
#        'END_PERFORM': [_break ],
#    },
#
#    'name_StopStatement': {
#        'STOP': [_break ],
#        'RUN': [_break ],
#    },
#
#    'name_ExitStatement': {
#        'EXIT': [_break ],
#        'PROGRAM': [_break ],
#    },
#
#    'name_DivideGivingPhrase': {
#        'GIVING': [_break ],
#    },
#
#    'name_DivideGiving': {
#        'ROUNDED': [_break ],
#        'Identifier': [_break ],
#    },
#
#    'name_DivideRemainder': {
#        'REMAINDER': [_break ],
#        'Identifier': [_break ],
#    },
#
#    'name_AddTo': {
#        'Identifier': [_break ],
#        'ROUNDED': [_break ],
#    },
#
#    'name_MoveToSendingArea': {
#        'Identifier': [_break ],
#        'Literal': [_break ],
#    },
#
#    'name_DisplayOperand': {
#        'Identifier': [_break ],
#    },
#
#    'name_ProcedureName': {
#        'ParagraphName': [_continue ],
#    },
#
#    'name_QualifiedDataName': {
#        'QualifiedDataNameFormat1': [_continue ],
#    },
#
#    'name_QualifiedDataNameFormat1': {
#        'DataName': [_continue ],
##        'QualifiedInData': [_break ],
#    },
#
##    'name_QualifiedInData': {
##        'InData': [_break ],
##        'InTable': [_break ],
##    },
#
#    'name_InData': {
#        'IN': [_break ],
#        'OF': [_break ],
#        'DataName': [_break ],
#    },
#
#    'name_PerformVaryingClause': {
#        'VARYING': [_break ],
#    },
#
#    'name_CallUsingPhrase': {
#        'USING': [_break ],
#    },
#
#    'name_CallByReference': {
#        'ADDRESS': [_break ],
#        'OF': [_break ],
#        'INTEGER': [_break ],
#        'STRING': [_break ],
#        'OMITTED': [_break ],
#        'Identifier': [_break ],
#    },
#
#    'name_PerformVaryingPhrase': {
#        'Identifier': [_break ],
#    },
#
#    'name_PerformFrom': {
#        'FROM': [_break ],
#    },
#
#    'name_PerformBy': {
#        'BY': [_break ],
#    },
#
#    'name_PerformUntil': {
#        'UNTIL': [_break ],
#    },
#
#    'name_ParagraphName': {
#        'CobolWord': [_collect_name, _continue],
#    },
#
#    #### Common ####
#
#    'name_RunUnit': {
#    },
#
#    'name_ProgramUnit': {
##        'IdentificationDivision': [_reg_name, _break],
#    },
#
#    'name_Paragraph': {
#        'ParagraphName': [_reg_name, _break],
#    },
#
#    'name_RelationalOperator': {
#        'IS': [_break ],
#        'ARE': [_break ],
#        'NOT': [_break ],
#        'GREATER': [_break ],
#        'THAN': [_break ],
#        'MORETHANCHAR': [_break ],
#        'LESS': [_break ],
#        'LESSTHANCHAR': [_break ],
#        'EQUAL': [_break ],
#        'TO': [_break ],
#        'EQUALCHAR': [_break ],
#        'NOTEQUALCHAR': [_break ],
#        'MORETHANOREQUAL': [_break ],
#        'OR': [_break ],
#        'LESSTHANOREQUAL': [_break ],
#    },
#
#
#    'name_Basis': {
#        'Identifier': [_break ],
#    },
#
#    'name_Identifier': {
#        'QualifiedDataName': [_continue ],
#        'TableCall': [_break ],
#    },
#
#    'name_TableCall': {
#        'QualifiedDataName': [_break ],
#        'LPARENCHAR': [_break ],
#        'RPARENCHAR': [_break ],
#    },
#
#    'name_SectionName': {
#        'CobolWord': [_collect_name, _continue],
#    },
#
#    'name_Subscript': {
#        'ALL': [_break ],
#        'QualifiedDataName': [_break ],
#    },
#
#    'name_ReferenceModifier': {
#        'LPARENCHAR': [_break ],
#        'RPARENCHAR': [_break ],
#        'COLONCHAR': [_break ],
#    },
#
#    'name_Literal': {
#        'NONNUMERICLITERAL': [_break ],
#    },
#
#    'name_IntegerLiteral': {
#        'INTEGERLITERAL': [_break ],
#    },
#
#    'name_CobolWord': {
#        'IDENTIFIER': [_continue ]
#    },
}

TODO analyze and collect should be used simultaneously

def pre_collect(node, basket):

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

            for task in collect_tasks:
                analyzer_name = "%s_%s_%s"%(task, pname, sname)
                if analyzer_name in globals():
                    op.insert(0, globals()[analyzer_name])

            if sname.isupper():
                subops[tokenmap[sname]]= op
            else:
                subops[sname]= op

    node.root.analysis_tasks = collect_tasks

    basket['entry_node'] = node

    return node

def post_collect(node, basket):
    entry_node = basket['entry_node']
    del entry_node.root.skip_tokens
    del entry_node.root.analysis_tasks
    del entry_node.root.operators
    del entry_node.root.revtokenmap
    return node
