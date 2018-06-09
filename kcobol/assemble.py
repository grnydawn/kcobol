# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
import logging
from builtins import *
from collections import OrderedDict

from stemtree import DFS_LF, Node

from .scan import _debug, _break, _continue, reg_scan, has_scan, push_scan, pop_scan
from .exception import AssembleError
from .util import exit

scan_type = 'assemble'

scan_tasks = (
    'frame',
)

def _first_terminal_subnode(node):

    first_subnode = None
    for subnode in node.subnodes:
        if subnode.name == "terminal":
            first_subnode = subnode
            break
    return first_subnode

def _last_terminal_subnode(node):

    last_subnode = None
    for subnode in reversed(node.subnodes):
        if subnode.name == "terminal":
            last_subnode = subnode
            break
    return last_subnode

def _next_terminal_subnode(node, prev_node):

    next_subnode = None
    for subnode in node.subnodes:
        if subnode is prev_node:
            next_subnode = subnode
        elif next_subnode is not None:
            next_subnode = subnode
            if subnode.name == "terminal":
                break
    return next_subnode

def _prev_terminal_subnode(node, next_node):

    prev_subnode = None
    for subnode in reversed(node.subnodes):
        if subnode is next_node:
            prev_subnode = subnode
        elif prev_subnode is not None:
            prev_subnode = subnode
            if subnode.name == "terminal":
                break
    return prev_subnode

def hidden_task(node, basket):
    node.knode = True

def _scan_mark(node, basket):
    node.knode = True

def _upward_mark(node, basket):
    while hasattr(node, 'uppernode'):
        node.knode = True
        node = node.uppernode

def _scan_hidden_mark(node, basket):
    if node.name == "hidden":
        node.knode = True

def _mark(node, path, attrs):
    path[-1].knode = True

def _mark_first_subnode(node, path, attrs):
    first_subnode = _first_terminal_subnode(node)
    first_subnode.search(_scan_mark, DFS_LF, stopnode=node)

def _mark_last_subnode(node, path, attrs):
    last_subnode = _last_terminal_subnode(node)
    last_subnode.search(_scan_mark, DFS_LF, stopnode=node)

def _mark_prev_subnode(node, path, attrs):
    prev_subnode = _prev_terminal_subnode(node, path[-1])
    prev_subnode.search(_scan_mark, DFS_LF, stopnode=node)

def _mark_next_subnode(node, path, attrs):
    next_subnode = _next_terminal_subnode(node, path[-1])
    next_subnode.search(_scan_mark, DFS_LF, stopnode=node)

def _mark_terminal_subnodes(node, path, attrs):
    for subnode in node.subnodes:
        if subnode.name == "terminal":
            subnode.knode = True

def _mark_hidden_subnodes(node, path, attrs):
    for subnode in node.subnodes:
        if subnode.name == "hidden":
            subnode.knode = True

def _mark_id_division(node, path, attrs):

    id_division = node.subnodes[0]
    id_division.search(_scan_mark, DFS_LF, stopnode=node)

def _mark_data_descentry_format1(node, path, attrs):
    for subnode in node.subnodes:
        if subnode.name in ('DataPictureClause',
            'DataValueClause'):
            subnode.search(_scan_mark, DFS_LF, stopnode=node)
    #import pdb; pdb.set_trace()

