# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

from .config import config
from .util import runcmd

def survey_application():

    # clean
    for line in runcmd(config['opts/extract/clean']):
        pass

    # build under inspection

    pass

