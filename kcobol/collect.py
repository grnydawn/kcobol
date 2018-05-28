# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *
from collections import OrderedDict

from .search import _debug, _break, _continue, reg_search, has_search, push_search, pop_search
from .exception import AnalyzeError
from .util import exit

search_type = 'collect'

search_tasks = (
    'collect',
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

def _collect_name(node, path, attrs):
    attrs['names'].append(path[0])

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
#    'collect_IdentificationDivision': {
#        'IDENTIFICATION': [_break],
##        'ProgramIdParagraph': _continue,
#    },
#
#    'collect_ProgramIdParagraph': {
#        'PROGRAM_ID': [_break],
#        'ProgramName': [_reg_name, _break],
#    },
#
#    'collect_ProgramName': {
#        'CobolWord': [_collect_name, _continue],
#    },
#
#    #### EnvironmentDivision ####
#
#    'collect_EnvironmentDivision': {
#        'ENVIRONMENT': [_break],
#    },
#
#    #### DataDivision ####
#
#    'collect_DataDivision': {
#        'DATA': [_break],
#    },
#
#    'collect_WorkingStorageSection': {
#        'WORKING_STORAGE': [_break],
#    },

    'collect_DataDescriptionEntryFormat1': {
        'INTEGERLITERAL': [_break],
        'DataName': [_break],
    },

    'collect_DataOccursClause': {
        'OCCURS': [_break],
    },

    'collect_DataRedefinesClause': {
        'REDEFINES': [_break],
        'DataName': [_collect_name, _break],
    },

    'collect_DataUsageClause': {
        'COMP_5': [_break],
    },

    'collect_DataName': {
        'CobolWord': [_continue],
    },

    'collect_DataPictureClause': {
        'PIC': [_break ],
    },

    'collect_DataValueClause': {
        'VALUE': [_break ],
    },

    'collect_PictureChars': {
        'IDENTIFIER': [_break ],
        'LPARENCHAR': [_break ],
        'RPARENCHAR': [_break ],
    },

    #### ProcedureDivision ####

    'collect_ProcedureDivision': {
        'PROCEDURE': [_break ],
    },

    'collect_ProcedureSection': {
    },

    'collect_ProcedureSectionHeader': {
        'SectionName': [_break ],
    },

    'collect_InitializeStatement': {
        'INITIALIZE': [_break ],
        'Identifier': [_collect_name, _break ],
##        'InitializeReplacingPhrase': [_break ],
    },

    'collect_CallStatement': {
        'CALL': [_break ],
        'END_CALL': [_break ],
    },

    'collect_MoveStatement': {
        'MOVE': [_break ],
    },

    'collect_MoveToStatement': {
        'TO': [_break ],
        'Identifier': [_collect_name, _break ],
    },

    'collect_PerformStatement': {
        'PERFORM': [_break ],
    },

    'collect_DisplayStatement': {
        'DISPLAY': [_break ],
    },

    'collect_DivideStatement': {
        'DIVIDE': [_break ],
        'END_DIVIDE': [_break ],
        'Identifier': [_collect_name, _break ],
    },

    'collect_AddStatement': {
        'ADD': [_break ],
        'END_ADD': [_break ],
    },

    'collect_AddToStatement': {
        'TO': [_break ],
    },

    'collect_DivideByGivingStatement': {
        'BY': [_break ],
    },

    'collect_GobackStatement': {
        'GOBACK': [_break ],
    },

    'collect_PerformProcedureStatement': {
        'THROUGH': [_break ],
        'THRU': [_break ],
        'ProcedureName': [_collect_name, _break ],
##        'PerformType': [_break ],
    },

    'collect_PerformInlineStatement': {
        'END_PERFORM': [_break ],
    },

    'collect_StopStatement': {
        'STOP': [_break ],
        'RUN': [_break ],
    },

    'collect_ExitStatement': {
        'EXIT': [_break ],
        'PROGRAM': [_break ],
    },

    'collect_DivideGivingPhrase': {
        'GIVING': [_break ],
    },

    'collect_DivideGiving': {
        'ROUNDED': [_break ],
        'Identifier': [_collect_name, _break ],
    },

    'collect_DivideRemainder': {
        'REMAINDER': [_break ],
        'Identifier': [_collect_name, _break ],
    },

    'collect_AddTo': {
        'ROUNDED': [_break ],
        'Identifier': [_collect_name, _break ],
    },

    'collect_MoveToSendingArea': {
        'Identifier': [_collect_name, _break ],
#        'Literal': [_break ],
    },

    'collect_DisplayOperand': {
        'Identifier': [_collect_name, _break],
    },

    'collect_ProcedureName': {
        'ParagraphName': [_continue ],
    },

    'collect_QualifiedDataName': {
        'QualifiedDataNameFormat1': [_continue ],
    },

    'collect_QualifiedDataNameFormat1': {
        'DataName': [_continue ],
#        'QualifiedInData': [_break ],
    },

###    'collect_QualifiedInData': {
###        'InData': [_break ],
###        'InTable': [_break ],
###    },

    'collect_InData': {
        'IN': [_break ],
        'OF': [_break ],
        'DataName': [_break ], # TODO: check if _break is valid
    },

    'collect_PerformVaryingClause': {
        'VARYING': [_break ],
    },

    'collect_CallUsingPhrase': {
        'USING': [_break ],
    },

    'collect_CallByReference': {
        'ADDRESS': [_break ],
        'OF': [_break ],
        'INTEGER': [_break ],
        'STRING': [_break ],
        'OMITTED': [_break ],
        'Identifier': [_break ],
    },

    'collect_PerformVaryingPhrase': {
        'Identifier': [_collect_name, _break],
    },

    'collect_PerformFrom': {
        'FROM': [_break ],
    },

    'collect_PerformBy': {
        'BY': [_break ],
    },

    'collect_PerformUntil': {
        'UNTIL': [_break ],
    },

    'collect_ParagraphName': {
        'CobolWord': [_continue],
    },

    #### Common ####

    'collect_RunUnit': {
    },

##    'collect_ProgramUnit': {
###        'IdentificationDivision': [_reg_name, _break],
##    },

    'collect_Sentence': {
    },

#    'collect_Statement': {
#    },

    'collect_Paragraph': {
        'ParagraphName': [_break],
    },

    'collect_RelationArithmeticComparison': {
        'ArithmeticExpression': [_collect_name, _break],
    },


    'collect_RelationalOperator': {
        'IS': [_break ],
        'ARE': [_break ],
        'NOT': [_break ],
        'GREATER': [_break ],
        'THAN': [_break ],
        'MORETHANCHAR': [_break ],
        'LESS': [_break ],
        'LESSTHANCHAR': [_break ],
        'EQUAL': [_break ],
        'TO': [_break ],
        'EQUALCHAR': [_break ],
        'NOTEQUALCHAR': [_break ],
        'MORETHANOREQUAL': [_break ],
        'OR': [_break ],
        'LESSTHANOREQUAL': [_break ],
    },


    'collect_ArithmeticExpression': {
        'MultDivs': [_continue],
    },

    'collect_MultDivs': {
        'Powers': [_continue],
    },

    'collect_Powers': {
        'Basis': [_continue],
    },

    'collect_Basis': {
        'Identifier': [_continue],
    },

    'collect_Identifier': {
        'QualifiedDataName': [_continue ],
        'TableCall': [_continue ],
    },

    'collect_TableCall': {
        'QualifiedDataName': [_continue],
        'LPARENCHAR': [_break ],
        'RPARENCHAR': [_break ],
    },

    'collect_SectionName': {
        'CobolWord': [_continue],
    },

    'collect_Subscript': {
        'ALL': [_break ],
        'QualifiedDataName': [_collect_name, _break ],
    },


    'collect_CharacterPosition': {
        'ArithmeticExpression': [_collect_name, _break],
    },

    'collect_ReferenceModifier': {
        'LPARENCHAR': [_break ],
        'RPARENCHAR': [_break ],
        'COLONCHAR': [_break ],
    },

    'collect_Literal': {
        'NONNUMERICLITERAL': [_break ],
    },

    'collect_IntegerLiteral': {
        'INTEGERLITERAL': [_break ],
    },

    'collect_CobolWord': {
        'IDENTIFIER': [_continue ]
    },
}


def pre_collect(node, basket):

    if not has_search(search_type):

        ops = {}
        for pname, snodes in _operators.items():
            subops = {}
            ops[pname] = subops

            for sname, op in snodes.items():

                for task in search_tasks:
                    collect_name = "%s_%s_%s"%(task, pname, sname)
                    if collect_name in globals():
                        op.insert(0, globals()[collect_name])

                if sname.isupper():
                    subops[node.tokenmap[sname]]= op
                else:
                    subops[sname]= op

        reg_search(search_type, search_tasks, ops)

    push_search(search_type)
    basket['names'] = []

    return node


def post_collect(node, basket):
    pop_search()
    return node

