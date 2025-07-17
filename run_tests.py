#!/usr/bin/env python3
"""
Simple test runner for the inspiration board project.
Run this script to execute all tests with coverage.
"""

import subprocess
import sys
import os

def run_tests():
    """Run pytest with coverage."""
    try:
        # Check if pytest is installed
        subprocess.run([sys.executable, "-m", "pytest", "--version"], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("pytest not found. Installing test dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"], 
                      check=True)
    
    # Run tests with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--verbose"
    ]
    
    result = subprocess.run(cmd)
    return result.returncode

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code) 