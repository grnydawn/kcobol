# -*- coding: utf-8 -*-
# finding resolutions

from __future__ import (absolute_import, division,
                        print_function)
from builtins import *
from collections import OrderedDict

import logging
import pickle

from stemtree import DFS_LF
from stemcobol import parse, EOF
from .scan import _debug, _break, _continue, upward_scan, reg_scan, has_scan, push_scan, pop_scan
from .collect import pre_collect, post_collect
from .exception import ResolveError
from .reader import parse_source
from .config import config, get_source_by_program_id
from .util import exit

# NOTE: resolve if name is definite
# NOTE: in(of) name may be used repeatitive. The last one should be used for resolve at beginning
# NOTE: There may be other cases that name is not definite at first
# NOTE: may ignore subscript in TableCall

scan_type = 'resolve'

scan_tasks = (
    'resolve',
)

_cache = {}
_resolved = {}

def hidden_task(node, basket):
    pass

def _push_name(node, path, attrs):
    if 'name' in attrs:
        exit(exitno=1, msg='_push_name: "name" key already exists.')
    attrs['name'] = path[0].text

def _push_string_name(node, path, attrs):
    if 'name' in attrs:
        exit(exitno=1, msg='_push_string_name: "name" key already exists.')
    attrs['name'] = path[0].text[1:-1]

def _resolve_at_rununit_node(node, name, upper_names):

    if name in node.rununit_node.namespace:
        res_node = node.rununit_node.namespace[name]
        # TODO: check if handlling upper_names is needed
        #if len(upper_names) > 0:
        #    import pdb; pdb.set_trace()
        return res_node

    srcpath, compilerpath = get_source_by_program_id(name)
    if srcpath is not None and compilerpath is not None:
        with open(compilerpath, 'rb') as f:
            compiler = pickle.load(f)
            #source = get_source(srcpath, compiler)
            root = parse_source(srcpath, compiler)
            #root = parse(srcpath, source.format, source.standard, config['opts/main/output'], root=node.root)
            # TODO: find programid terminal node and program node to return
            #import pdb; pdb.set_trace()
    return None, None

def _resolve_at_program_node(node, name, upper_names):

    if name in node.program_node.namespace:
        res_node = node.program_node.namespace[name]
        # TODO: check if handlling upper_names is needed
        #if len(upper_names) > 0:
        #    import pdb; pdb.set_trace()
        return res_node

    return None, None

def _resolve_node(node, name, namepath, attrs):

    # try to resolve at program nodes
    res_terminal, res_node = _resolve_at_program_node(node, name, namepath[1:])

    # try to resolve at rununit node
    if res_terminal is None or res_node is None:
        res_terminal, res_node = _resolve_at_rununit_node(node, name, namepath[1:])

    if res_terminal is None or res_node is None:

        logging.info("UNRES: "+name)
        attrs["unresolved"].add(tuple(namepath))

    else:

        attrs['nodes'].add(res_terminal)
        logging.info('RES: "%s" is resolved by "%s(%s...)"'%(name, res_node.name, res_node.tocobol()[:10]))

        if res_node not in _resolved:

            entries = [res_node]

            if hasattr(res_node, "subentries"):
                entries.extend(res_node.subentries)

            for entry in entries:
                _resolved[entry] = None

                collect_basket = {"unknowns": set(), "nodes": set()}
                entry.search(upward_scan, DFS_LF, basket=collect_basket, premove=pre_collect,
                postmove=post_collect, stopnode=entry.uppernode)

                attrs['nodes'] |= collect_basket["nodes"]
                attrs['unknowns'] |= collect_basket["unknowns"]

            #import pdb; pdb.set_trace()

# handling qualified data name formats
def _save_or_resolve_name(node, path, attrs):

    if 'name' not in attrs:
        exit(exitno=1, msg='_save_or_resolve_name at "%s": "name" key does not exists.'%node.name)

    nid = id(node)
    if nid not in _cache:
        _cache[nid] = [None for _ in node.subnodes]

    _cache[nid][node.subnodes.index(path[-1])] = attrs['name']

    if any(n is None for n in _cache[nid]):
        return
    else:
        _resolve_node(node, _cache[nid][0], _cache[nid], attrs)
        del _cache[nid]

