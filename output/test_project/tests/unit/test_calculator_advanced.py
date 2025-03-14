"""
Advanced unit tests for Calculator class functionality.
"""

import pytest
import math
from calculator.calculator import Calculator, parse_expression

@pytest.mark.unit
class TestAdvancedCalculator:
    """Test advanced calculator features."""
    
    def test_init_with_value(self):
        """Test initialization with a specific value."""
        calc = Calculator(10.5)
        assert calc.result == 10.5
    
    def test_power(self):
        """Test power operation."""
        calc = Calculator(2)
        result = calc.power(3)
        assert result == 8
        assert calc.result == 8
    
    def test_power_negative_exponent(self):
        """Test power with negative exponent."""
        calc = Calculator(2)
        result = calc.power(-1)
        assert result == 0.5
        assert calc.result == 0.5
    
    def test_square_root(self):
        """Test square root operation."""
        calc = Calculator(16)
        result = calc.square_root()
        assert result == 4
        assert calc.result == 4
    
    def test_square_root_of_negative(self):
        """Test square root of negative value raises ValueError."""
        calc = Calculator(-1)
        with pytest.raises(ValueError) as excinfo:
            calc.square_root()
        assert "Cannot calculate square root of a negative number" in str(excinfo.value)
    
    def test_memory_features(self):
        """Test memory store, recall, add, and clear operations."""
        calc = Calculator(10)
        # Test memory store
        calc.memory_store()
        assert calc.memory == 10
        
        # Test memory recall
        memory_value = calc.memory_recall()
        assert memory_value == 10
        
        # Test memory add
        calc.add(5)  # result is now 15
        calc.memory_add()
        assert calc.memory == 25  # 10 + 15
        
        # Test memory clear
        calc.memory_clear()
        assert calc.memory == 0
    
    def test_clear(self):
        """Test clear operation."""
        calc = Calculator(10)
        calc.clear()
        assert calc.result == 0
    
    def test_history(self):
        """Test operation history recording."""
        calc = Calculator(5)
        calc.add(3)
        calc.multiply(2)
        calc.subtract(1)
        
        history = calc.get_history()
        
        # Check we have 4 operations (init, add, multiply, subtract)
        assert len(history) == 4
        
        # Check the last operation was subtract
        assert history[-1]["operation"] == "subtract"
        assert history[-1]["value"] == 1
        assert history[-1]["result"] == 15  # (5+3)*2-1 = 15
    
    def test_evaluate_simple_expression(self):
        """Test evaluating simple expressions."""
        calc = Calculator()
        result = calc.evaluate("2 + 3 * 4")
        assert result == 14
        assert calc.result == 14
    
    def test_evaluate_with_parentheses(self):
        """Test evaluating expressions with parentheses."""
        calc = Calculator()
        result = calc.evaluate("(2 + 3) * 4")
        assert result == 20
        assert calc.result == 20
    
    def test_evaluate_invalid_expression(self):
        """Test evaluating invalid expressions raises ValueError."""
        calc = Calculator()
        with pytest.raises(ValueError):
            calc.evaluate("2 + * 4")
    
    def test_evaluate_with_disallowed_chars(self):
        """Test evaluating expressions with disallowed characters raises ValueError."""
        calc = Calculator()
        with pytest.raises(ValueError):
            calc.evaluate("__import__('os').system('ls')")
    
    def test_parse_expression_basic(self):
        """Test parse_expression function with basic operations."""
        assert parse_expression("2+3") == 5
        assert parse_expression("10-4") == 6
        assert parse_expression("3*7") == 21
        assert parse_expression("20/5") == 4
    
    def test_parse_expression_complex(self):
        """Test parse_expression function with complex expressions."""
        assert parse_expression("2+3*4") == 14
        assert parse_expression("(2+3)*4") == 20
        assert parse_expression("2+3*4-1") == 13
        assert parse_expression("10/2+5*3") == 20
    
    def test_parse_expression_with_spaces(self):
        """Test parse_expression function with spaces in expression."""
        assert parse_expression("2 + 3") == 5
        assert parse_expression(" 10 - 4 ") == 6
    
    def test_parse_expression_divide_by_zero(self):
        """Test parse_expression function with division by zero."""
        with pytest.raises(ZeroDivisionError):
            parse_expression("10/0")
    
    def test_parse_expression_invalid(self):
        """Test parse_expression function with invalid expressions."""
        with pytest.raises(ValueError):
            parse_expression("2+*3")
    
    def test_chained_advanced_operations(self):
        """Test a complex chain of operations."""
        calc = Calculator()
        calc.add(10)         # result = 10
        calc.power(2)        # result = 100
        calc.memory_store()  # memory = 100
        calc.divide(4)       # result = 25
        calc.square_root()   # result = 5
        calc.add(3)          # result = 8
        calc.memory_add()    # memory = 108
        
        assert calc.result == 8
        assert calc.memory == 108
        
        calc.memory_recall() # doesn't change result
        assert calc.result == 8
        
        history = calc.get_history()
        assert len(history) == 9  # init, add, power, m_store, divide, sqrt, add, m_add, m_recall
        
        calc.evaluate("(5+3)*2")  # result = 16
        assert calc.result == 16
        
        calc.clear()
        assert calc.result == 0
        
        # Final history should have 11 operations
        history = calc.get_history()
        assert len(history) == 11