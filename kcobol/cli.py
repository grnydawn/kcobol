# -*- coding: utf-8 -*-

"""Console script for kcobol."""
from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

import sys
import os
import click
import logging

from .kcobol import on_main_command, on_extract_command
from .project import initialize_project
from .util import initialize_logging
from .exception import InternalError, UsageError
from contextlib import contextmanager


@contextmanager
def command_context():
        try:
            yield
        except InternalError as err:
            logging.critical(str(err))
        except UsageError as err:
            click.echo(main.get_help(ctx))
            logging.critical(str(err))
        except Exception as err:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            tb_back = exc_tb
            tb = exc_tb
            while tb.tb_next is not None:
                tb_back = tb
                tb = tb.tb_next
            fname_back = os.path.split(tb_back.tb_frame.f_code.co_filename)[1]
            fname = os.path.split(tb.tb_frame.f_code.co_filename)[1]
            logging.critical("[%s:%d<--%s:%d %s]  %s"%(fname, tb.tb_lineno,
                fname_back, tb_back.tb_lineno, exc_type.__name__, str(exc_obj)))
            sys.exit(-1)



@click.group(invoke_without_command=True)
@click.option(u'--debug/--no-debug', default=False)
@click.option(u'--output', u'-o', default=os.getcwd(),
    metavar=u'<outputpath>', type=str, help=u'output directory')
@click.pass_context
def main(ctx, debug, output):
    """main entry for kcobol commands."""

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
    else:

        with command_context():
            ctx.params['subcommand'] = subcmd = ctx.invoked_subcommand
            outdir = ctx.params[u'output']
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            initialize_logging(outdir)
            logging.info('==== Starting %s ====' % subcmd)
            retcode = on_main_command(ctx.params)
            if retcode == 0:
                initialize_project()
            return retcode


@click.command()
@click.argument(u'target', default=None, type=str,
    metavar=u'<filepath>[:<namepath>][:<lineno>-<lineno>]')
@click.option(u'--clean', default=None, type=str,
    metavar=u'<command>', help=u'clean command')
@click.option(u'--build', default=None, type=str,
    metavar=u'<command>', help=u'build command')
@click.option(u'--run', default=None, type=str,
    metavar=u'  <command>', help=u'run command')
@click.pass_context
def extract(ctx, target, clean, build, run):
    """extract a kerel from Cobol source codes."""

    with command_context():
        return on_extract_command(ctx.params)

# subcommands
main.add_command(extract)

if __name__ == u"__main__":
    sys.exit(main())
