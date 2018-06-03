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

def hidden_task(node, basket):
    node.knode = True

def _scan_mark(node, basket):
    node.knode = True

def _scan_hidden_mark(node, basket):
    if node.name == "hidden":
        node.knode = True

def _mark(node, path, attrs):
    path[-1].knode = True

def _mark_first_subnode(node, path, attrs):
    node.subnodes[0].search(_scan_mark, DFS_LF, stopnode=node)

def _mark_last_subnode(node, path, attrs):
    node.subnodes[-1].search(_scan_mark, DFS_LF, stopnode=node)

def _mark_prev_subnode(node, path, attrs):
    node.subnodes[node.subnodes.index(path[-1])-1].search(_scan_mark, DFS_LF, stopnode=node)

def _mark_next_subnode(node, path, attrs):
    node.subnodes[node.subnodes.index(path[-1])+1].search(_scan_mark, DFS_LF, stopnode=node)

def _mark_terminal_subnodes(node, path, attrs):
    for subnode in node.subnodes:
        if subnode.name == "terminal":
            subnode.knode = True

def _mark_hidden_subnodes(node, path, attrs):
    for subnode in node.subnodes:
        if subnode.name == "hidden":
            subnode.knode = True

def _mark_text_subnodes(node, path, attrs):
    _mark_terminal_subnodes(node, None, None)
    _mark_hidden_subnodes(node, None, None)

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
        'DataDivisionSection': [_mark, _mark_text_subnodes, _continue],
    },

    'frame_DataDivisionSection': {
        'WorkingStorageSection': [_mark, _continue],
    },

    'frame_WorkingStorageSection': {
        'DataDescriptionEntry': [_mark, _mark_text_subnodes, _continue],
    },

    'frame_DataDescriptionEntry': {
        'DataDescriptionEntryFormat1': [_mark, _continue],
    },

    'frame_DataDescriptionEntryFormat1': {
        'INTEGERLITERAL': [_mark, _continue],
        'DataName': [_mark, _mark_data_descentry_format1, _mark_text_subnodes, _continue],
        'DataPictureClause': [_mark, _mark_text_subnodes, _continue],
        'DataValueClause': [_mark, _mark_text_subnodes, _continue],
    },

    'frame_DataValueClause': {
        'VALUE': [_mark, _continue],
        'DataValueInterval': [_mark, _mark_text_subnodes, _continue],
    },

    'frame_DataPictureClause': {
        'PIC': [_mark, _continue],
        'PictureString': [_mark, _mark_text_subnodes, _continue],
    },

    'frame_PictureString': {
        'PictureChars': [_mark, _continue],
    },

    'frame_PictureChars': {
        'LPARENCHAR': [_mark, _continue],
        'RPARENCHAR': [_mark, _continue],
        'IDENTIFIER': [_mark, _continue],
        'IntegerLiteral': [_mark, _mark_text_subnodes, _continue],
    },

    'frame_DataValueInterval': {
        'DataValueIntervalFrom': [_mark, _continue],
    },

    'frame_DataValueIntervalFrom': {
        'Literal': [_mark, _continue],
        'CobolWord': [_mark, _continue],
    },

    #### ProcedureDivision ####

    'frame_ProcedureDivision': {
        'PROCEDURE': [_mark, _continue],
        'ProcedureDivisionBody': [_mark, _mark_text_subnodes, _continue],
    },

    'frame_ProcedureDivisionBody': {
        'Paragraphs': [_mark, _continue],
    },

    'frame_DisplayStatement': {
        'DISPLAY': [_mark, _continue],
        'DisplayOperand': [_mark, _mark_first_subnode, _continue],
    },

    'frame_PerformStatement': {
        'PERFORM': [_mark, _continue],
        'PerformInlineStatement': [_mark, _mark_first_subnode, _continue],
    },

    'frame_GobackStatement': {
        'GOBACK': [_mark, _continue],
    },

    'frame_PerformInlineStatement': {
        'PerformType': [_mark, _mark_last_subnode, _continue],
        'Statement': [_mark, _mark_last_subnode, _continue],
        'END_PERFORM': [_mark, _continue],
    },

    'frame_PerformType': {
        'PerformVarying': [_mark, _continue],
    },

    'frame_PerformVarying': {
        'PerformVaryingClause': [_mark, _continue],
    },

    'frame_PerformVaryingClause': {
        'VARYING': [_mark, _continue],
        'PerformVaryingPhrase': [_mark, _mark_first_subnode, _continue],
    },

    'frame_PerformVaryingPhrase': {
        'Identifier': [_mark, _continue],
        'PerformFrom': [_mark, _continue],
        'PerformBy': [_mark, _continue],
        'PerformUntil': [_mark, _continue],
    },

    'frame_PerformFrom': {
        'FROM': [_mark, _continue],
        'Literal': [_mark, _mark_first_subnode, _continue],
    },

    'frame_PerformBy': {
        'BY': [_mark, _continue],
        'Literal': [_mark, _mark_first_subnode, _continue],
    },

    'frame_PerformAfter': {
        'AFTER': [_mark, _continue],
        'Literal': [_mark, _mark_first_subnode, _continue],
    },

    'frame_PerformUntil': {
        'UNTIL': [_mark, _continue],
        'Literal': [_mark, _mark_terminal_subnodes, _continue],
        'Condition': [_mark, _mark_terminal_subnodes, _continue],
    },

    'frame_DisplayOperand': {
        'Identifier': [_mark, _continue],
        'Literal': [_mark, _continue],
    },

    #### Common ####

    'frame_root': {
        'RunUnit': [_mark, _continue],
    },

    'frame_RunUnit': {
        'CompilationUnit': [_mark, _continue],
    },

    'frame_CompilationUnit': {
        'ProgramUnit': [_mark, _mark_hidden_subnodes, _continue],
    },

    'frame_ProgramUnit': {
        'ProcedureDivision': [_mark, _mark_id_division, _continue],
        'DataDivision': [_mark, _continue],
    },

    'frame_Paragraphs': {
        'Paragraph': [_mark, _continue],
    },

    'frame_Paragraph': {
        'ParagraphName': [_mark, _mark_terminal_subnodes, _continue],
        'Sentence': [_mark, _mark_first_subnode, _mark_terminal_subnodes, _continue],
    },

    'frame_Sentence': {
        'Statement': [_mark, _continue],
    },

    'frame_Statement': {
        'PerformStatement': [_mark, _continue],
        'DisplayStatement': [_mark, _continue],
        'GobackStatement': [_mark, _continue],
    },

    'frame_Condition': {
        'CombinableCondition': [_mark, _continue],
    },

    'frame_CombinableCondition': {
        'SimpleCondition': [_mark, _continue],
    },

    'frame_SimpleCondition': {
        'RelationCondition': [_mark, _continue],
    },

    'frame_RelationCondition': {
        'RelationArithmeticComparison': [_mark, _continue],
    },

    'frame_RelationArithmeticComparison': {
        'ArithmeticExpression': [_mark, _continue],
        'RelationalOperator': [_mark, _continue],
    },

    'frame_RelationalOperator': {
        'MORETHANCHAR': [_mark, _continue],
    },

    'frame_ArithmeticExpression': {
        'MultDivs': [_mark, _continue],
    },

    'frame_MultDivs': {
        'Powers': [_mark, _continue],
    },

    'frame_Powers': {
        'Basis': [_mark, _mark_terminal_subnodes, _continue],
    },

    'frame_Basis': {
        'LPARENCHAR': [_mark, _continue],
        'RPARENCHAR': [_mark, _continue],
        'Identifier': [_mark, _mark_terminal_subnodes, _continue],
        'Literal': [_mark, _mark_terminal_subnodes, _continue],
    },

    'frame_Identifier': {
        'QualifiedDataName': [_mark, _continue],
        'TableCall': [_mark, _continue],
    },

    'frame_TableCall': {
        'QualifiedDataName': [_mark, _continue],
        'ReferenceModifier': [_mark, _continue],
    },

    'frame_QualifiedDataName': {
        'QualifiedDataNameFormat1': [_mark, _continue],
    },

    'frame_QualifiedDataNameFormat1': {
        'DataName': [_mark, _continue],
    },

    'frame_ReferenceModifier': {
        'LPARENCHAR': [_mark, _continue],
        'RPARENCHAR': [_mark, _continue],
        'COLONCHAR': [_mark, _continue],
        'CharacterPosition': [_mark, _mark_next_subnode,_continue],
        'Length': [_mark, _continue],
    },

    'frame_CharacterPosition': {
        'ArithmeticExpression': [_mark, _continue],
    },

    'frame_Length': {
        'ArithmeticExpression': [_mark, _continue],
    },

    'frame_ParagraphName': {
        'CobolWord': [_mark, _continue],
        'IntegerLiteral': [_mark, _continue],
    },

    'frame_DataName': {
        'CobolWord': [_mark, _continue],
    },

    'frame_CobolWord': {
        'IDENTIFIER': [_mark, _mark_hidden_subnodes, _continue],
    },

    'frame_Literal': {
        'NumericLiteral': [_mark, _continue],
        'NONNUMERICLITERAL': [_mark, _mark_hidden_subnodes, _continue],
    },

    'frame_NumericLiteral': {
        'IntegerLiteral': [_mark, _continue],
    },

    'frame_IntegerLiteral': {
        'INTEGERLITERAL': [_mark, _mark_hidden_subnodes, _continue],
    },

}


def pre_assemble(node, basket):

    if not has_scan(scan_type):

        ops = {}
        for pname, snodes in _operators.items():
            subops = {}
            ops[pname] = subops

            for sname, op in snodes.items():

                for task in scan_tasks:
                    analyzer_name = "%s_%s_%s"%(task, pname, sname)
                    if analyzer_name in globals():
                        op.insert(0, globals()[analyzer_name])

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
