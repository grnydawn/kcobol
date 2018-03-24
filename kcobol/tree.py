# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *
from collections import OrderedDict
from stemtree import Node


class SourceLineTree(Node):

    def __init__(self, path):
        super(self.__class__, self).__init__(attr_factory=OrderedDict)
        self.name = path

        with open(path) as f:
            for i, line in enumerate(f):
                node = Node(attr_factory=OrderedDict)
                node.line = line
                node.lineno = i
                node.name = str(i+1)
                self.add_subnode(node)
