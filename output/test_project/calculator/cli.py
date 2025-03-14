#!/usr/bin/env python3
"""
Command Line Interface for the Advanced Calculator application.
"""

import argparse
import sys
import re
from .calculator import Calculator, add_numbers, hello_world, parse_expression

def handle_interactive_mode():
    """Run the calculator in interactive mode"""
    calc = Calculator()
    print("Advanced Calculator Interactive Mode")
    print("Type 'help' for instructions, 'exit' to quit")
    
    help_text = """
Commands:
  + <number>     - Add number to result
  - <number>     - Subtract number from result
  * <number>     - Multiply result by number
  / <number>     - Divide result by number
  ^ <number>     - Raise result to power
  sqrt           - Calculate square root of result
  clear          - Clear result to 0
  ms             - Store result in memory
  mr             - Recall value from memory
  m+             - Add result to memory
  mc             - Clear memory
  history        - Show operation history
  =<expression>  - Evaluate expression (e.g., =3+4*2)
  exit           - Exit the calculator
  help           - Show this help text
    """
    
    while True:
        try:
            # Display current result
            print(f"\nResult: {calc.result}")
            
            # Get user input
            user_input = input(">>> ").strip()
            
            # Handle commands
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            elif user_input.lower() == 'help':
                print(help_text)
            elif user_input.lower() == 'sqrt':
                try:
                    calc.square_root()
                except ValueError as e:
                    print(f"Error: {e}")
            elif user_input.lower() == 'clear':
                calc.clear()
            elif user_input.lower() == 'ms':
                calc.memory_store()
                print(f"Stored {calc.memory} in memory")
            elif user_input.lower() == 'mr':
                print(f"Memory: {calc.memory_recall()}")
            elif user_input.lower() == 'm+':
                calc.memory_add()
                print(f"Added result to memory: {calc.memory}")
            elif user_input.lower() == 'mc':
                calc.memory_clear()
                print("Memory cleared")
            elif user_input.lower() == 'history':
                history = calc.get_history()
                if not history:
                    print("No history yet")
                else:
                    print("\nOperation History:")
                    for i, op in enumerate(history):
                        # Skip the init operation
                        if i == 0 and op["operation"] == "init":
                            continue
                        value = op["value"]
                        value_str = str(value) if value is not None else ""
                        print(f"{i}: {op['operation']} {value_str} = {op['result']}")
            # Handle expression evaluation
            elif user_input.startswith('='):
                expression = user_input[1:].strip()
                try:
                    calc.evaluate(expression)
                except (ValueError, ZeroDivisionError) as e:
                    print(f"Error: {e}")
            # Handle basic operations
            elif re.match(r'^[\+\-\*\/\^]\s*\d+(\.\d+)?$', user_input):
                op = user_input[0]
                try:
                    number = float(user_input[1:].strip())
                    if op == '+':
                        calc.add(number)
                    elif op == '-':
                        calc.subtract(number)
                    elif op == '*':
                        calc.multiply(number)
                    elif op == '/':
                        try:
                            calc.divide(number)
                        except ZeroDivisionError as e:
                            print(f"Error: {e}")
                    elif op == '^':
                        calc.power(number)
                except ValueError:
                    print("Error: Invalid number")
            else:
                print("Error: Unknown command. Type 'help' for instructions.")
        except Exception as e:
            print(f"Error: {e}")
    
    return 0

def main():
    """Main entry point for the calculator CLI."""
    parser = argparse.ArgumentParser(description="Advanced Calculator CLI tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add two numbers")
    add_parser.add_argument("a", type=float, help="First number")
    add_parser.add_argument("b", type=float, help="Second number")
    
    # Subtract command
    subtract_parser = subparsers.add_parser("subtract", help="Subtract second number from first")
    subtract_parser.add_argument("a", type=float, help="First number")
    subtract_parser.add_argument("b", type=float, help="Second number")
    
    # Multiply command
    multiply_parser = subparsers.add_parser("multiply", help="Multiply two numbers")
    multiply_parser.add_argument("a", type=float, help="First number")
    multiply_parser.add_argument("b", type=float, help="Second number")
    
    # Divide command
    divide_parser = subparsers.add_parser("divide", help="Divide first number by second")
    divide_parser.add_argument("a", type=float, help="First number")
    divide_parser.add_argument("b", type=float, help="Second number")
    
    # Power command
    power_parser = subparsers.add_parser("power", help="Raise a number to a power")
    power_parser.add_argument("base", type=float, help="Base number")
    power_parser.add_argument("exponent", type=float, help="Exponent")
    
    # Square root command
    sqrt_parser = subparsers.add_parser("sqrt", help="Calculate the square root of a number")
    sqrt_parser.add_argument("number", type=float, help="Number to find square root of")
    
    # Expression command
    expr_parser = subparsers.add_parser("eval", help="Evaluate a mathematical expression")
    expr_parser.add_argument("expression", type=str, help="Expression to evaluate (e.g., '2+3*4')")
    
    # Interactive mode
    interactive_parser = subparsers.add_parser("interactive", help="Run calculator in interactive mode")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == "add":
        result = add_numbers(args.a, args.b)
        print(f"{args.a} + {args.b} = {result}")
    elif args.command == "subtract":
        calc = Calculator()
        calc.add(args.a)
        result = calc.subtract(args.b)
        print(f"{args.a} - {args.b} = {result}")
    elif args.command == "multiply":
        calc = Calculator()
        calc.add(args.a)
        result = calc.multiply(args.b)
        print(f"{args.a} * {args.b} = {result}")
    elif args.command == "divide":
        try:
            calc = Calculator()
            calc.add(args.a)
            result = calc.divide(args.b)
            print(f"{args.a} / {args.b} = {result}")
        except ZeroDivisionError:
            print("Error: Cannot divide by zero")
            return 1
    elif args.command == "power":
        calc = Calculator(args.base)
        result = calc.power(args.exponent)
        print(f"{args.base} ^ {args.exponent} = {result}")
    elif args.command == "sqrt":
        try:
            calc = Calculator(args.number)
            result = calc.square_root()
            print(f"√{args.number} = {result}")
        except ValueError as e:
            print(f"Error: {e}")
            return 1
    elif args.command == "eval":
        try:
            result = parse_expression(args.expression)
            print(f"{args.expression} = {result}")
        except (ValueError, ZeroDivisionError) as e:
            print(f"Error: {e}")
            return 1
    elif args.command == "interactive":
        return handle_interactive_mode()
    else:
        hello_world()
        parser.print_help()
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())