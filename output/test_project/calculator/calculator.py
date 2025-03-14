#!/usr/bin/env python3
"""
Advanced calculator implementation with various mathematical operations.
"""
import math
import re
from typing import Union, List, Tuple, Dict, Optional

def hello_world():
    """Print a greeting message"""
    print("Hello, world!")

def add_numbers(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Add two numbers together
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
    """
    return a + b

def parse_expression(expression: str) -> Union[float, str]:
    """Parse and evaluate a simple mathematical expression
    
    Args:
        expression: Mathematical expression as string (e.g., "2 + 3 * 4")
        
    Returns:
        Result of the evaluated expression
        
    Raises:
        ValueError: If the expression is invalid or contains unsupported operations
        ZeroDivisionError: If the expression attempts division by zero
    """
    # Security check - only allow basic arithmetic operations and numbers
    if not re.match(r'^[\d\s\+\-\*\/\(\)\.]+$', expression):
        raise ValueError("Expression contains invalid characters")
    
    try:
        # Replace ^ with ** for exponentiation
        expression = expression.replace('^', '**')
        # Evaluate the expression safely with limited math functions
        safe_dict = {"__builtins__": None}
        safe_dict.update({
            "abs": abs,
            "round": round,
            "max": max,
            "min": min
        })
        result = eval(expression, {"__builtins__": None}, safe_dict)
        return result
    except ZeroDivisionError:
        raise ZeroDivisionError("Cannot divide by zero")
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")

class Calculator:
    """An advanced calculator class with memory and history"""
    
    def __init__(self, initial_value: Union[int, float] = 0):
        """Initialize the calculator
        
        Args:
            initial_value: Initial value for the calculator
        """
        self.result = initial_value
        self.memory = 0.0
        self.history: List[Dict[str, Union[str, float]]] = []
        self._record_operation("init", initial_value, initial_value)
    
    def _record_operation(self, operation: str, value: Union[int, float], result: Union[int, float]) -> None:
        """Record an operation in the history
        
        Args:
            operation: The operation performed
            value: The value used in the operation
            result: The result after the operation
        """
        self.history.append({
            "operation": operation,
            "value": value,
            "result": result
        })
    
    def add(self, number: Union[int, float]) -> Union[int, float]:
        """Add a number to the result
        
        Args:
            number: Number to add
            
        Returns:
            Updated result
        """
        self.result += number
        self._record_operation("add", number, self.result)
        return self.result
    
    def subtract(self, number: Union[int, float]) -> Union[int, float]:
        """Subtract a number from the result
        
        Args:
            number: Number to subtract
            
        Returns:
            Updated result
        """
        self.result -= number
        self._record_operation("subtract", number, self.result)
        return self.result
    
    def multiply(self, number: Union[int, float]) -> Union[int, float]:
        """Multiply the result by a number
        
        Args:
            number: Number to multiply by
            
        Returns:
            Updated result
        """
        self.result *= number
        self._record_operation("multiply", number, self.result)
        return self.result
    
    def divide(self, number: Union[int, float]) -> Union[int, float]:
        """Divide the result by a number
        
        Args:
            number: Number to divide by
            
        Returns:
            Updated result
            
        Raises:
            ZeroDivisionError: If number is 0
        """
        if number == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        self.result /= number
        self._record_operation("divide", number, self.result)
        return self.result
    
    def power(self, exponent: Union[int, float]) -> Union[int, float]:
        """Raise the result to a power
        
        Args:
            exponent: The power to raise to
            
        Returns:
            Updated result
        """
        self.result **= exponent
        self._record_operation("power", exponent, self.result)
        return self.result
    
    def square_root(self) -> Union[int, float]:
        """Calculate the square root of the result
        
        Returns:
            Updated result
            
        Raises:
            ValueError: If result is negative
        """
        if self.result < 0:
            raise ValueError("Cannot calculate square root of a negative number")
        self.result = math.sqrt(self.result)
        self._record_operation("sqrt", None, self.result)
        return self.result
    
    def memory_store(self) -> None:
        """Store the current result in memory"""
        self.memory = self.result
        self._record_operation("m_store", self.result, self.result)
    
    def memory_recall(self) -> Union[int, float]:
        """Recall the value from memory
        
        Returns:
            The memory value
        """
        self._record_operation("m_recall", self.memory, self.result)
        return self.memory
    
    def memory_add(self) -> None:
        """Add the current result to memory"""
        self.memory += self.result
        self._record_operation("m_add", self.result, self.result)
    
    def memory_clear(self) -> None:
        """Clear the memory"""
        self.memory = 0.0
        self._record_operation("m_clear", 0, self.result)
    
    def clear(self) -> None:
        """Clear the result"""
        self.result = 0.0
        self._record_operation("clear", 0, self.result)
    
    def get_history(self) -> List[Dict[str, Union[str, float]]]:
        """Get the operation history
        
        Returns:
            List of operations performed
        """
        return self.history
    
    def evaluate(self, expression: str) -> Union[int, float]:
        """Evaluate a mathematical expression and update the result
        
        Args:
            expression: The expression to evaluate
            
        Returns:
            The result after evaluation
            
        Raises:
            ValueError: If expression is invalid
        """
        try:
            value = parse_expression(expression)
            self.result = value
            self._record_operation("evaluate", expression, value)
            return value
        except (ValueError, ZeroDivisionError) as e:
            self._record_operation("error", expression, str(e))
            raise