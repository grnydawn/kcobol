# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

"""Main module."""

import os
import re
import logging
import click
from stemtree import DFS_LF, UPWARDS, assemble_subtrees
from stemcobol import EOF
from .config import read_config, write_config, config
from .reader import (read_target, collect_kernel_statements, remove_eof,
    )
from .resolve import resolve, pre_resolve, post_resolve
from .analyze import analyze, pre_analysis, post_analysis
from .assemble import assemble, pre_assemble, post_assemble, prune
from .util import parse_kcobol_directive
from .exception import InternalError

def on_main_command(opts):
    logging.debug('Entering "on_main_command"')

    # save command-line options in config
    for k, v in opts.items():
        config[u'opts/main/%s'%k] = v

    # read configuration file
    read_config()

    logging.debug('Leaving "on_main_command"')
    return 0

def on_extract_command(opts):
    logging.debug('Entering "on_extract_command"')

    # save command-line options in config
    for k, v in opts.items():
        config[u'opts/extract/%s'%k] = v

    # read target source file
    tree = read_target()

    # collect kernel statements
    tree.setattr_shared('kernel_index', -1)
    tree.kcobol_group = []
    tree.kernel_group = []
    tree.kernel_flag = False
    tree.search(collect_kernel_statements, DFS_LF)
    del tree.kernel_flag

    # repeat per each kernel group
    for kidx in range(len(tree.kernel_group)):

        # clone parsed tree
        kernel_tree = tree.clone()

        # setup kernel values
        kcobol_directive = kernel_tree.kcobol_group[kidx]
        kernel_nodes = kernel_tree.kernel_group[kidx]
        kcobol_directive[1] = parse_kcobol_directive(kcobol_directive[1])
        kernel_name = kcobol_directive[1].get('name', str(kidx))

        if len(kernel_nodes) == 0: continue

        #kernel_tree.kcobol_directive = kcobol_directive # directives
        #kernel_tree.kernel_nodes = kernel_nodes         # kernel nodes
        #kernel_tree.resolve_paths = []                  # resolving paths
        #kernel_tree.is_modified = False                 # is modified?

        # analyze kernel tree
        # 1. construct namespaces
        basket = {}
        kernel_tree.search(analyze, DFS_LF, basket=basket, premove=pre_analysis,
            postmove=post_analysis)

        # resolve kernel nodes
        # 1. find resolving terminal nodes
        basket = {'unknowns': set(kernel_nodes), 'nodes': set()}
        pre_resolve(kernel_nodes[0], basket)
        while basket['unknowns']:
            knode = basket['unknowns'].pop()
            resolve(knode, basket)
        post_resolve(kernel_nodes[0], basket)

        # append resolving nodes to kernel nodes
        for n in basket['nodes']:
            if n not in kernel_nodes:
                kernel_nodes.append(n)

        # transform tree

        # assemble subtrees
        #subtrees = assemble_subtrees(kernel_nodes)

        # add frame nodes if needed


        kernel_tree.setattr_shared('knode', False)

        # assemble kernel nodes
        # 1. reconstruct a minimum cobol ast that contains kernel nodes
        basket = {}
        pre_assemble(kernel_nodes[0], basket)
        for knode in kernel_nodes:
            assemble(knode, basket)
        post_assemble(kernel_nodes[0], basket)

        # prune tree
        basket = {}
        prune(kernel_tree, basket)

        # write nodes into a file
        outfile = os.path.basename(config['opts/extract/target'])
        outdir = os.path.join(config['opts/main/output'], kernel_name)
        if not os.path.isdir(outdir):
            os.mkdir(outdir)
        outpath = os.path.join(outdir, outfile)

        with open(outpath, 'w') as f:
            f.write(kernel_tree.tocobol(revise=remove_eof))

    write_config()

    #import pdb; pdb.set_trace()
    logging.debug('Leaving "on_extract_command"')
    return 0


