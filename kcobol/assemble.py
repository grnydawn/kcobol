# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *
from collections import OrderedDict

from stemtree import DFS_RF

from .exception import AssembleError
from .util import exit

assemble_tasks = (
    'frame',
)


###############################
# debug
##############################
_debug_texts = tuple()
#_debug_texts = ( 'W-COUNT', )

def _debug(node, path, attrs):
    import pdb; pdb.set_trace()

def debugtree(node, level=0):
    i = 0
    while i < level:
        i += 1
        if node.uppernode is None:
            break
        else:
            node = node.uppernode
    print(node.treeview('text'))

###############################
# common assembler
##############################

def _mark_subtree(node):
    node.knode = True
    for subnode in node.subnodes:
        _mark_subtree(subnode)

def _mark_iddiv_subtree(node, path, attrs):

    if node.name != "IdentificationDivision":
        return

    node.knode = True

    if hasattr(node, '__iddiv_processed__'):
        return

    node.__iddiv_processed__ = True

    for subnode in _mark_subnodes(node, path, attrs):
        if subnode.name in ("ProgramIdParagraph", ):
            _mark_subtree(subnode)
        else:
            import pdb; pdb.set_trace()

def _break(node, path, attrs):
    return False

def _continue(node, path, attrs):
    return True

def _mark(node, path, attrs):
    node.knode = True

def _check(node, path, attrs):
    if node.uppernode is None:
        return False
    return not node.uppernode.knode

def _mark_and_check(node, path, attrs):
    _mark(node, path, attrs)
    return _check(node, path, attrs)

def _move_dotfs(node, path, attrs):

    def _find_last_terminal(snode, basket):
        if snode.name == "terminal":
            basket['insert_after'] = snode
            return snode.STOP_SEARCH

    def _add_dotfs(snode, basket):
        tnode = basket['insert_after']
        dotfs = basket['dotfs']
        if tnode.token != node.tokenmap['DOT_FS']:
            tnode.uppernode.insert_after(tnode, dotfs)

    last = None
    dotfs = None
    for idx, subnode in enumerate(node.subnodes):
        if subnode.name == "hidden":
            pass
        elif subnode.name == "terminal":
            if subnode.token == node.tokenmap['DOT_FS']:
                dotfs = idx
                break
        elif subnode.knode is True:
            last = idx

    if last is not None and dotfs is not None:
        dotfs_node = node.subnodes.pop(dotfs)
        last_node = node.subnodes[last]
        basket = {'dotfs': dotfs_node}
        last_node.search(_find_last_terminal, DFS_RF, basket=basket,
            postmove=_add_dotfs)

def _goback_stmt(node, path, attrs):
    if node.knode is True:
        if hasattr(node, 'goback_stmt') and node.goback_stmt is not None:
            _mark_subtree(node.goback_stmt)

#def _collect_name(node, path, attrs):
#    if 'name' in attrs:
#        exit(exitno=1, msg='_collect_name: "name" key already exists.')
#    attrs['name'] = path[0]
#
#def _add_name(node, path, attrs):
#    if 'name' not in attrs:
#        exit(exitno=1, msg='_add_name at "%s": "name" key does not exists.'%node.name)
#    node.program_node.add_name(attrs['name'])

# NOTE
# - break as early as possible if not necessary

def _mark_subnodes(node, path, attrs):

    for subnode in node.subnodes:
        if subnode is path[-1]: continue

        if subnode.name in ('hidden', 'terminal'):
            subnode.knode = True
            continue

        yield subnode

###############################
# prerun assemblers
##############################

def _CompilationUnit_ProgramUnit(node, path, attrs):

    for subnode in _mark_subnodes(node, path, attrs):
        pass

def _ProgramUnit_ProcedureDivision(node, path, attrs):

    for subnode in _mark_subnodes(node, path, attrs):
        if subnode.name in ("IdentificationDivision",
            "EnvironmentDivision"):
            _mark_iddiv_subtree(subnode, path, attrs)
        elif subnode.name in ("DataDivision", ):
            pass
        else:
            import pdb; pdb.set_trace()

def _ProcedureDivision_ProcedureDivisionBody(node, path, attrs):

    for subnode in _mark_subnodes(node, path, attrs):
        import pdb; pdb.set_trace()

def _ProcedureDivisionBody_Paragraphs(node, path, attrs):
    pass

def _ProcedureSection_ProcedureSectionHeader(node, path, attrs):
    idx = node.subnodes.index(path[-1])
    node.subnodes[idx+1].knode = True # DOT_FS

def _ProcedureSectionHeader_SectionName(node, path, attrs):
    idx = node.subnodes.index(path[-1])
    node.subnodes[idx+1].knode = True # SECTION

def _Paragraphs_Paragraph(node, path, attrs):
    pass

def _Paragraph_Sentence(node, path, attrs):

    for subnode in _mark_subnodes(node, path, attrs):
        if subnode.name == "ParagraphName":
            _mark_subtree(subnode)
        elif subnode.name in ("Sentence", "AlteredGoTo"):
            continue
        else:
            import pdb; pdb.set_trace()

