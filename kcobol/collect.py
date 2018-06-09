# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *
from collections import OrderedDict

import logging

from .scan import _debug, _break, _continue, reg_scan, has_scan, push_scan, pop_scan
from .exception import AnalyzeError
from .util import exit

scan_type = 'collect'

scan_tasks = (
    'collect',
)


def hidden_task(node, basket):
    pass

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

def _collect_node(node, path, attrs):

    logging.info('"%s" is collected as a kernel node at "%s"'%(path[0].text, node.name))

    attrs['nodes'].add(path[0])


def _collect_name(node, path, attrs):

    logging.info('"%s" is collected as an unknown node at "%s"'%(path[0].text, node.name))

    attrs['unknowns'].add(path[0])

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

###    #### IdentificationDivision ####
###
###    'collect_IdentificationDivision': {
###        'IDENTIFICATION': [_break],
####        'ProgramIdParagraph': _continue,
###    },
###
###    'collect_ProgramIdParagraph': {
###        'PROGRAM_ID': [_break],
###        'ProgramName': [_reg_name, _break],
###    },
###
###    'collect_ProgramName': {
###        'CobolWord': [_collect_name, _continue],
###    },
###
###    #### EnvironmentDivision ####
###
###    'collect_EnvironmentDivision': {
###        'ENVIRONMENT': [_break],
###    },
###
###    #### DataDivision ####
###
###    'collect_DataDivision': {
###        'DATA': [_break],
###    },
###
###    'collect_WorkingStorageSection': {
###        'WORKING_STORAGE': [_break],
###    },

    'collect_DataDescriptionEntryFormat1': {
        'INTEGERLITERAL': [_collect_node, _break],
        'DataName': [_break],
    },

    'collect_DataOccursClause': {
        'OCCURS': [_collect_node, _break],
    },

    'collect_DataRedefinesClause': {
        'REDEFINES': [_collect_node, _break],
##        'DataName': [_collect_name, _break],
    },

    'collect_DataUsageClause': {
        'COMP_5': [_collect_node, _break],
    },

    'collect_DataName': {
        'CobolWord': [_continue],
    },

    'collect_DataPictureClause': {
        'PIC': [_collect_node, _break ],
    },

    'collect_DataValueClause': {
        'VALUE': [_collect_node, _break ],
    },

    'collect_PictureChars': {
        'IDENTIFIER': [_collect_node, _break ],
        'LPARENCHAR': [_collect_node, _break ],
        'RPARENCHAR': [_collect_node, _break ],
    },

    #### ProcedureDivision ####

    'collect_ProcedureDivision': {
        'PROCEDURE': [_collect_node, _break ],
    },

    'collect_ProcedureSection': {
#        'ProcedureSectionHeader': [_debug ],
    },

    'collect_ProcedureSectionHeader': {
        'SectionName': [_break ],
    },

    'collect_InitializeStatement': {
        'INITIALIZE': [_collect_node, _break ],
#        'Identifier': [_collect_name, _break ],
#        'InitializeReplacingPhrase': [_break ],
    },

    'collect_CallStatement': {
        'CALL': [_collect_node, _break ],
        'END_CALL': [_collect_node, _break ],
    },

    'collect_MoveStatement': {
        'MOVE': [_collect_node, _break ],
    },

    'collect_MoveToStatement': {
        'TO': [_collect_node, _break ],
#        'Identifier': [_collect_name, _break ],
    },

    'collect_PerformStatement': {
        'PERFORM': [_collect_node, _break ],
    },

    'collect_DisplayStatement': {
        'DISPLAY': [_collect_node, _break ],
    },

    'collect_DivideStatement': {
        'DIVIDE': [_collect_node, _break ],
        'END_DIVIDE': [_collect_node, _break ],
#        'Identifier': [_collect_name, _break ],
    },

    'collect_AddStatement': {
        'ADD': [_collect_node, _break ],
        'END_ADD': [_collect_node, _break ],
    },

    'collect_AddToStatement': {
        'TO': [_collect_node, _break ],
    },

    'collect_DivideByGivingStatement': {
        'BY': [_collect_node, _break ],
    },

    'collect_GobackStatement': {
        'GOBACK': [_collect_node, _break ],
    },

    'collect_PerformProcedureStatement': {
        'THROUGH': [_collect_node, _break ],
        'THRU': [_collect_node, _break ],
        'ProcedureName': [_collect_name, _break ],
###        'PerformType': [_break ],
    },

    'collect_PerformInlineStatement': {
        'END_PERFORM': [_collect_node, _break ],
    },

    'collect_StopStatement': {
        'STOP': [_collect_node, _break ],
        'RUN': [_collect_node, _break ],
    },

    'collect_ExitStatement': {
        'EXIT': [_collect_node, _break ],
        'PROGRAM': [_collect_node, _break ],
    },

    'collect_DivideGivingPhrase': {
        'GIVING': [_collect_node, _break ],
    },

    'collect_DivideGiving': {
        'ROUNDED': [_collect_node, _break ],
#        'Identifier': [_collect_name, _break ],
    },

    'collect_DivideRemainder': {
        'REMAINDER': [_collect_node, _break ],
#        'Identifier': [_collect_name, _break ],
    },

    'collect_AddTo': {
        'ROUNDED': [_collect_node, _break ],
#        'Identifier': [_collect_name, _break ],
    },

    'collect_MoveToSendingArea': {
#        'Identifier': [_collect_name, _break ],
##        'Literal': [_break ],
    },

    'collect_DisplayOperand': {
#        'Identifier': [_collect_name, _break],
    },

    'collect_ProcedureName': {
        'ParagraphName': [_continue ],
    },

    'collect_QualifiedDataName': {
##        'QualifiedDataNameFormat1': [_continue ],
    },

    'collect_QualifiedDataNameFormat1': {
        'DataName': [_collect_name, _break ],
##        'QualifiedInData': [_break ],
    },

    'collect_QualifiedInData': {
####        'InData': [_break ],
####        'InTable': [_break ],
    },

    'collect_InData': {
        'IN': [_collect_node, _break ],
        'OF': [_collect_node, _break ],
#        'DataName': [_break ], # TODO: assumes that first name is a registered resource name
    },

    'collect_PerformVaryingClause': {
        'VARYING': [_collect_node, _break ],
    },

    'collect_CallUsingPhrase': {
        'USING': [_collect_node, _break ],
    },

    'collect_CallByReference': {
        'ADDRESS': [_collect_node, _break ],
        'OF': [_collect_node, _break ],
        'INTEGER': [_collect_node, _break ],
        'STRING': [_collect_node, _break ],
        'OMITTED': [_collect_node, _break ],
        'Identifier': [_collect_node, _break ],
    },

