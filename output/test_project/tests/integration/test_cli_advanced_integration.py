"""
Integration tests for the advanced CLI module.
Test the interaction between advanced CLI and Calculator modules.
"""

import pytest
import io
import sys
from unittest.mock import patch
from calculator.cli import main

@pytest.mark.integration
class TestAdvancedCliIntegration:
    """Test advanced CLI integration with Calculator functionality."""
    
    def test_power_command(self):
        """Test 'power' command with Calculator operations."""
        with patch.object(sys, 'argv', ['calculator', 'power', '2', '3']):
            with patch('sys.stdout', new=io.StringIO()) as fake_output:
                assert main() == 0
                assert fake_output.getvalue().strip() == "2.0 ^ 3.0 = 8.0"
    
    def test_sqrt_command(self):
        """Test 'sqrt' command with Calculator operations."""
        with patch.object(sys, 'argv', ['calculator', 'sqrt', '16']):
            with patch('sys.stdout', new=io.StringIO()) as fake_output:
                assert main() == 0
                assert fake_output.getvalue().strip() == "√16.0 = 4.0"
    
    def test_sqrt_negative_number(self):
        """Test 'sqrt' command with negative number."""
        with patch.object(sys, 'argv', ['calculator', 'sqrt', '-4']):
            with patch('sys.stdout', new=io.StringIO()) as fake_output:
                assert main() == 1
                assert "Error: Cannot calculate square root of a negative number" in fake_output.getvalue()
    
    def test_eval_command(self):
        """Test 'eval' command with Calculator operations."""
        with patch.object(sys, 'argv', ['calculator', 'eval', '2+3*4']):
            with patch('sys.stdout', new=io.StringIO()) as fake_output:
                assert main() == 0
                assert fake_output.getvalue().strip() == "2+3*4 = 14"
    
    def test_eval_with_parentheses(self):
        """Test 'eval' command with parentheses."""
        with patch.object(sys, 'argv', ['calculator', 'eval', '(2+3)*4']):
            with patch('sys.stdout', new=io.StringIO()) as fake_output:
                assert main() == 0
                assert fake_output.getvalue().strip() == "(2+3)*4 = 20"
    
    def test_eval_invalid_expression(self):
        """Test 'eval' command with invalid expression."""
        with patch.object(sys, 'argv', ['calculator', 'eval', '2+*3']):
            with patch('sys.stdout', new=io.StringIO()) as fake_output:
                assert main() == 1
                assert "Error:" in fake_output.getvalue()
    
    def test_interactive_mode_initialization(self):
        """Test that interactive mode initializes properly."""
        with patch.object(sys, 'argv', ['calculator', 'interactive']):
            with patch('calculator.cli.handle_interactive_mode') as mock_interactive:
                mock_interactive.return_value = 0
                assert main() == 0
                mock_interactive.assert_called_once()

@pytest.mark.integration
class TestInteractiveMode:
    """Test the interactive mode of the calculator."""
    
    def test_help_command(self):
        """Test displaying help in interactive mode."""
        # Simulate user entering 'help' then 'exit'
        user_inputs = ['help', 'exit']
        
        with patch('builtins.input', side_effect=user_inputs):
            with patch('sys.stdout', new=io.StringIO()) as fake_output:
                from calculator.cli import handle_interactive_mode
                handle_interactive_mode()
                output = fake_output.getvalue()
                assert "Commands:" in output
                assert "Add number to result" in output
    
    def test_basic_operations(self):
        """Test basic operations in interactive mode."""
        # Simulate user performing operations and then exiting
        user_inputs = [
            '+ 5',     # Add 5
            '* 2',     # Multiply by 2
            '- 3',     # Subtract 3
            '/ 2',     # Divide by 2
            'exit'
        ]
        
        with patch('builtins.input', side_effect=user_inputs):
            with patch('sys.stdout', new=io.StringIO()) as fake_output:
                from calculator.cli import handle_interactive_mode
                handle_interactive_mode()
                output = fake_output.getvalue()
                
                # Initial result is 0
                assert "Result: 0" in output
                
                # After adding 5
                assert "Result: 5" in output
                
                # After multiplying by 2 (result = 10)
                assert "Result: 10" in output
                
                # After subtracting 3 (result = 7)
                assert "Result: 7" in output
                
                # After dividing by 2 (result = 3.5)
                assert "Result: 3.5" in output
    
    def test_memory_operations(self):
        """Test memory operations in interactive mode."""
        user_inputs = [
            '+ 10',    # Add 10
            'ms',      # Store in memory
            '* 2',     # Multiply by 2
            'm+',      # Add to memory
            'clear',   # Clear result
            'mr',      # Recall memory
            'exit'
        ]
        
        with patch('builtins.input', side_effect=user_inputs):
            with patch('sys.stdout', new=io.StringIO()) as fake_output:
                from calculator.cli import handle_interactive_mode
                handle_interactive_mode()
                output = fake_output.getvalue()
                
                # Check memory store worked
                assert "Stored 10" in output
                
                # Check memory add worked
                assert "Added result to memory: 30" in output
                
                # Check memory recall worked
                assert "Memory: 30" in output
    
    def test_expression_evaluation(self):
        """Test expression evaluation in interactive mode."""
        user_inputs = [
            '=2+3*4',  # Evaluate 2+3*4
            '=10/2',   # Evaluate 10/2
            'exit'
        ]
        
        with patch('builtins.input', side_effect=user_inputs):
            with patch('sys.stdout', new=io.StringIO()) as fake_output:
                from calculator.cli import handle_interactive_mode
                handle_interactive_mode()
                output = fake_output.getvalue()
                
                # Check first result
                assert "Result: 14" in output
                
                # Check second result
                assert "Result: 5" in output
    
    def test_error_handling(self):
        """Test error handling in interactive mode."""
        user_inputs = [
            '/ 0',     # Divide by zero
            'sqrt',    # Square root of 0
            '+ 9',     # Add 9
            'sqrt',    # Square root of 9
            '= invalid',  # Invalid expression
            'unknown',  # Unknown command
            'exit'
        ]
        
        with patch('builtins.input', side_effect=user_inputs):
            with patch('sys.stdout', new=io.StringIO()) as fake_output:
                from calculator.cli import handle_interactive_mode
                handle_interactive_mode()
                output = fake_output.getvalue()
                
                # Check divide by zero error
                assert "Error: Cannot divide by zero" in output
                
                # Check square root works after adding 9
                assert "Result: 3.0" in output
                
                # Check invalid expression error
                assert "Error: Invalid expression" in output or "Error: Expression contains invalid characters" in output
                
                # Check unknown command error
                assert "Error: Unknown command" in output