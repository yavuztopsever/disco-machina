"""
Unit tests for the add_numbers function.
"""

import pytest
from calculator import add_numbers

@pytest.mark.unit
class TestAddNumbers:
    """Test cases for the add_numbers function."""
    
    def test_add_positive_numbers(self):
        """Test adding two positive numbers."""
        assert add_numbers(1, 2) == 3
    
    def test_add_negative_numbers(self):
        """Test adding two negative numbers."""
        assert add_numbers(-1, -2) == -3
    
    def test_add_mixed_numbers(self):
        """Test adding positive and negative numbers."""
        assert add_numbers(5, -3) == 2
        assert add_numbers(-5, 8) == 3
    
    def test_add_zero(self):
        """Test adding zero to a number."""
        assert add_numbers(10, 0) == 10
        assert add_numbers(0, 10) == 10
        assert add_numbers(0, 0) == 0
    
    def test_add_floats(self):
        """Test adding floating point numbers."""
        assert add_numbers(1.5, 2.5) == 4.0
        # Test for floating point precision
        assert abs(add_numbers(0.1, 0.2) - 0.3) < 1e-10
    
    @pytest.mark.parametrize("a, b, expected", [
        (1, 1, 2),
        (100, 200, 300),
        (-5, -10, -15),
        (0.5, 0.5, 1.0),
    ])
    def test_add_numbers_parametrized(self, a, b, expected):
        """Test addition with parametrized test cases."""
        assert add_numbers(a, b) == expected