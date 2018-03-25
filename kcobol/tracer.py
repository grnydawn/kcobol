# -*- coding: utf-8 -*-

"""Console script for kcobol."""
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *


#strace -o $2 -f -q -s 100000 -e trace=execve -v -- /bin/sh -c "$1"
def parse_strace_execve(line):
    pass

