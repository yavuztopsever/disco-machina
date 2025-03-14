"""
Step definitions for calculator feature tests.
"""

import subprocess
import sys
import io
from unittest.mock import patch
from behave import given, when, then, step
from calculator import Calculator, add_numbers, parse_expression
from calculator.cli import handle_interactive_mode

@given('I have a calculator')
def step_have_calculator(context):
    """Create a new calculator instance."""
    context.calculator = Calculator()
    context.error = None

@when('I add {a:d} and {b:d}')
def step_add_numbers(context, a, b):
    """Add two numbers using the calculator."""
    context.result = add_numbers(a, b)

@when('I subtract {b:d} from {a:d}')
def step_subtract_numbers(context, a, b):
    """Subtract a number from another using calculator."""
    context.calculator.add(a)
    context.result = context.calculator.subtract(b)

@when('I multiply {a:d} by {b:d}')
def step_multiply_numbers(context, a, b):
    """Multiply two numbers using calculator."""
    context.calculator.add(a)
    context.result = context.calculator.multiply(b)

@when('I divide {a:d} by {b:d}')
def step_divide_numbers(context, a, b):
    """Divide a number by another using calculator."""
    context.calculator.add(a)
    context.result = context.calculator.divide(b)

@when('I try to divide {a:d} by {b:d}')
def step_try_divide_by_zero(context, a, b):
    """Try to divide by zero and catch exception."""
    context.calculator.add(a)
    try:
        context.calculator.divide(b)
    except ZeroDivisionError as e:
        context.error = e

@when('I perform "{operation}" with {a:d} and {b:d}')
def step_perform_operation(context, operation, a, b):
    """Perform a specified operation using CLI."""
    cmd = [sys.executable, "-m", "calculator.cli", operation, str(a), str(b)]
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False
    )
    context.process_result = result
    
    # Extract the result value from the output
    if result.returncode == 0:
        output_parts = result.stdout.strip().split('=')
        if len(output_parts) > 1:
            context.result = float(output_parts[1].strip())

@then('the result should be {expected:d}')
def step_check_result(context, expected):
    """Check that the result matches the expected value."""
    if hasattr(context, 'process_result'):
        assert context.process_result.returncode == 0
        assert context.result == float(expected)
    else:
        assert context.result == expected

@then('I should get a division by zero error')
def step_check_division_by_zero(context):
    """Check that a division by zero error was raised."""
    assert context.error is not None
    assert isinstance(context.error, ZeroDivisionError)

# Advanced calculator steps

@when('I set the initial value to {value:f}')
def step_set_initial_value(context, value):
    """Set the initial value of the calculator."""
    context.calculator = Calculator(value)

@when('I raise it to the power of {exponent:d}')
def step_raise_to_power(context, exponent):
    """Raise the result to a power."""
    context.result = context.calculator.power(exponent)

@when('I take the square root')
def step_take_square_root(context):
    """Take the square root of the result."""
    try:
        context.result = context.calculator.square_root()
    except ValueError as e:
        context.error = e

@when('I store the result in memory')
def step_store_in_memory(context):
    """Store the result in memory."""
    context.calculator.memory_store()

@when('I clear the result')
def step_clear_result(context):
    """Clear the calculator result."""
    context.calculator.clear()

@when('I add the memory value to the result')
def step_add_memory_to_result(context):
    """Add the memory value to the result."""
    memory_value = context.calculator.memory_recall()
    context.result = context.calculator.add(memory_value)

@when('I evaluate the expression "{expression}"')
def step_evaluate_expression(context, expression):
    """Evaluate a mathematical expression."""
    try:
        context.result = context.calculator.evaluate(expression)
    except (ValueError, ZeroDivisionError) as e:
        context.error = e

@then('taking the square root should give an error')
def step_check_square_root_error(context):
    """Check that taking the square root of a negative number raises an error."""
    try:
        context.calculator.square_root()
        assert False, "Expected ValueError was not raised"
    except ValueError as e:
        assert "Cannot calculate square root of a negative number" in str(e)

@when('I perform "{operation}" with value {operand:f}')
def step_perform_operation_with_value(context, operation, operand):
    """Perform a specified operation with the given value."""
    if operation == "power":
        context.result = context.calculator.power(operand)
    elif operation == "sqrt":
        context.result = context.calculator.square_root()
    elif operation == "multiply":
        context.result = context.calculator.multiply(operand)
    elif operation == "divide":
        context.result = context.calculator.divide(operand)
    elif operation == "add":
        context.result = context.calculator.add(operand)
    elif operation == "subtract":
        context.result = context.calculator.subtract(operand)
    else:
        raise ValueError(f"Unknown operation: {operation}")

@when('I perform the following operations')
def step_perform_operations_table(context):
    """Perform a series of operations from a table."""
    for row in context.table:
        operation = row['operation']
        value = float(row['value'])
        step_perform_operation_with_value(context, operation, value)

# Interactive mode testing steps

@given('I am using the calculator in interactive mode')
def step_using_interactive_mode(context):
    """Set up calculator for interactive mode testing."""
    context.calculator = Calculator()
    context.inputs = []
    context.output = io.StringIO()

@when('I enter command "{command}"')
def step_enter_command(context, command):
    """Enter a command in interactive mode."""
    context.inputs.append(command)

@then('the final result should be {expected:d}')
def step_check_final_result(context, expected):
    """Check the final result after a series of commands."""
    # Add exit command to end the interactive session
    context.inputs.append("exit")
    
    # Run the interactive mode with our prepared inputs
    with patch('builtins.input', side_effect=context.inputs):
        with patch('sys.stdout', new=context.output):
            handle_interactive_mode()
    
    # Check the result in the output
    output_text = context.output.getvalue()
    assert f"Result: {expected}" in output_text