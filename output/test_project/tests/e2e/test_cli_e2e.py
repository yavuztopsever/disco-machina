"""
End-to-end tests for the calculator CLI.
Tests the actual execution of the CLI as a subprocess.
"""

import pytest
import subprocess
import sys
import os

@pytest.mark.e2e
class TestCliE2E:
    """End-to-end tests for calculator CLI."""
    
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
    
    def test_add_command_e2e(self):
        """Test add command in a real subprocess."""
        proc = self.run_cli("add", "5", "3")
        assert proc.returncode == 0
        assert "5.0 + 3.0 = 8.0" in proc.stdout
    
    def test_subtract_command_e2e(self):
        """Test subtract command in a real subprocess."""
        proc = self.run_cli("subtract", "10", "4")
        assert proc.returncode == 0
        assert "10.0 - 4.0 = 6.0" in proc.stdout
    
    def test_multiply_command_e2e(self):
        """Test multiply command in a real subprocess."""
        proc = self.run_cli("multiply", "6", "7")
        assert proc.returncode == 0
        assert "6.0 * 7.0 = 42.0" in proc.stdout
    
    def test_divide_command_e2e(self):
        """Test divide command in a real subprocess."""
        proc = self.run_cli("divide", "20", "5")
        assert proc.returncode == 0
        assert "20.0 / 5.0 = 4.0" in proc.stdout
    
    def test_divide_by_zero_e2e(self):
        """Test divide by zero error in a real subprocess."""
        proc = self.run_cli("divide", "10", "0")
        assert proc.returncode == 1
        assert "Error: Cannot divide by zero" in proc.stdout
    
    def test_help_command_e2e(self):
        """Test help output in a real subprocess."""
        proc = self.run_cli("--help")
        assert proc.returncode == 0
        assert "Calculator CLI tool" in proc.stdout
        
    def test_invalid_command_e2e(self):
        """Test behavior with invalid command."""
        proc = self.run_cli("invalid_command")
        # Invalid commands are handled by argparse before our code runs
        # So we just check that the process exits with an error code
        assert proc.returncode != 0
        assert "invalid choice" in proc.stderr