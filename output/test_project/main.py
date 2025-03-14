#!/usr/bin/env python3
"""
Simple test project for Disco-Machina
"""

def hello_world():
    """Print a greeting message"""
    print("Hello, world!")

def add_numbers(a, b):
    """Add two numbers together
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
    """
    return a + b

class Calculator:
    """A simple calculator class"""
    
    def __init__(self):
        """Initialize the calculator"""
        self.result = 0
    
    def add(self, number):
        """Add a number to the result
        
        Args:
            number: Number to add
            
        Returns:
            Updated result
        """
        self.result += number
        return self.result
    
    def subtract(self, number):
        """Subtract a number from the result
        
        Args:
            number: Number to subtract
            
        Returns:
            Updated result
        """
        self.result -= number
        return self.result
    
    def multiply(self, number):
        """Multiply the result by a number
        
        Args:
            number: Number to multiply by
            
        Returns:
            Updated result
        """
        self.result *= number
        return self.result
    
    def divide(self, number):
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
        return self.result

if __name__ == "__main__":
    hello_world()
    calc = Calculator()
    print(f"1 + 2 = {add_numbers(1, 2)}")
    
    calc.add(5)
    print(f"Result: {calc.result}")
    
    calc.subtract(2)
    print(f"Result: {calc.result}")
    
    calc.multiply(3)
    print(f"Result: {calc.result}")
    
    calc.divide(3)
    print(f"Result: {calc.result}")