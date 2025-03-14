"""
Integration tests for the CLI module.
Test the interaction between CLI and Calculator modules.
"""

import pytest
import io
import sys
from unittest.mock import patch
from calculator.cli import main

@pytest.mark.integration
class TestCliIntegration:
    """Test CLI integration with Calculator functionality."""

    def test_add_command(self):
        """Test 'add' command calls add_numbers and prints correct result."""
        with patch.object(sys, 'argv', ['calculator', 'add', '5', '3']):
            with patch('sys.stdout', new=io.StringIO()) as fake_output:
                assert main() == 0
                assert fake_output.getvalue().strip() == "5.0 + 3.0 = 8.0"

    def test_subtract_command(self):
        """Test 'subtract' command uses Calculator and prints correct result."""
        with patch.object(sys, 'argv', ['calculator', 'subtract', '10', '4']):
            with patch('sys.stdout', new=io.StringIO()) as fake_output:
                assert main() == 0
                assert fake_output.getvalue().strip() == "10.0 - 4.0 = 6.0"

    def test_multiply_command(self):
        """Test 'multiply' command uses Calculator and prints correct result."""
        with patch.object(sys, 'argv', ['calculator', 'multiply', '6', '7']):
            with patch('sys.stdout', new=io.StringIO()) as fake_output:
                assert main() == 0
                assert fake_output.getvalue().strip() == "6.0 * 7.0 = 42.0"

    def test_divide_command(self):
        """Test 'divide' command uses Calculator and prints correct result."""
        with patch.object(sys, 'argv', ['calculator', 'divide', '20', '5']):
            with patch('sys.stdout', new=io.StringIO()) as fake_output:
                assert main() == 0
                assert fake_output.getvalue().strip() == "20.0 / 5.0 = 4.0"

    def test_divide_by_zero(self):
        """Test 'divide' command handles division by zero correctly."""
        with patch.object(sys, 'argv', ['calculator', 'divide', '10', '0']):
            with patch('sys.stdout', new=io.StringIO()) as fake_output:
                assert main() == 1
                assert "Error: Cannot divide by zero" in fake_output.getvalue()

    def test_no_command_shows_help(self):
        """Test no command displays help and hello message."""
        with patch.object(sys, 'argv', ['calculator']):
            with patch('sys.stdout', new=io.StringIO()) as fake_output:
                with patch('calculator.cli.hello_world') as mock_hello:
                    assert main() == 0
                    mock_hello.assert_called_once()
                    assert "usage:" in fake_output.getvalue()