_operators = {

    #### IdentificationDivision ####

    #### DataDivision ####

    'frame_DataDivision': {
        'DataDivisionSection': [_mark_terminal_subnodes],
    },

    'frame_DataDivisionSection': {
        'WorkingStorageSection': [],
    },

    'frame_WorkingStorageSection': {
        'DataDescriptionEntry': [_mark_terminal_subnodes],
    },

    'frame_DataDescriptionEntry': {
        'DataDescriptionEntryFormat1': [],
    },

    'frame_DataDescriptionEntryFormat1': {
        'INTEGERLITERAL': [],
        'DataName': [_mark_data_descentry_format1, _mark_terminal_subnodes],
        'DataPictureClause': [_mark_terminal_subnodes],
        'DataUsageClause': [_mark_terminal_subnodes],
        'DataValueClause': [_mark_terminal_subnodes],
        'DataOccursClause': [_mark_terminal_subnodes],
    },

    'frame_DataValueClause': {
        'VALUE': [],
        'DataValueInterval': [_mark_terminal_subnodes],
    },

    'frame_DataPictureClause': {
        'PIC': [],
        'PictureString': [_mark_terminal_subnodes],
    },

    'frame_DataUsageClause': {
        'COMP_5': [],
        'END_DIVIDE': [],
    },

    'frame_DataOccursClause': {
        'OCCURS': [],
        'IntegerLiteral': [],
    },

    'frame_PictureString': {
        'PictureChars': [],
    },

    'frame_PictureChars': {
        'LPARENCHAR': [],
        'RPARENCHAR': [],
        'IDENTIFIER': [],
        'IntegerLiteral': [_mark_terminal_subnodes],
    },

    'frame_DataValueInterval': {
        'DataValueIntervalFrom': [],
    },

    'frame_DataValueIntervalFrom': {
        'Literal': [],
        'CobolWord': [],
    },

    #### ProcedureDivision ####

    'frame_ProcedureDivision': {
        'PROCEDURE': [],
        'ProcedureDivisionBody': [_mark_terminal_subnodes],
    },

    'frame_ProcedureDivisionBody': {
        'Paragraphs': [],
        'ProcedureSection': [],
    },

    'frame_DisplayStatement': {
        'DISPLAY': [],
        'DisplayOperand': [_mark_first_subnode],
    },

    'frame_PerformStatement': {
        'PERFORM': [],
        'PerformInlineStatement': [_mark_first_subnode],
        'PerformProcedureStatement': [_mark_first_subnode],
    },

    'frame_MoveStatement': {
        'MOVE': [],
        'ALL': [],
        'MoveToStatement': [_mark_terminal_subnodes],
        'MoveCorrespondingToStatement': [_mark_terminal_subnodes],
    },

#   : CALL (identifier | literal) callUsingPhrase? callGivingPhrase? onOverflowPhrase? onExceptionClause? notOnExceptionClause? END_CALL?


    'frame_CallStatement': {
        'CALL': [],
        'Identifier': [],
        'Literal': [],
        'CallUsingPhrase': [],
        'END_CALL': [],
    },

    'frame_InitializeStatement': {
        'INITIALIZE': [],
        'Identifier': [_mark_first_subnode],
        'InitializeReplacingPhrase': [_mark_first_subnode],
    },

    'frame_ExitStatement': {
        'EXIT': [],
        'PROGRAM': [],
    },

    'frame_MoveToStatement': {
        'MoveToSendingArea': [_mark_next_subnode],
        'TO': [],
        'Identifier': [_mark_prev_subnode],
    },

    'frame_AddStatement': {
        'ADD': [],
        'AddToStatement': [_mark_first_subnode],
    },

    'frame_AddToStatement': {
        'AddFrom': [_mark_next_subnode],
        'TO': [],
        'AddTo': [_mark_prev_subnode],
    },

    'frame_PerformProcedureStatement': {
        'ProcedureName': [_mark_terminal_subnodes],
        'THROUGH': [],
        'THRU': [],
        'PerformType': [],
    },

    'frame_DivideStatement': {
        'DIVIDE': [],
        'END_DIVIDE': [],
        'Identifier': [_mark_first_subnode],
        'Literal': [_mark_first_subnode],
        'DivideByGivingStatement': [_mark_first_subnode],
        'DivideRemainder': [_mark_first_subnode],
    },

    'frame_GobackStatement': {
        'GOBACK': [],
    },

    'frame_StopStatement': {
        'STOP': [],
        'RUN': [],
        'Literal': [],
    },

    'frame_PerformInlineStatement': {
        'PerformType': [_mark_last_subnode],
        'Statement': [_mark_last_subnode],
        'END_PERFORM': [],
    },

    'frame_DivideByGivingStatement': {
        'BY': [],
        'Identifier': [_mark_first_subnode],
        'Literal': [_mark_first_subnode],
        'DivideGivingPhrase': [_mark_first_subnode],
    },

    'frame_ProcedureSection': {
        'ProcedureSectionHeader': [_mark_next_subnode],
        'Paragraphs': [_mark_prev_subnode],
    },

    'frame_ProcedureSectionHeader': {
        'SectionName': [_mark_terminal_subnodes],
        'SECTION': [],
        'IntegerLiteral': [],
    },

    'frame_PerformType': {
        'PerformVarying': [],
    },

    'frame_PerformVarying': {
        'PerformVaryingClause': [],
    },

    'frame_PerformVaryingClause': {
        'VARYING': [],
        'PerformVaryingPhrase': [_mark_first_subnode],
    },

    'frame_PerformVaryingPhrase': {
        'Identifier': [],
        'PerformFrom': [],
        'PerformBy': [],
        'PerformUntil': [],
    },

    'frame_CallUsingParameter': {
        'CallByReferencePhrase': [],
        'CallByValuePhrase': [],
        'CallByContentPhrase': [],
    },

    'frame_CallUsingPhrase': {
        'USING': [],
        'CallUsingParameter': [],
    },

    'frame_CallByReferencePhrase': {
        'BY': [],
        'REFERENCE': [],
        'CallByReference': [],
    },

    'frame_PerformFrom': {
        'FROM': [],
        'Literal': [_mark_first_subnode],
    },

    'frame_PerformBy': {
        'BY': [],
        'Literal': [_mark_first_subnode],
    },

    'frame_PerformAfter': {
        'AFTER': [],
        'Literal': [_mark_first_subnode],
    },

    'frame_PerformUntil': {
        'UNTIL': [],
        'Literal': [_mark_terminal_subnodes],
        'Condition': [_mark_terminal_subnodes],
    },

    'frame_DisplayOperand': {
        'Identifier': [],
        'Literal': [],
    },

    'frame_DivideGivingPhrase': {
        'GIVING': [],
        'DivideGiving': [_mark_first_subnode],
    },

    'frame_DivideGiving': {
        'Identifier': [],
        'ROUNDED': [],
    },

    'frame_DivideRemainder': {
        'REMAINDER': [],
        'Identifier': [],
    },

    'frame_MoveToSendingArea': {
        'Identifier': [],
        'Literal': [],
    },

    'frame_AddFrom': {
        'Identifier': [],
        'Literal': [],
    },

    'frame_AddTo': {
        'Identifier': [],
        'ROUNDED': [],
    },

    'frame_CallByReference': {
        'ADDRESS': [],
        'OF': [],
        'INTEGER': [],
        'STRING': [],
        'Identifier': [],
        'Literal': [],
        'FileName': [],
        'OMITTED': [],
    },

    'frame_QualifiedInData': {
        'InData': [],
        'InTable': [],
    },

    'frame_InData': {
        'IN': [],
        'OF': [],
        'DataName': [],
    },


    #### Common ####

    'frame_root': {
        'RunUnit': [],
    },

    'frame_RunUnit': {
        'CompilationUnit': [],
    },

    'frame_CompilationUnit': {
        'ProgramUnit': [],
    },

    'frame_ProgramUnit': {
        'ProcedureDivision': [_mark_id_division],
        'DataDivision': [],
    },

    'frame_Paragraphs': {
        'Paragraph': [],
        'Sentence': [],
    },

    'frame_Paragraph': {
        'ParagraphName': [_mark_terminal_subnodes],
        'Sentence': [_mark_first_subnode, _mark_terminal_subnodes],
    },

    'frame_Sentence': {
        'Statement': [_mark_last_subnode],
    },

    'frame_Statement': {
        'PerformStatement': [],
        'DisplayStatement': [],
        'MoveStatement': [],
        'AddStatement': [],
        'DivideStatement': [],
        'InitializeStatement': [],
        'GobackStatement': [],
        'CallStatement': [],
        'ExitStatement': [],
        'StopStatement': [],
    },

    'frame_Condition': {
        'CombinableCondition': [],
    },

    'frame_CombinableCondition': {
        'SimpleCondition': [],
    },

    'frame_SimpleCondition': {
        'RelationCondition': [],
    },

    'frame_RelationCondition': {
        'RelationArithmeticComparison': [],
    },

    'frame_RelationArithmeticComparison': {
        'ArithmeticExpression': [],
        'RelationalOperator': [],
    },

    'frame_RelationalOperator': {
        'MORETHANCHAR': [],
        'LESSTHANCHAR': [],
    },

    'frame_Subscript': {
        'ALL': [],
        'QualifiedDataName': [],
    },

    'frame_ArithmeticExpression': {
        'MultDivs': [],
    },

    'frame_MultDivs': {
        'Powers': [],
    },

    'frame_Powers': {
        'Basis': [_mark_terminal_subnodes],
    },

    'frame_Basis': {
        'LPARENCHAR': [],
        'RPARENCHAR': [],
        'Identifier': [_mark_terminal_subnodes],
        'Literal': [_mark_terminal_subnodes],
    },

    'frame_Identifier': {
        'QualifiedDataName': [],
        'TableCall': [],
    },

    'frame_TableCall': {
        'LPARENCHAR': [],
        'RPARENCHAR': [],
        'QualifiedDataName': [],
        'ReferenceModifier': [],
        'Subscript': [],
    },

    'frame_QualifiedDataName': {
        'QualifiedDataNameFormat1': [],
    },

    'frame_QualifiedDataNameFormat1': {
        'DataName': [],
        'QualifiedInData': [],
    },

    'frame_ReferenceModifier': {
        'LPARENCHAR': [],
        'RPARENCHAR': [],
        'COLONCHAR': [],
        'CharacterPosition': [_mark_next_subnode],
        'Length': [],
    },

    'frame_CharacterPosition': {
        'ArithmeticExpression': [],
    },

    'frame_Length': {
        'ArithmeticExpression': [],
    },

    'frame_SectionName': {
        'CobolWord': [],
        'IntegerLiteral': [],
    },

    'frame_ProcedureName': {
        'ParagraphName': [],
        'InSection': [],
        'SectionName': [],
    },

    'frame_ParagraphName': {
        'CobolWord': [],
        'IntegerLiteral': [],
    },

    'frame_DataName': {
        'CobolWord': [],
    },

    'frame_CobolWord': {
        'IDENTIFIER': [],
    },

    'frame_Literal': {
        'NumericLiteral': [],
        'NONNUMERICLITERAL': [],
    },

    'frame_NumericLiteral': {
        'IntegerLiteral': [],
    },

    'frame_IntegerLiteral': {
        'INTEGERLITERAL': [],
    },

}


