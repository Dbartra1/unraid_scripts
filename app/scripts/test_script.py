#!/usr/bin/env python3
"""
Test script for the job scheduling system.
This script can be scheduled to run periodically to test the scheduler.
"""

import os
import sys
import time
from datetime import datetime

def main():
    """Main function that simulates a script execution."""
    print(f"[{datetime.now().isoformat()}] Test script started")
    print(f"Script name: {os.path.basename(__file__)}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    
    # Simulate some work
    print("Performing test operations...")
    time.sleep(1)
    
    # Simulate success
    print("Test operations completed successfully!")
    print(f"[{datetime.now().isoformat()}] Test script finished")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in test script: {str(e)}")
        sys.exit(1)