def _Sentence_Statement(node, path, attrs):
    for subnode in node.subnodes:
        if subnode.name != 'Statement':
            subnode.knode = True

def _DataDivision_DataDivisionSection(node, path, attrs):

    for subnode in _mark_subnodes(node, path, attrs):
        pass

def _WorkingStorageSection_DataDescriptionEntry(node, path, attrs):

    for subnode in _mark_subnodes(node, path, attrs):
        pass

def _DataDescriptionEntryFormat1_DataName(node, path, attrs):

    for subnode in _mark_subnodes(node, path, attrs):

        if subnode.name in ('DataPictureClause', 'DataValueClause'):
            _mark_subtree(subnode)
        else:
            import pdb; pdb.set_trace()

def _CobolWord_terminal(node, path, attrs):

    for subnode in node.subnodes:
        if subnode is path[-1]: continue

        if subnode.name in ('hidden', ) or \
            subnode.token in (node.tokenmap['DOT_FS'], ):
            subnode.knode = True
            continue

        import pdb; pdb.set_trace()

_operators = {

#    #### IdentificationDivision ####
#
#    'frame_IdentificationDivision': {
#        'IDENTIFICATION': _break,
#    },
#
#    'frame_ProgramIdParagraph': {
#        'PROGRAM_ID': _break,
#        'ProgramName': (_add_name, _break),
#    },
#
#    'frame_ProgramName': {
#        'CobolWord': (_collect_name, _continue),
#    },
#
    #### DataDivision ####

    'frame_DataDivision': {
        'DataDivisionSection': (_mark, _check),
    },

    'frame_DataDivisionSection': {
        'WorkingStorageSection': (_mark, _check),
    },

    'frame_WorkingStorageSection': {
        'DataDescriptionEntry': (_mark, _check),
    },

    'frame_DataDescriptionEntry': {
        'DataDescriptionEntryFormat1': (_mark, _check),
    },

    'frame_DataDescriptionEntryFormat1': {
#        'INTEGERLITERAL': _break,
        'DataName': (_mark, _check),
    },

    'frame_DataName': {
        'CobolWord': (_mark, _check),
    },
#
#    'frame_DataPictureClause': {
#        'PIC': _break,
#    },
#
#    'frame_DataValueClause': {
#        'VALUE': _break,
#    },
#
#    'frame_PictureChars': {
#        'IDENTIFIER': _break,
#        'LPARENCHAR': _break,
#        'RPARENCHAR': _break,
#    },
#
#    #### ProcedureDivision ####

# NOTE: add terminal on non-terminal node that HAS the terminal node
# TODO: assign callback with Node name and if mathced node name, run the callback

    'frame_ProcedureDivision': {
        'ProcedureDivisionBody': (_mark, _check),
    },


    'frame_ProcedureDivisionBody': {
        'Paragraphs': (_mark, _check),
        'ProcedureSection': (_mark, _check),
    },

    'frame_ProcedureSection': {
        'Paragraphs': (_mark, _check),
        'ProcedureSectionHeader': (_mark, _check),
    },

    'frame_ProcedureSectionHeader': {
        'SectionName': (_mark, _check),
        'IntegerLiteral': (_mark, _check),
    },

    'frame_Paragraph': {
        'Sentence': (_mark, _check),
    },

    'frame_PerformStatement': {
        'PERFORM': (_mark, _check),
    },

    'frame_PerformProcedureStatement': {
        'ProcedureName': (_mark, _check),
        'PerformType': (_mark, _check),
    },

    'frame_DisplayStatement': {
        'DISPLAY': (_mark, _check),
    },
#
#    'frame_GobackStatement': {
#        'GOBACK': _break,
#    },
#
    'frame_PerformInlineStatement': {
        'PerformType': (_mark, _check),
        'END_PERFORM': (_mark, _check),
    },

    'frame_DisplayOperand': {
        'Identifier': (_mark, _check),
    },

    'frame_QualifiedDataName': {
        'QualifiedDataNameFormat1': (_mark, _check),
    },

    'frame_QualifiedDataNameFormat1': {
        'DataName': (_mark, _check),
    },

    'frame_PerformType': {
        'PerformVarying': (_mark, _check),
    },

    'frame_PerformVarying': {
        'PerformVaryingClause': (_mark, _check),
    },

    'frame_PerformVaryingClause': {
        'VARYING': (_mark, _check),
    },

    'frame_PerformVaryingPhrase': {
        'Identifier': (_mark, _check),
    },

    'frame_PerformFrom': {
        'FROM': (_mark, _check),
    },

    'frame_PerformBy': {
        'BY': (_mark, _check),
    },

    'frame_PerformUntil': {
        'UNTIL': (_mark, _check),
    },

    'frame_ProcedureName': {
        'ParagraphName': (_mark, _check),
        'InSection': (_mark, _check),
        'SectionName': (_mark, _check),
    },

    #### Common ####

    'frame_root': {
        'RunUnit': (_mark, _check),
    },

    'frame_RunUnit': {
        'CompilationUnit': (_mark, _check),
    },

    'frame_CompilationUnit': {
        'ProgramUnit': (_mark, _check),
    },

    'frame_ProgramUnit': {
        'ProcedureDivision': (_mark, _check),
    },


    'frame_Paragraphs': {
        'Paragraph': (_mark, _check),
        'Sentence': (_mark, _check),
    },

    'frame_Paragraph': {
        'Sentence': (_mark, _check),
    },

    'frame_Sentence': {
        'Statement': (_mark, _goback_stmt, _move_dotfs, _check),
    },

    'frame_Statement': {
        'PerformStatement': (_mark, _check),
        'DisplayStatement': (_mark, _check),
    },

    'frame_RelationalOperator': {
        'MORETHANCHAR': (_mark, _check),
    },

    'frame_Condition': {
        'CombinableCondition': (_mark, _check),
    },

    'frame_CombinableCondition': {
        'SimpleCondition': (_mark, _check),
    },

    'frame_SimpleCondition': {
        'RelationCondition': (_mark, _check),
    },

    'frame_RelationCondition': {
        'RelationArithmeticComparison': (_mark, _check),
    },

    'frame_RelationArithmeticComparison': {
        'ArithmeticExpression': (_mark, _check),
    },

    'frame_Length': {
        'ArithmeticExpression': (_mark, _check),
    },

    'frame_CharacterPosition': {
        'ArithmeticExpression': (_mark, _check),
    },

    'frame_ArithmeticExpression': {
        'MultDivs': (_mark, _check),
    },

    'frame_MultDivs': {
        'Powers': (_mark, _check),
    },

    'frame_Powers': {
        'Basis': (_mark, _check),
    },

    'frame_Basis': {
        'Identifier': (_mark, _check),
        'Literal': (_mark, _check),
    },

    'frame_SectionName': {
        'CobolWord': (_mark, _check),
        'IntegerLiteral': (_mark, _check),
    },

    'frame_ParagraphName': {
        'CobolWord': (_mark, _check),
        'IntegerLiteral': (_mark, _check),
    },

    'frame_Identifier': {
        'QualifiedDataName': (_mark, _check),
        'TableCall': (_mark, _check),
    },

    'frame_TableCall': {
        'QualifiedDataName': (_mark, _check),
    },

    'frame_ReferenceModifier': {
        'LPARENCHAR': (_mark, _check),
        'RPARENCHAR': (_mark, _check),
        'COLONCHAR': (_mark, _check),
    },

    'frame_Literal': {
        'NumericLiteral': (_mark, _check),
    },

    'frame_NumericLiteral': {
        'IntegerLiteral': (_mark, _check),
    },

    'frame_IntegerLiteral': {
        'INTEGERLITERAL': (_mark, _check),
    },

    'frame_CobolWord': {
        'IDENTIFIER': (_mark, _check),
    },
}

