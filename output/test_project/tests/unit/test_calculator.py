"""
Unit tests for the Calculator class.
"""

import pytest
from calculator import Calculator

@pytest.mark.unit
class TestCalculator:
    """Test cases for the Calculator class."""
    
    def test_initial_result(self, calculator):
        """Test initial result is zero."""
        assert calculator.result == 0
    
    def test_add(self, calculator):
        """Test add method."""
        # Add a positive number
        assert calculator.add(5) == 5
        # Add another positive number
        assert calculator.add(3) == 8
        # Add a negative number
        assert calculator.add(-10) == -2
    
    def test_subtract(self, calculator):
        """Test subtract method."""
        calculator.add(10)  # Set initial value
        # Subtract a positive number
        assert calculator.subtract(3) == 7
        # Subtract a negative number
        assert calculator.subtract(-5) == 12
    
    def test_multiply(self, calculator):
        """Test multiply method."""
        calculator.add(5)  # Set initial value
        # Multiply by a positive number
        assert calculator.multiply(3) == 15
        # Multiply by a negative number
        assert calculator.multiply(-2) == -30
        # Multiply by zero
        assert calculator.multiply(0) == 0
    
    def test_divide(self, calculator):
        """Test divide method."""
        calculator.add(10)  # Set initial value
        # Divide by a positive number
        assert calculator.divide(2) == 5
        # Divide by a negative number
        assert calculator.divide(-5) == -1
    
    def test_divide_by_zero(self, calculator):
        """Test division by zero raises an exception."""
        calculator.add(10)  # Set initial value
        with pytest.raises(ZeroDivisionError, match="Cannot divide by zero"):
            calculator.divide(0)
    
    def test_chained_operations(self, calculator):
        """Test chaining multiple operations."""
        # 0 + 5 = 5
        calculator.add(5)
        # 5 * 2 = 10
        calculator.multiply(2)
        # 10 - 3 = 7
        calculator.subtract(3)
        # 7 / 7 = 1
        calculator.divide(7)
        assert calculator.result == 1
    
    @pytest.mark.parametrize("operations,expected", [
        ([("+", 5), ("+", 3)], 8),
        ([("+", 5), ("-", 3)], 2),
        ([("+", 5), ("*", 3)], 15),
        ([("+", 6), ("/", 3)], 2),
        ([("+", 5), ("*", 2), ("-", 3), ("/", 7)], 1),
    ])
    def test_operations_parametrized(self, calculator, operations, expected):
        """Test operations with parametrized test cases."""
        for op, value in operations:
            if op == "+":
                calculator.add(value)
            elif op == "-":
                calculator.subtract(value)
            elif op == "*":
                calculator.multiply(value)
            elif op == "/":
                calculator.divide(value)
        
        assert calculator.result == expected