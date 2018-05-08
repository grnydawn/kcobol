#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `kcobol` package."""

import os
import pytest

from click.testing import CliRunner

from kcobol import cli

basedir = os.path.dirname(__file__)

# TODO: change srcdir to relative path, and output with temporary directory

srcdir = "%s/cobol/des"%basedir
output = "/home/youngsung/temp/kcoboltest/des"
source = "%s/testdes.cob"%srcdir
clean = "cd %s;make clean"%srcdir
build = "cd %s;make build"%srcdir
run = "cd %s;make run"%srcdir

def test_extract():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ["-o", output, 'extract', source,
        "--clean", clean, "--build", build, "--run", run])
    assert result.exit_code == 0