def _resolve_name(node, path, attrs):

    if 'name' not in attrs:
        exit(exitno=1, msg='_resolve_name at "%s": "name" key does not exists.'%node.name)

    _resolve_node(node, attrs['name'], [attrs['name']], attrs)

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
#        'CobolWord': [_push_name, _continue],
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

    'resolve_DataOccursClause': {
        'OCCURS': [_break],
    },

    'resolve_DataRedefinesClause': {
        'REDEFINES': [_break],
        'DataName': [_resolve_name, _break],
    },

    'resolve_DataValueClause': {
        'VALUE': [_break],
    },

    'resolve_DataName': {
        'CobolWord': [_push_name, _continue],
    },

    'resolve_PictureChars': {
        'LPARENCHAR': [_break],
        'RPARENCHAR': [_break],
        'IDENTIFIER': [_break],
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

    'resolve_ProcedureDivision': {
        'PROCEDURE': [_break],
    },

    'resolve_ProcedureSection': {
    },

    'resolve_InitializeStatement': {
        'INITIALIZE': [_break],
    },


    'resolve_PerformStatement': {
        'PERFORM': [_break],
    },

    'resolve_PerformProcedureStatement': {
        'ProcedureName': [_resolve_name, _break],
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

    'resolve_CallStatement': {
        'CALL': [_break],
        'Literal': [_push_string_name, _resolve_name, _break],
    },

    'resolve_StopStatement': {
        'STOP': [_break],
        'RUN': [_break],
    },

    'resolve_ExitStatement': {
        'EXIT': [_break],
    },

    'resolve_AddStatement': {
        'ADD': [_break],
    },

    'resolve_DivideStatement': {
        'DIVIDE': [_break],
        'END_DIVIDE': [_break],
    },

    'resolve_GobackStatement': {
        'GOBACK': [_break],
    },

    'resolve_AddToStatement': {
        'TO': [_break],
    },

    'resolve_PerformInlineStatement': {
        'END_PERFORM': [_break],
    },

    'resolve_DivideByGivingStatement': {
        'BY': [_break],
    },


#    'resolve_DisplayOperand': {
#
#        'Identifier': [_break],
#    },
#
#    'resolve_QualifiedDataName': {
#        'QualifiedDataNameFormat1': [_continue],
#    },
#

    'resolve_ProcedureSectionHeader': {
        'SectionName': [_break],
    },

    'resolve_QualifiedDataNameFormat1': {
        'DataName': [_save_or_resolve_name, _break],
        'QualifiedInData': [_save_or_resolve_name, _break]
    },

    'resolve_DataDescriptionEntryFormat1': {
        'INTEGERLITERAL': [_break],
        'DataName': [_break],
    },

    'resolve_QualifiedInData': {
        'InData': [_continue ],
    },

    'resolve_PerformVaryingClause': {
        'VARYING': [_break],
    },

    'resolve_DataPictureClause': {
        'PIC': [_break],
    },

    'resolve_DataUsageClause': {
        'COMP_5': [_break],
    },

    'resolve_InData': {
        'IN': [_break ],
        'OF': [_break ],
        'DataName': [_continue ],
    },

    'resolve_CallUsingPhrase': {
        'USING': [_break ],
    },

    'resolve_DivideGivingPhrase': {
        'GIVING': [_break ],
    },

    'resolve_DivideRemainder': {
        'REMAINDER': [_break ],
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

    #### Common ####

    'resolve_RunUnit': {
        'ProgramUnit': _debug,
    },

    'resolve_Sentence': {
    },

    'resolve_Paragraph': {
        'ParagraphName': [_break],
    },

    'resolve_TableCall': {
        'LPARENCHAR': [_break],
        'RPARENCHAR': [_break],
    },

    'resolve_SectionName': {
        'CobolWord': [_push_name, _continue],
    },

    'resolve_ParagraphName': {
        'CobolWord': [_push_name, _continue],
    },

    'resolve_ProcedureName': {
        'ParagraphName': [_continue],
    },

    'resolve_RelationalOperator': {
        'MORETHANCHAR': [_break],
        'LESSTHANCHAR': [_break],
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
        'NONNUMERICLITERAL': [_continue],
    },

    'resolve_IntegerLiteral': {
        'INTEGERLITERAL': [_break],
    },

    'resolve_CobolWord': {
        'IDENTIFIER': [_continue],
    },
}

def pre_resolve(node, basket):

    _cache.clear()

    if not has_scan(scan_type):

        ops = {}
        for pname, snodes in _operators.items():
            subops = {}
            ops[pname] = subops

            for sname, op in snodes.items():

                for task in scan_tasks:
                    resolve_name = "%s_%s_%s"%(task, pname, sname)
                    if resolve_name in globals():
                        op.insert(0, globals()[resolve_name])

                if sname.isupper():
                    subops[node.tokenmap[sname]]= op
                else:
                    subops[sname]= op

        reg_scan(scan_type, scan_tasks, ops, hidden_task)

    push_scan(scan_type)

    return node


def post_resolve(node, basket):
    pop_scan()
    return node
