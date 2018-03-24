#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `kcobol` package."""

import pytest

from click.testing import CliRunner

from kcobol import cli

srcdir = "/home/youngsung/temp/cookiecutter_work/kcobol/tests/cobol/helloworld"
output = "/home/youngsung/temp/kcoboltest"
source = "%s/helloworld.cob"%srcdir
clean = "cd %s;make clean"%srcdir
build = "cd %s;make build"%srcdir
run = "cd %s;make run"%srcdir

def test_extract():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ["-o", output, 'extract', source,
        "--clean", clean, "--build", build, "--run", run])
    assert result.exit_code == 0

