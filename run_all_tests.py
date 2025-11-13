"""
Comprehensive Test Runner for Electronic Medication Administration Record (eMAR).

This script runs all test suites and generates a comprehensive test report:
- Unit tests (validation, queue management, blueprints)
- Integration tests (API validation, queue integration)
- Performance tests
- Edge case tests
- Regression tests
"""

import subprocess
import sys
import time
from datetime import datetime


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)


def run_test_file(test_file, description):
    """
    Run a test file and return the result.
    
    Args:
        test_file: Path to the test file
        description: Human-readable description
        
    Returns:
        tuple: (passed: bool, duration: float)
    """
    print(f"\n{'-'*70}")
    print(f"Running: {description}")
    print(f"File: {test_file}")
    print(f"{'-'*70}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        duration = time.time() - start_time
        
        # Print output
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        # Check exit code
        passed = result.returncode == 0
        
        return passed, duration
        
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        print(f"\n[FAIL] TEST TIMEOUT: {test_file} exceeded 5 minute limit")
        return False, duration
        
    except Exception as e:
        duration = time.time() - start_time
        print(f"\n[FAIL] ERROR running {test_file}: {e}")
        return False, duration


def check_server_running():
    """Check if the server needs to be started."""
    import requests
    
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def main():
    """Run all tests and generate report."""
    print_header("COMPREHENSIVE TEST SUITE - eMAR")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    overall_start = time.time()
    
    # Check if server is running for integration tests
    server_running = check_server_running()
    
    if not server_running:
        print("\n[WARN] WARNING: Server is not running at http://localhost:5000")
        print("Some integration, performance, edge case, and regression tests will fail.")
        print("To run all tests, start the server in a separate terminal:")
        print("  python app.py")
        print("\nContinuing with available tests...")
    else:
        print("\n[PASS] Server is running at http://localhost:5000")
    
    # Define all test suites
    test_suites = [
        # Unit tests (don't require server)
        {
            'file': 'test_validation.py',
            'description': 'Input Validation Unit Tests',
            'requires_server': False,
            'category': 'Unit Tests'
        },
        {
            'file': 'test_queue_management.py',
            'description': 'Queue Management Unit Tests',
            'requires_server': False,
            'category': 'Unit Tests'
        },
        {
            'file': 'test_blueprints.py',
            'description': 'Blueprint Architecture Tests',
            'requires_server': False,
            'category': 'Unit Tests'
        },
        # Integration tests (require server)
        {
            'file': 'test_api_validation.py',
            'description': 'API Validation Integration Tests',
            'requires_server': True,
            'category': 'Integration Tests'
        },
        {
            'file': 'test_queue_integration.py',
            'description': 'Queue API Integration Tests',
            'requires_server': True,
            'category': 'Integration Tests'
        },
        # New test suites (require server)
        {
            'file': 'test_performance.py',
            'description': 'Performance and Load Tests',
            'requires_server': True,
            'category': 'Performance Tests'
        },
        {
            'file': 'test_edge_cases.py',
            'description': 'Edge Case Tests',
            'requires_server': True,
            'category': 'Edge Case Tests'
        },
        {
            'file': 'test_regression.py',
            'description': 'Automated Regression Tests',
            'requires_server': True,
            'category': 'Regression Tests'
        },
    ]
    
    results = []
    skipped = []
    
    # Run each test suite
    for suite in test_suites:
        # Skip tests that require server if it's not running
        if suite['requires_server'] and not server_running:
            print(f"\n[WARN] SKIPPED: {suite['description']} (requires server)")
            skipped.append(suite)
            continue
        
        passed, duration = run_test_file(suite['file'], suite['description'])
        
        results.append({
            'suite': suite,
            'passed': passed,
            'duration': duration
        })
    
    overall_duration = time.time() - overall_start
    
    # Generate summary report
    print_header("TEST SUMMARY REPORT")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total duration: {overall_duration:.2f} seconds")
    
    # Group results by category
    categories = {}
    for result in results:
        category = result['suite']['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(result)
    
    # Print results by category
    total_passed = 0
    total_tests = len(results)
    
    for category, cat_results in categories.items():
        print(f"\n{category}:")
        cat_passed = sum(1 for r in cat_results if r['passed'])
        
        for result in cat_results:
            status = "[PASS] PASS" if result['passed'] else "[FAIL] FAIL"
            duration = f"{result['duration']:.2f}s"
            print(f"  {status} - {result['suite']['description']} ({duration})")
        
        print(f"  Subtotal: {cat_passed}/{len(cat_results)} passed")
        total_passed += cat_passed
    
    # Print skipped tests
    if skipped:
        print(f"\nSkipped Tests:")
        for suite in skipped:
            print(f"  [SKIP] {suite['description']} (requires server)")
    
    # Overall summary
    print(f"\n{'-'*70}")
    print(f"OVERALL RESULTS:")
    print(f"  Total Passed: {total_passed}/{total_tests}")
    if skipped:
        print(f"  Skipped: {len(skipped)} (server not running)")
    print(f"  Success Rate: {(total_passed/total_tests)*100:.1f}%")
    print(f"  Total Time: {overall_duration:.2f} seconds")
    
    # Final verdict
    print(f"\n{'='*70}")
    if total_passed == total_tests:
        print("[PASS] ALL TESTS PASSED!")
        print(f"{'='*70}")
        return 0
    else:
        failed = total_tests - total_passed
        print(f"[FAIL] {failed} TEST SUITE(S) FAILED")
        print(f"{'='*70}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n[WARN] Test run interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n[FAIL] FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
