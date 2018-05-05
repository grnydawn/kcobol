# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

import logging

"""KCobol Exception module."""

class KCobolException(Exception):

    def __init__(self, msg):
        logging.debug(msg)
        super(KCobolException, self).__init__(msg)

class UsageError(KCobolException):
    pass


class InternalError(KCobolException):
    pass


#class ResolveError(InternalError):
#    def __init__(self, org, node):
#
#        nodename = getattr(node, 'name', 'Node')
#        nodetext = getattr(node, 'text', '')
#        orgname = getattr(org, 'name', 'Node')
#        orgtext = getattr(org, 'text', '')
#
#        _node = '%s(%s)'%(nodename, nodetext)
#        _org = '%s(%s)'%(orgname, orgtext)
#
#        _msg = '%s can not resolve "%s" request.' % (_node, _org)
#
#        super(InternalError, self).__init__(_msg)

class SearchError(InternalError):

    def __init__(self, org, node):

        nodename = getattr(node, 'name', 'Node')
        nodetext = getattr(node, 'text', '')
        orgname = getattr(org, 'name', 'Node')
        orgtext = getattr(org, 'text', '')

        _node = '%s(%s)'%(nodename, nodetext)
        _org = '%s(%s)'%(orgname, orgtext)

        _msg = '%s can not search "%s".' % (_node, _org)

        super(InternalError, self).__init__(_msg)

class ResolveError(InternalError):

    def __init__(self, node):

        _msg = 'resolve_%s() is not implemented.' % node.name

        super(InternalError, self).__init__(_msg)

class AnalyzeError(InternalError):

    def __init__(self, node):

        _msg = 'analyze_%s() is not implemented.' % node.name

        super(InternalError, self).__init__(_msg)


class AssembleError(InternalError):

    def __init__(self, node):

        _msg = 'assemble_%s() is not implemented.' % node.name

        super(InternalError, self).__init__(_msg)

