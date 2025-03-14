"""
End-to-end tests for the advanced calculator CLI.
Tests the actual execution of the CLI as a subprocess.
"""

import pytest
import subprocess
import sys
import os
import time
import signal
import pexpect
import re
import tempfile
from pathlib import Path

@pytest.mark.e2e
class TestAdvancedCliE2E:
    """End-to-end tests for advanced calculator CLI."""
    
    def run_cli(self, *args):
        """Helper to run the CLI with given arguments."""
        cmd = [sys.executable, "-m", "calculator.cli"] + list(args)
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return proc
    
    def test_power_command_e2e(self):
        """Test power command in a real subprocess."""
        proc = self.run_cli("power", "2", "3")
        assert proc.returncode == 0
        assert "2.0 ^ 3.0 = 8.0" in proc.stdout
    
    def test_sqrt_command_e2e(self):
        """Test sqrt command in a real subprocess."""
        proc = self.run_cli("sqrt", "16")
        assert proc.returncode == 0
        assert "√16.0 = 4.0" in proc.stdout
    
    def test_sqrt_negative_e2e(self):
        """Test sqrt command with negative number in a real subprocess."""
        proc = self.run_cli("sqrt", "-4")
        assert proc.returncode == 1
        assert "Error: Cannot calculate square root of a negative number" in proc.stdout
    
    def test_eval_command_e2e(self):
        """Test eval command in a real subprocess."""
        proc = self.run_cli("eval", "2+3*4")
        assert proc.returncode == 0
        assert "2+3*4 = 14" in proc.stdout
    
    def test_eval_with_parentheses_e2e(self):
        """Test eval command with parentheses in a real subprocess."""
        proc = self.run_cli("eval", "(2+3)*4")
        assert proc.returncode == 0
        assert "(2+3)*4 = 20" in proc.stdout
    
    def test_eval_invalid_e2e(self):
        """Test eval command with invalid expression in a real subprocess."""
        proc = self.run_cli("eval", "2+*3")
        assert proc.returncode == 1
        assert "Error:" in proc.stdout
    
    def test_eval_security_e2e(self):
        """Test eval command security in a real subprocess."""
        proc = self.run_cli("eval", "__import__('os').system('ls')")
        assert proc.returncode == 1
        assert "Error:" in proc.stdout

@pytest.mark.e2e
@pytest.mark.skipif(sys.platform == "win32", reason="pexpect doesn't work well on Windows")
class TestInteractiveModeE2E:
    """End-to-end tests for interactive mode using pexpect."""
    
    def test_basic_interactive_session(self):
        """Test a basic interactive session with multiple commands."""
        if sys.platform == "win32":
            pytest.skip("pexpect doesn't work well on Windows")
            
        # Create a temp file to log the interactive session
        log_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            # Start the interactive process
            child = pexpect.spawn(f"{sys.executable} -m calculator.cli interactive", 
                                 encoding='utf-8', logfile=open(log_file.name, 'w'))
            
            # Wait for the prompt
            child.expect(">>> ", timeout=2)
            
            # Test help command
            child.sendline("help")
            child.expect("Commands:", timeout=2)
            child.expect(">>> ", timeout=2)
            
            # Test adding a number
            child.sendline("+ 10")
            child.expect(r"Result: 10\.0", timeout=2)
            child.expect(">>> ", timeout=2)
            
            # Test multiplying
            child.sendline("* 2")
            child.expect(r"Result: 20\.0", timeout=2)
            child.expect(">>> ", timeout=2)
            
            # Test memory store
            child.sendline("ms")
            child.expect(r"Stored 20\.0 in memory", timeout=2)
            child.expect(">>> ", timeout=2)
            
            # Test using an expression
            child.sendline("=5+5*2")
            child.expect(r"Result: 15", timeout=2)
            child.expect(">>> ", timeout=2)
            
            # Test memory recall
            child.sendline("mr")
            child.expect(r"Memory: 20\.0", timeout=2)
            child.expect(">>> ", timeout=2)
            
            # Test square root
            child.sendline("sqrt")
            child.expect(r"Result: 3\.", timeout=2)
            child.expect(">>> ", timeout=2)
            
            # Test clear
            child.sendline("clear")
            child.expect(r"Result: 0\.0", timeout=2)
            child.expect(">>> ", timeout=2)
            
            # Exit the program
            child.sendline("exit")
            child.expect("Goodbye!", timeout=2)
            child.expect(pexpect.EOF, timeout=2)
            
            # Make sure it exited cleanly
            assert child.isalive() is False
            
        finally:
            # Clean up
            if child.isalive():
                child.close()
            
            # Read the log file to help with debugging if needed
            with open(log_file.name, 'r') as f:
                log_content = f.read()
            
            # Close and remove the temp file
            log_file.close()
            Path(log_file.name).unlink()
    
    def test_error_handling_interactive(self):
        """Test error handling in interactive mode."""
        if sys.platform == "win32":
            pytest.skip("pexpect doesn't work well on Windows")
            
        # Create a temp file to log the interactive session
        log_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            # Start the interactive process
            child = pexpect.spawn(f"{sys.executable} -m calculator.cli interactive", 
                                 encoding='utf-8', logfile=open(log_file.name, 'w'))
            
            # Wait for the prompt
            child.expect(">>> ", timeout=2)
            
            # Test division by zero
            child.sendline("/ 0")
            child.expect("Error: Cannot divide by zero", timeout=2)
            child.expect(">>> ", timeout=2)
            
            # Test adding a number after error
            child.sendline("+ 5")
            child.expect(r"Result: 5\.0", timeout=2)
            child.expect(">>> ", timeout=2)
            
            # Test invalid expression
            child.sendline("=2+*3")
            child.expect("Error:", timeout=2)
            child.expect(">>> ", timeout=2)
            
            # Test unknown command
            child.sendline("unknown")
            child.expect("Error: Unknown command", timeout=2)
            child.expect(">>> ", timeout=2)
            
            # Exit the program
            child.sendline("exit")
            child.expect("Goodbye!", timeout=2)
            child.expect(pexpect.EOF, timeout=2)
            
            # Make sure it exited cleanly
            assert child.isalive() is False
            
        finally:
            # Clean up
            if child.isalive():
                child.close()
            
            # Read the log file to help with debugging if needed
            with open(log_file.name, 'r') as f:
                log_content = f.read()
            
            # Close and remove the temp file
            log_file.close()
            Path(log_file.name).unlink()