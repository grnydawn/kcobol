# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *
from collections import OrderedDict

import logging

from .scan import _debug, _break, _continue, reg_scan, has_scan, push_scan, pop_scan
from .exception import AnalyzeError
from .util import exit

scan_type = 'analyze'

scan_tasks = (
    'name',
)

# ???NOTE: EntryFormat?: register name into program unit and continue to Entry
# ???NOTE: Entry: regiter name if contains lower level EntryFormats
# ??? How to handle order of Entries with different levels???

_namespace_nodes = {
    "ProgramUnit": lambda n: n.rununit_node,
    "ProcedureSection": lambda n: n.program_node,
    "Paragraph": lambda n: n.program_node,
    "DataDescriptionEntryFormat1": lambda n: n.program_node,
}

_blockentry_nodes = {
    "DataDescriptionEntryFormat1": lambda s,n,o: _data_division_section_node(s,n,o),
}

def hidden_task(node, basket):
    pass

def _data_division_section_node(start, node, org_node):
    if hasattr(node, "name") and node.name == "DataDivisionSection":
        if not hasattr(node, "structureentries"):
            node.structureentries = {}
        node.structureentries[start] = org_node
        return node
    elif hasattr(node, "uppernode"):
        return _data_division_section_node(start, node.uppernode, org_node)
    else:
        return None

def _reg_name(node, path, attrs):

    if 'name' not in attrs:
        exit(exitno=1, msg='_reg_name at "%s": "name" key does not exist.'%node.name)

    namespace_node = _namespace_nodes[node.name](node)
    namespace_node.add_name(attrs['name'].text, attrs['name'], node)

    logging.info('"%s(%s)" is saved in a namespace of %s'%(
        attrs['name'].text, node.name, namespace_node.name))

def _reg_rununit_name(node, path, attrs):

    if 'name' not in attrs:
        exit(exitno=1, msg='_reg_rununit_name at "%s": "name" key does not exist.'%node.name)

    namespace_node = _namespace_nodes[node.name](node)
    namespace_node.add_name(attrs['name'].text, attrs['name'], node)

    logging.info('"%s(%s)" is saved in a namespace of %s'%(
        attrs['name'].text, node.name, namespace_node.name))

def _push_name(node, path, attrs):

    if 'name' in attrs:
        exit(exitno=1, msg='_push_name: "name" key already exists.')

    attrs['name'] = path[0]

def _reg_start(node, path, attrs):

    if 'start' not in attrs:
        exit(exitno=1, msg='_reg_start at "%s": "start" key does not exist.'%node.name)

    structure_node = _blockentry_nodes[node.name](attrs['start'], node, node)
    if structure_node not in attrs['structure_nodes']:
        attrs['structure_nodes'].append(structure_node)

def _push_start(node, path, attrs):

    if 'start' in attrs:
        exit(exitno=1, msg='_push_start: "start" key already exists.')

    attrs['start'] = path[0].start

# NOTE
# - collect name at the node that the name refers to: this is required because the referred node will be saved too.

