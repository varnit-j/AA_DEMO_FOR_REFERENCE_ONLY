#!/usr/bin/env python
"""
SAGA Test Runner Script
Runs all SAGA orchestrator tests and generates reports
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings')

# Add the project directory to the path
project_dir = Path(__file__).parent.parent
sys.path.insert(0, str(project_dir))

django.setup()

from flight.saga_tests import run_saga_tests
import logging

logger = logging.getLogger(__name__)

def main():
    """Main test runner function"""
    print("\n" + "=" * 80)
    print("SAGA ORCHESTRATOR TEST SUITE RUNNER")
    print("=" * 80 + "\n")
    
    try:
        # Run all tests
        results = run_saga_tests()
        
        # Print summary
        print("\n" + "=" * 80)
        print("TEST EXECUTION COMPLETED")
        print("=" * 80)
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print("=" * 80 + "\n")
        
        return results
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()
