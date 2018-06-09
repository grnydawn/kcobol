# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

import os
import re
import logging
import tempfile
import platform
import datetime
import time
import math
import pickle

from .config import config
from .compiler import get_compiler
from .project import _write_project
from .util import runcmd, hash_sha1, istext

_sysname = platform.system()

_pid_re = re.compile(r'(?P<pid>\d+)')
_exitno_re = re.compile(r'(?P<exitno>\d+)')
_iopath_re = re.compile(r'\d+<(?P<path>[^<]+)>')
_dirpath_re = re.compile(r'"(?P<path>[^"]+)"')
_unlinkat_re = re.compile(r'(?P<args>[^\)]+)\)')

_tempdirs = {
    'Linux': ('/tmp', '/var/tmp', '/usr/tmp'),
    'Windows': ('C:\TEMP', 'C:\TMP', '\TEMP', '\TMP'),
    'Darwin': ('/tmp',),
}

tempdirs = set(os.environ[var] for var in ('TMPDIR', 'TEMP', 'TMP') if var in os.environ)
tempdirs |= set(_tempdirs.get(_sysname, ('/tmp',)))
tempdirs.add(tempfile.gettempdir())

_sysdirs = {
    'Linux': ('/etc', '/usr', '/tmp', 'pipe', '/opt', '/bin'),
    'Windows': tuple(),
    'Darwin': tuple(),
}

_syscalls = {
    'Linux': ('execve', 'read', 'write', 'unlink', 'unlinkat', 'chdir'),
    'Windows': tuple(),
    'Darwin': tuple(),
}

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

def _file_sha1(path):
    if istext(path):
        with open(path, 'r') as f:
            content = f.read()
    else:
        with open(path, 'rb') as f:
            content = f.read()
    return hash_sha1(content)

def _strace_run(cmd):

    syscalls = _syscalls[_sysname]
    sysdirs = _sysdirs[_sysname]

    unfinished = {}
    finished ={}

    curdirs = [os.getcwd()]

    strace_cmd = 'strace -y -f -q -s 100000 -e trace=' + \
        ','.join(syscalls)+' -v -- $SHELL -c "%s"'%cmd

    for line in runcmd(strace_cmd):

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
        pos_syscall = {}
        for syscall in syscalls:
            pos_syscall[syscall] = line.find(syscall+"(")

        if reduce( lambda x, y: x + 1 if y>=0 else x, [0]+pos_syscall.values()) > 1:
            import pdb; pdb.set_trace()

        exitno = '-1'
        pos_equal = line.rfind("=")
        if pos_equal > 0:
            exitno = _get_exitno(line[pos_equal+1:])

        for syscall, pos in pos_syscall.items():

            if syscall == "execve" and exitno == "0" and pos >= 0:
                cmd, args, envs = eval(line[pos+6:pos_equal])
                yield syscall, cmd, args[1:], curdirs[-1]

            elif syscall == "read" and exitno == "0" and pos >= 0:

                match = _iopath_re.match(line[pos+5:pos_equal])
                if match:
                    path = match.group('path')
                    if all(not path.startswith(p) for p in sysdirs):
                        yield syscall, path, _file_sha1(path), curdirs[-1]

            elif syscall == "write" and pos >= 0:
                match = _iopath_re.match(line[pos+6:])
                if match:
                    path = match.group('path')
                    if os.path.exists(path) and all( not path.startswith(t) for t in tempdirs):
                        mtime = os.path.getmtime(path)
                        dtime = datetime.datetime.fromtimestamp(mtime)
                        subsec = "{:.6f}".format(mtime-math.floor(mtime)).lstrip("0")
                        yield syscall, path, dtime.strftime('%Y-%m-%d %H:%M:%S')+subsec, curdirs[-1]

            elif syscall == "unlink" and exitno == "0" and pos >= 0:
                match = _dirpath_re.match(line[pos+7:])
                if match:
                    path = match.group('path')
                    if all( not path.startswith(t) for t in tempdirs):
                        yield syscall, path, str(datetime.datetime.now()), curdirs[-1]

            elif syscall == "unlinkat" and exitno == "0" and pos >= 0:
                match = _unlinkat_re.match(line[pos+9:])
                if match:
                    args = match.group('args')
                    _, path, _ = args.split(',')
                    path = eval(path)
                    if all( not path.startswith(t) for t in tempdirs):
                        yield syscall, path, str(datetime.datetime.now()), curdirs[-1]

            elif syscall == "chdir" and exitno == "0" and pos >= 0:
                match = _dirpath_re.match(line[pos+6:])
                if match:
                    curdirs.append(match.group('path'))

def survey_application_strace():

    logging.debug('Entering "survey_application_strace"')

    changed = [_file_sha1(path) != sha1 for path, sha1 in \
        config.get_subitems('prjconfig/build/read')]

    # clean
    for line in runcmd(config['opts/extract/clean']):
        pass

    changed = []

    if len(changed) == 0 or any(changed):

        # build: read, write
        for syscall, attr, value, pwd in _strace_run(config['opts/extract/build']):
            path = os.path.normpath(os.path.join(pwd, attr))
            config['strace/build/%s/%s'%(syscall, path)] = value
            if syscall == 'read':
                config['prjconfig/build/read/'+path] = value
            elif syscall == 'write':
                config['prjconfig/build/write/'+path] = value
                if 'prjconfig/build/read/'+path in config:
                    del config['prjconfig/build/read/'+path]
            elif syscall in ('execve',):
                compiler = get_compiler(path, pwd, value)
                if compiler is not None and compiler.source is not None:
                    config['strace/build/compiler/%s'%compiler.source] = compiler
                    pickle_path = os.path.join(config['project/topdir'], hash_sha1(compiler.source))
                    with open(pickle_path,'wb') as f:
                        pickle.dump(compiler, f)
                    config['prjconfig/build/compiler/%s'%compiler.source] = pickle_path

        # run: execve
        for syscall, attr, value, pwd in _strace_run(config['opts/extract/run']):
            path = os.path.normpath(os.path.join(pwd, attr))
            config['strace/run/%s/%s'%(syscall, path)] = value
            if syscall in ('execve',):
                for k, v in config.get_subitems('prjconfig/build/write'):
                    if path == k:
                        config['prjconfig/run/%s/%s'%(syscall, path)] = v
                        break

        # clean: unlink, unlinkat
        for syscall, attr, value, pwd in _strace_run(config['opts/extract/clean']):
            config['strace/clean/%s/%s'%(syscall, attr)] = value
            if syscall in ('unlink', 'unlinkat'):
                path = os.path.normpath(os.path.join(pwd, attr))
                config['prjconfig/clean/unlink/%s'%path] = value

        # find an executable target
        # TODO: may or many not need to analyze linker command
        items = dict(item for item in config.get_subitems('prjconfig/run/execve'))
        if len(items) > 1:
            for key in config.get_subitems('prjconfig/clean/unlink'):
                if key in items:
                    del items[key]
        if len(items) == 1:
            keys = list(items)
            config['prjconfig/run/target/'+keys[0]] = items[keys[0]]
        else:
            import pdb; pdb.set_trace()

        prjdir = config['project/topdir']
        _write_project(prjdir)

    logging.debug('Leaving "survey_application_strace"')