def pre_assemble(node, basket):

    if not has_scan(scan_type):

        ops = {}
        for pname, snodes in _operators.items():
            subops = {}
            ops[pname] = subops

            for sname, op in snodes.items():

                op.insert(0, _mark)
                op.insert(0, _mark_hidden_subnodes)

                for task in scan_tasks:
                    analyzer_name = "%s_%s_%s"%(task, pname, sname)
                    if analyzer_name in globals():
                        op.insert(0, globals()[analyzer_name])

                op.append(_continue)

                if sname.isupper():
                    subops[node.tokenmap[sname]]= op
                else:
                    subops[sname]= op


        reg_scan(scan_type, scan_tasks, ops, hidden_task)

    push_scan(scan_type)

    return node


def _insert_goback_statement(endnode):

    goback_terminal_node = Node()
    goback_statement_node = Node()

    goback_terminal_node.knode = True
    goback_terminal_node.name = "terminal"
    goback_terminal_node.text = "\n           GOBACK."
    goback_terminal_node.token = 1
    goback_terminal_node.uppernode = goback_statement_node

    goback_statement_node.knode = True
    goback_statement_node.name = "GobackStatement"
    del goback_statement_node.subnodes[:]
    goback_statement_node.subnodes.append(goback_terminal_node)

    endnode.insert_after(goback_statement_node)

def post_assemble(node, basket):


    dirtype, dirattrs, dirbegin, dirend = node.root.kcobol_directive
    _upward_mark(dirbegin, basket)
    _upward_mark(dirend, basket)

    assert dirtype == "extract"

    # process dirbegin
    for subnode in dirbegin.uppernode.subnodes:
        if subnode is dirbegin:
            break
        subnode.search(_scan_hidden_mark, DFS_LF, stopnode=subnode)

    # process dirend
    _insert_goback_statement(dirend)

    pop_scan()

    return node

def prune(node, basket):
    node.subnodes = [prune(s, basket) for s in node.subnodes if hasattr(s, 'knode') and s.knode is True]
    return node
