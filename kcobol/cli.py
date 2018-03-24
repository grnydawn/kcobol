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
        ctx.params['subcommand'] = ctx.invoked_subcommand
        initialize_logging(ctx.params[u'output'])
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

    logging.info("Starting extract")
    retcode = on_extract_command(ctx.params)
    logging.info("Exiting extract")

    return retcode

main.add_command(extract)

if __name__ == u"__main__":
    sys.exit(main())  # pragma: no cover
