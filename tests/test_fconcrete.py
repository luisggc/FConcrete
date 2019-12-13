#!/usr/bin/env python

"""Tests for `fconcrete` package."""


import unittest
from click.testing import CliRunner

from fconcrete import fconcrete
from fconcrete import cli


class TestFconcrete(unittest.TestCase):
    """Tests for `fconcrete` package."""

    def test_structural_shear_diagram(self):
        """Test Shear Diagram"""


    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'fconcrete.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