_operators = {

    #### IdentificationDivision ####

    'name_IdentificationDivision': {
        'IDENTIFICATION': [_break],
        'ProgramIdParagraph': [_continue],
    },

    'name_ProgramIdParagraph': {
        'PROGRAM_ID': [_break],
        'ProgramName': [_continue],
    },

    'name_ProgramName': {
        'CobolWord': [_push_name, _continue],
    },

    #### EnvironmentDivision ####

    'name_EnvironmentDivision': {
        'ENVIRONMENT': [_break],
    },

    #### DataDivision ####

    'name_DataDivision': {
        'DATA': [_break],
    },

    'name_WorkingStorageSection': {
        'WORKING_STORAGE': [_break],
    },

    'name_DataDescriptionEntryFormat1': {
        'INTEGERLITERAL': [_push_start, _reg_start, _break],
        'DataName': [_reg_name, _break],
    },

    'name_DataOccursClause': {
        'OCCURS': [_break],
    },

    'name_DataRedefinesClause': {
        'REDEFINES': [_break],
        'DataName': [_break],
    },

    'name_DataUsageClause': {
        'COMP_5': [_break],
    },

    'name_DataName': {
        'CobolWord': [_push_name, _continue],
    },

    'name_DataPictureClause': {
        'PIC': [_break ],
    },

    'name_DataValueClause': {
        'VALUE': [_break ],
    },

    'name_DataValueIntervalFrom': {
        #'Literal': [_break],
        'CobolWord': [_push_name, _continue],
    },

    'name_PictureChars': {
        'IDENTIFIER': [_break ],
        'LPARENCHAR': [_break ],
        'RPARENCHAR': [_break ],
    },

    #### ProcedureDivision ####

    'name_ProcedureDivision': {
        'PROCEDURE': [_break ],
    },

    'name_ProcedureSection': {
        'ProcedureSectionHeader': [_reg_name, _break],
    },

    'name_ProcedureSectionHeader': {
        'SectionName': [_continue],
    },

    'name_Sentence': {
    },

    'name_Statement': {
        'GobackStatement': [_break],
    },

    'name_InitializeStatement': {
        'INITIALIZE': [_break ],
        'Identifier': [_break ],
        'InitializeReplacingPhrase': [_break ],
    },

    'name_CallStatement': {
        'CALL': [_break ],
        #'Literal': [_break ],
        'END_CALL': [_break ],
    },

    'name_MoveStatement': {
        'MOVE': [_break ],
    },

    'name_MoveToStatement': {
        'TO': [_break ],
        'Identifier': [_break ],
    },

    'name_PerformStatement': {
        'PERFORM': [_break ],
    },

    'name_DisplayStatement': {
        'DISPLAY': [_break ],
    },

    'name_DivideStatement': {
        'DIVIDE': [_break ],
        'END_DIVIDE': [_break ],
        'Identifier': [_break ],
    },

    'name_AddStatement': {
        'ADD': [_break ],
        'END_ADD': [_break ],
        'Identifier': [_break ],
    },

    'name_AddToStatement': {
        'TO': [_break ],
    },

    'name_DivideByGivingStatement': {
        'BY': [_break ],
    },

    'name_GobackStatement': {
        #'GOBACK': [_continue ],
        'GOBACK': [_break ],
    },

    'name_PerformProcedureStatement': {
        'THROUGH': [_break ],
        'THRU': [_break ],
        'ProcedureName': [_break ],
        'PerformType': [_break ],
    },

    'name_PerformInlineStatement': {
        'END_PERFORM': [_break ],
    },

    'name_StopStatement': {
        'STOP': [_break ],
        'RUN': [_break ],
    },

    'name_ExitStatement': {
        'EXIT': [_break ],
        'PROGRAM': [_break ],
    },

    'name_DivideGivingPhrase': {
        'GIVING': [_break ],
    },

    'name_DivideGiving': {
        'ROUNDED': [_break ],
        'Identifier': [_break ],
    },

    'name_DivideRemainder': {
        'REMAINDER': [_break ],
        'Identifier': [_break ],
    },

    'name_AddTo': {
        'Identifier': [_break ],
        'ROUNDED': [_break ],
    },

    'name_MoveToSendingArea': {
        'Identifier': [_break ],
        #'Literal': [_break ],
    },

    'name_DisplayOperand': {
        'Identifier': [_break ],
        #'Literal': [_break ],
    },

    'name_ProcedureName': {
        'ParagraphName': [_continue ],
    },

    'name_QualifiedDataName': {
        'QualifiedDataNameFormat1': [_continue ],
    },

    'name_QualifiedDataNameFormat1': {
        'DataName': [_continue ],
#        'QualifiedInData': [_break ],
    },

    'name_QualifiedInData': {
        'InData': [_break ],
        'InTable': [_break ],
    },

    'name_InData': {
        'IN': [_break ],
        'OF': [_break ],
        'DataName': [_break ],
    },

    'name_PerformVaryingClause': {
        'VARYING': [_break ],
    },

    'name_CallUsingPhrase': {
        'USING': [_break ],
    },

    'name_CallByReference': {
        'ADDRESS': [_break ],
        'OF': [_break ],
        'INTEGER': [_break ],
        'STRING': [_break ],
        'OMITTED': [_break ],
        'Identifier': [_break ],
    },

    'name_PerformVaryingPhrase': {
        'Identifier': [_break ],
    },

    'name_PerformFrom': {
        'FROM': [_break ],
    },

    'name_PerformBy': {
        'BY': [_break ],
    },

    'name_PerformUntil': {
        'UNTIL': [_break ],
    },

    'name_ParagraphName': {
        'CobolWord': [_push_name, _continue],
    },

    #### Common ####

    'name_RunUnit': {
    },

    'name_ProgramUnit': {
        'IdentificationDivision': [_reg_rununit_name, _break],
    },

    'name_Paragraph': {
        'ParagraphName': [_reg_name, _break],
    },

    'name_RelationalOperator': {
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


    'name_Basis': {
        'Identifier': [_break ],
    },

    'name_Identifier': {
        'QualifiedDataName': [_continue ],
        'TableCall': [_break ],
    },

    'name_TableCall': {
        'QualifiedDataName': [_break ],
        'LPARENCHAR': [_break ],
        'RPARENCHAR': [_break ],
    },

    'name_SectionName': {
        'CobolWord': [_push_name, _continue],
    },

    'name_Subscript': {
        'ALL': [_break ],
        'QualifiedDataName': [_break ],
    },

    'name_ReferenceModifier': {
        'LPARENCHAR': [_break ],
        'RPARENCHAR': [_break ],
        'COLONCHAR': [_break ],
    },

    'name_Literal': {
        'NONNUMERICLITERAL': [_break ],
    },

    'name_IntegerLiteral': {
        'INTEGERLITERAL': [_break ],
    },

    'name_CobolWord': {
        'IDENTIFIER': [_continue ]
    },
}

def pre_analyze(node, basket):

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
    basket['structure_nodes'] = []

    return node


def post_analyze(node, basket):
    stack = []
    for snode in basket['structure_nodes']:
        for start in sorted(snode.structureentries.keys()):

            entry_node = snode.structureentries[start]
            level_num = int(entry_node.subnodes[0].text)

            while len(stack) > 0 and level_num < stack[-1][0]:
                stack.pop()

            if len(stack) == 0:
                stack.append((level_num, entry_node))
            elif level_num == stack[-1][0]:
                if len(stack) > 1:
                    stack[-2][1].subentries.append(entry_node)

                    logging.info('"%s(%s...)" is saved as a subentry in "%s(%s...)"'%(
                        entry_node.name, entry_node.tocobol()[:10],
                        stack[-2][1].name, stack[-2][1].tocobol()[:10]))

                stack[-1] = (level_num, entry_node)
            else:
                if not hasattr(stack[-1][1], "subentries"):
                    stack[-1][1].subentries = []
                logging.info('"%s(%s...)" is saved as a subentry in "%s(%s...)"'%(
                    entry_node.name, entry_node.tocobol()[:10],
                    stack[-1][1].name, stack[-1][1].tocobol()[:10]))

                stack[-1][1].subentries.append(entry_node)
                stack.append((level_num, entry_node))

    del basket['structure_nodes']

    pop_scan()

    return node
