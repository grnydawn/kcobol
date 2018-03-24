#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `kcobol` package."""

import pytest

from click.testing import CliRunner

from kcobol import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


#def test_content(response):
#    """Sample pytest test function with the pytest fixture as an argument."""
#    # from bs4 import BeautifulSoup
#    # assert 'GitHub' in BeautifulSoup(response.content).title.string
#    output = hello('Peter')
#    assert 'Hello Peter' in output


#def test_command_line_interface():
#    """Test the CLI."""
#    runner = CliRunner()
#    result = runner.invoke(cli.main, ['Peter'])
#    assert result.exit_code == 0
#    assert 'Hello Peter' in result.output
#    help_result = runner.invoke(cli.main, ['--help'])
#    assert help_result.exit_code == 0
#    assert 'Console script for kcobol.' in help_result.output

def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['extract', 'targetfile'])
    assert result.exit_code == 0
