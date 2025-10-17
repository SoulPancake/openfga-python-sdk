#!/usr/bin/env python3
"""
Simple structure validation test for the conflict options example.

This script validates that:
1. The docker-compose file is valid
2. The Makefile has the expected targets
3. The example script has the correct structure
"""

import os
import sys


def test_docker_compose():
    """Test that docker-compose.yml exists and has required services."""
    path = "docker-compose.yml"
    if not os.path.exists(path):
        print(f"✗ {path} not found")
        return False
    
    with open(path, 'r') as f:
        content = f.read()
    
    required = ['postgres', 'openfga', 'migrate']
    missing = [s for s in required if s not in content]
    
    if missing:
        print(f"✗ docker-compose.yml missing services: {missing}")
        return False
    
    print(f"✓ docker-compose.yml is valid")
    return True


def test_makefile():
    """Test that Makefile exists and has required targets."""
    path = "Makefile"
    if not os.path.exists(path):
        print(f"✗ {path} not found")
        return False
    
    with open(path, 'r') as f:
        content = f.read()
    
    required = ['start', 'stop', 'run', 'clean', 'status']
    missing = [t for t in required if t not in content]
    
    if missing:
        print(f"✗ Makefile missing targets: {missing}")
        return False
    
    print(f"✓ Makefile is valid")
    return True


def test_example_script():
    """Test that the example script exists and has required components."""
    path = "conflict_options_example.py"
    if not os.path.exists(path):
        print(f"✗ {path} not found")
        return False
    
    with open(path, 'r') as f:
        content = f.read()
    
    required = [
        'ConflictOptions',
        'ClientWriteRequestOnDuplicateWrites',
        'ClientWriteRequestOnMissingDeletes',
        'demo_duplicate_write_error',
        'demo_duplicate_write_ignore',
        'demo_missing_delete_error',
        'demo_missing_delete_ignore',
        'demo_both_ignore',
        'demo_both_error',
    ]
    missing = [c for c in required if c not in content]
    
    if missing:
        print(f"✗ Example script missing components: {missing}")
        return False
    
    print(f"✓ Example script is valid")
    return True


def test_readme():
    """Test that README exists and has required sections."""
    path = "README.md"
    if not os.path.exists(path):
        print(f"✗ {path} not found")
        return False
    
    with open(path, 'r') as f:
        content = f.read()
    
    required = [
        'Quick Start',
        'Test Scenarios',
        'Prerequisites',
        'Make Targets',
    ]
    missing = [s for s in required if s not in content]
    
    if missing:
        print(f"✗ README missing sections: {missing}")
        return False
    
    print(f"✓ README is valid")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Conflict Options Example Structure")
    print("=" * 60)
    
    tests = [
        test_docker_compose,
        test_makefile,
        test_example_script,
        test_readme,
    ]
    
    results = [test() for test in tests]
    
    print("=" * 60)
    if all(results):
        print("✓ All structure tests passed!")
        return 0
    else:
        print("✗ Some structure tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
