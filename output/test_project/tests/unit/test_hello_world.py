"""
Unit tests for the hello_world function.
"""

import pytest
import io
import sys
from unittest.mock import patch
from calculator.calculator import hello_world

@pytest.mark.unit
def test_hello_world():
    """Test hello_world function prints the correct message."""
    with patch('sys.stdout', new=io.StringIO()) as fake_output:
        hello_world()
        assert fake_output.getvalue().strip() == "Hello, world!"