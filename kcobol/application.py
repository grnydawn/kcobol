# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

import os
import re
import logging

from .config import config
from .compiler import get_compiler
from .util import runcmd, hash_sha1, istext

_pid_re = re.compile(r'(?P<pid>\d+)')
_exitno_re = re.compile(r'(?P<exitno>\d+)')
_read_re = re.compile(r'\d+<(?P<path>[^<]+)>')

def _get_pid(line):
    pid_search = _pid_re.search(line)
    if pid_search:
        return pid_search.group('pid')
    return None

def _get_exitno(line):
    exitno_match = _exitno_re.match(line.lstrip())
    if exitno_match:
        return exitno_match.group('exitno')
    return '-1'

def survey_application_strace():

    logging.debug('Entering "survey_application_strace"')

    # clean
    for line in runcmd(config['opts/extract/clean']):
        pass

    # build under inspection

    syscalls = ('execve', 'read', 'write')
    unfinished = {}
    finished ={}

    # TODO: use cache in project directory

    strace_cmd = 'strace -y -f -q -s 100000 -e trace='+','.join(syscalls)+' -v -- $SHELL -c "%s"'
    for line in runcmd(strace_cmd%config['opts/extract/build']):

        # check killed
        pos_killed = line.find("killed by")
        if pos_killed > 0:
            # stop processing
            logging.debug('strace: killed')
            break

        # check unfinished
        pos_unfinished = line.rfind("<unfinished ...>")
        if pos_unfinished > 0:
            pid = _get_pid(line[:pos_unfinished])
            if pid:
                if pid not in unfinished:
                    unfinished[pid] = {}
                piddict = unfinished[pid]
                for syscall in syscalls:
                    pos_syscall = line.find(syscall)
                    if pos_syscall > 0:
                        if syscall in piddict:
                            logging.debug('strace: dupulicated %s in buffer.'%syscall)
                        else:
                            piddict[syscall] = line[:pos_unfinished]
                        break
            else:
                logging.debug('strace: no pid is found.')
            continue

        # check resumed
        pos_resumed = line.find("resumed>")
        if pos_resumed > 0:
            pid = _get_pid(line[:pos_resumed])
            if pid:
                if pid not in unfinished:
                    logging.debug('strace: pid is not found.')
                    continue
                piddict = unfinished[pid]
                for syscall in syscalls:
                    pos_syscall = line.find(syscall)
                    if pos_syscall > 0:
                        if syscall in piddict:
                            line = piddict[syscall]+line[pos_resumed+8:]
                            del piddict[syscall]
                        else:
                            logging.debug('strace: no unfinished for %s'%syscall)
                            line = ''
            else:
                logging.debug('strace: no pid is found.')
                line = ''

        # process line
        pos_execve = line.find("execve")
        pos_read = line.find("read")
        pos_write = line.find("write")
        if pos_execve > 0 or pos_read > 0 or pos_write > 0:
            exitno = '-1'
            pos_equal = line.rfind("=")
            if pos_equal > 0:
                exitno = _get_exitno(line[pos_equal+1:])

            if exitno == '0':
                try:
                    if pos_execve > 0:
                        cmd, args, envs = eval(line[pos_execve+6:pos_equal])

                        # get $PWD
                        pwd = None
                        for env in envs:
                            if env.startswith("PWD="):
                                pwd = env[4:]
                                break

                        path, name = os.path.split(cmd)
                        if name == args[0]:
                            # get compiler
                            compiler = get_compiler(cmd, pwd, args)

                            if compiler is not None:
                                config['strace/compile/source/%s'%compiler.source] = compiler
                    elif pos_write > 0:
                        logging.debug(line)
                        import pdb; pdb.set_trace()

                    elif pos_read > 0:
                        match = _read_re.match(line[pos_read+5:pos_equal])
                        if match:
                            path = match.group('path')
                            if all(not path.startswith(p) for p in ('/etc', '/usr', '/tmp', 'pipe')):
                                if istext(path):
                                    with open(path, 'r') as f:
                                        content = f.read()
                                else:
                                    with open(path, 'rb') as f:
                                        content = f.read()
                                config['strace/compile/read/%s'%match.group('path')] = hash_sha1(content)
                        #logging.debug(line)

                except Exception as e:
                    logging.debug(str(e))
                    import pdb; pdb.set_trace()

    #import pdb; pdb.set_trace()
    logging.debug('Leaving "survey_application_strace"')