def pre_assemble(node, basket):

    tokenmap = node.tokenmap

    node.root.revtokenmap = node.rtokenmap

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

def post_assemble(node, basket):
    entry_node = basket['entry_node']
    del entry_node.root.operators
    del entry_node.root.revtokenmap
    return node

def assemble(node, basket):

    node.knode = True

    if node.name == 'hidden':
        return

    if node.name == 'terminal':

        if node.text in _debug_texts:
            import pdb; pdb.set_trace()

        path = [node]
        node = node.uppernode

        task_attrs = {}
        task_result = {}
        for task in assemble_tasks:
            task_attrs[task] = {}
            task_result[task] = None


        while node is not None:

            for task in assemble_tasks:
                if task_result[task] is False:
                    continue
                rulename = task + '_' + node.name

                if rulename not in node.root.operators:
                    exit(exitno=1, msg='Assembler rule key, "%s", is not found.'%rulename)

                subrules = node.root.operators[rulename]

                assembler_name = "_%s_%s"%(node.name, path[-1].name)
                if assembler_name in globals():
                    task_result[task] = globals()[assembler_name](node, path, task_attrs[task])

                if path[-1].name == 'terminal':

                    if path[-1].token not in subrules:
                        exit(exitno=1, msg='Assembler subrule token, "%s / %s",'
                        ' is not found.'%(rulename, node.root.revtokenmap[path[-1].token]))
                    try:
                        for func in subrules[path[-1].token]:
                            task_result[task] = func(node, path, task_attrs[task])
                    except TypeError:
                        task_result[task] = subrules[path[-1].token](node, path, task_attrs[task])

                else:

                    if path[-1].name not in subrules:
                        exit(exitno=1, msg='Assembler subrule name, "%s / %s", '
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

def prune(node, basket):
    #node.subnodes = [prune(snode, basket) for snode in node.subnodes
    #    if snode.knode is True or snode.name == 'hidden']
    node.subnodes = [prune(s, basket) for s in node.subnodes if s.knode is True]

    return node