#    'collect_PerformVaryingPhrase': {
#        'Identifier': [_collect_name, _break],
#    },

    'collect_PerformFrom': {
        'FROM': [_collect_node, _break ],
    },

    'collect_PerformBy': {
        'BY': [_collect_node, _break ],
    },

    'collect_PerformUntil': {
        'UNTIL': [_collect_node, _break ],
    },

    'collect_ParagraphName': {
        'CobolWord': [_continue],
    },

    #### Common ####

    'collect_RunUnit': {
    },

###    'collect_ProgramUnit': {
####        'IdentificationDivision': [_reg_name, _break],
###    },

    'collect_Sentence': {
    },

    'collect_Statement': {
    },

    'collect_Paragraph': {
        'ParagraphName': [_break],
    },

#    'collect_RelationArithmeticComparison': {
##        'ArithmeticExpression': [_collect_name, _break],
##    },
##

    'collect_RelationalOperator': {
        'IS': [_collect_node, _break ],
        'ARE': [_collect_node, _break ],
        'NOT': [_collect_node, _break ],
        'GREATER': [_collect_node, _break ],
        'THAN': [_collect_node, _break ],
        'MORETHANCHAR': [_collect_node, _break ],
        'LESS': [_collect_node, _break ],
        'LESSTHANCHAR': [_collect_node, _break ],
        'EQUAL': [_collect_node, _break ],
        'TO': [_collect_node, _break ],
        'EQUALCHAR': [_collect_node, _break ],
        'NOTEQUALCHAR': [_collect_node, _break ],
        'MORETHANOREQUAL': [_collect_node, _break ],
        'OR': [_collect_node, _break ],
        'LESSTHANOREQUAL': [_collect_node, _break ],
    },


##    'collect_ArithmeticExpression': {
##        'MultDivs': [_continue],
##    },
##
##    'collect_MultDivs': {
##        'Powers': [_continue],
##    },
##
##    'collect_Powers': {
##        'Basis': [_continue],
##    },
##
##    'collect_Basis': {
##        'Identifier': [_continue],
##    },
##
##    'collect_Identifier': {
##        'QualifiedDataName': [_continue ],
##        'TableCall': [_continue ],
##    },
#
    'collect_TableCall': {
#        'QualifiedDataName': [_continue],
        'LPARENCHAR': [_collect_node, _break ],
        'RPARENCHAR': [_collect_node, _break ],
    },

    'collect_SectionName': {
        'CobolWord': [_continue],
    },

#    'collect_Subscript': {
#        'ALL': [_break ],
#        'QualifiedDataName': [_collect_name, _break ],
#    },
#
#
#    'collect_CharacterPosition': {
#        'ArithmeticExpression': [_collect_name, _break],
#    },

    'collect_ReferenceModifier': {
        'LPARENCHAR': [_collect_node, _break ],
        'RPARENCHAR': [_collect_node, _break ],
        'COLONCHAR': [_collect_node, _break ],
    },

    'collect_Literal': {
        'NONNUMERICLITERAL': [_collect_node, _break ],
    },

    'collect_IntegerLiteral': {
        'INTEGERLITERAL': [_collect_node, _break ],
    },

    'collect_CobolWord': {
        'IDENTIFIER': [_collect_node, _continue ]
    },
}


def pre_collect(node, basket):

    if not has_scan(scan_type):

        ops = {}
        for pname, snodes in _operators.items():
            subops = {}
            ops[pname] = subops

            for sname, op in snodes.items():

                #op.insert(0, _collect_node)

                for task in scan_tasks:
                    collect_name = "%s_%s_%s"%(task, pname, sname)
                    if collect_name in globals():
                        op.insert(0, globals()[collect_name])

                #op.append(_break)

                if sname.isupper():
                    subops[node.tokenmap[sname]]= op
                else:
                    subops[sname]= op

        reg_scan(scan_type, scan_tasks, ops, hidden_task)

    push_scan(scan_type)

    return node


def post_collect(node, basket):
    pop_scan()
    return node

