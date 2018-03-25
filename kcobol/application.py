# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

import re
import logging

from .config import config
from .compiler import get_compiler
from .util import runcmd

_pid_re = re.compile(r'(?P<pid>\d+)')

def _get_pid(line):
    pid_search = _pid_re.search(line)
    if pid_search:
        return pid_search.group('pid')
    return None

def survey_application():

    logging.debug('Entering "survey_application"')

    # clean
    for line in runcmd(config['opts/extract/clean']):
        pass

    # build under inspection

    unfinished = {}
    finished ={}

    # TODO: use cache in project directory

    strace_cmd = 'strace -f -q -s 100000 -e trace=execve -v -- $SHELL -c "%s"'
    for line in runcmd(strace_cmd%config['opts/extract/build']):

        # check killed
        pos_killed = line.find("killed by")
        if pos_killed > 0:
            # stop processing
            import pdb; pdb.set_trace()
            continue

        # check unfinished
        pos_unfinished = line.rfind("<unfinished ...>")
        if pos_unfinished > 0:
            pos_execve = line.find("execve")
            if pos_execve > 0:
                pid = _get_pid(line[:pos_execve])
                if pid:
                    if pid in unfinished:
                        import pdb; pdb.set_trace()
                    else:
                        unfinished[pid] = line[:pos_unfinished]
                else:
                    import pdb; pdb.set_trace()
            continue

        # check resumed
        pos_resumed = line.find("resumed>")
        if pos_resumed > 0:
            pid = _get_pid(line[:pos_resumed])
            if pid:
                if pid in unfinished:
                    line = unfinished[pid]+line[pos_resumed+8:]
                    del unfinished[pid]
                else:
                    import pdb; pdb.set_trace()
                    line = ''
            else:
                import pdb; pdb.set_trace()
                line = ''

        # process line
        pos_execve = line.find("execve")
        if pos_execve > 0:
            pos_equal = line.rfind("=")

            cmd, args, envs = eval(line[pos_execve+6:pos_equal])

            # get $PWD
            pwd = None
            for env in envs:
                if env.startswith("PWD="):
                    pwd = env[4:]
                    break

            # get compiler
            compiler = get_compiler(cmd, pwd, args)

            if compiler is not None:
                config['strace/compile/%s'%compiler.source] = compiler

    logging.debug('Leaving "survey_application"')
