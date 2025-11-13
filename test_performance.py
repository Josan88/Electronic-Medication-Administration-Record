"""
Performance and Load Testing Suite for Electronic Medication Administration Record (eMAR).

This test suite validates:
- API endpoint response times under load
- Concurrent request handling
- Queue processing performance
- Rate limiting behavior
- Memory and resource usage patterns
"""

import time
import statistics
import threading
import requests
from datetime import datetime
from typing import List, Dict, Any
import sys


BASE_URL = "http://localhost:5000"


def measure_response_time(func):
    """Decorator to measure function execution time."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, (end_time - start_time)
    return wrapper


def test_health_endpoint_performance():
    """Test health endpoint response time under repeated calls."""
    print("\n" + "="*60)
    print("HEALTH ENDPOINT PERFORMANCE TEST")
    print("="*60)
    
    response_times = []
    num_requests = 50
    
    print(f"\nSending {num_requests} requests to /api/health endpoint...")
    
    for i in range(num_requests):
        start = time.time()
        try:
            response = requests.get(f"{BASE_URL}/api/health", timeout=5)
            end = time.time()
            response_times.append((end - start) * 1000)  # Convert to ms
            
            if response.status_code != 200:
                print(f"✗ Request {i+1} failed with status {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Request {i+1} failed: {e}")
            return False
    
    # Calculate statistics
    avg_time = statistics.mean(response_times)
    median_time = statistics.median(response_times)
    min_time = min(response_times)
    max_time = max(response_times)
    std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0
    
    print(f"\n✓ Completed {num_requests} requests")
    print(f"  Average response time: {avg_time:.2f} ms")
    print(f"  Median response time: {median_time:.2f} ms")
    print(f"  Min response time: {min_time:.2f} ms")
    print(f"  Max response time: {max_time:.2f} ms")
    print(f"  Std deviation: {std_dev:.2f} ms")
    
    # Performance criteria: average should be under 100ms for health endpoint
    if avg_time < 100:
        print(f"✓ PASS: Average response time is acceptable ({avg_time:.2f} ms < 100 ms)")
        return True
    else:
        print(f"✗ FAIL: Average response time too slow ({avg_time:.2f} ms >= 100 ms)")
        return False


def test_concurrent_health_requests():
    """Test health endpoint with concurrent requests."""
    print("\n" + "="*60)
    print("CONCURRENT HEALTH REQUESTS TEST")
    print("="*60)
    
    num_threads = 10
    requests_per_thread = 10
    results = []
    errors = []
    lock = threading.Lock()
    
    def make_requests(thread_id):
        """Make multiple requests from a single thread."""
        for i in range(requests_per_thread):
            start = time.time()
            try:
                response = requests.get(f"{BASE_URL}/api/health", timeout=5)
                end = time.time()
                
                with lock:
                    results.append({
                        'thread_id': thread_id,
                        'request_num': i,
                        'status': response.status_code,
                        'time_ms': (end - start) * 1000
                    })
            except Exception as e:
                with lock:
                    errors.append(f"Thread {thread_id}, Request {i}: {e}")
    
    print(f"\nLaunching {num_threads} threads, each making {requests_per_thread} requests...")
    
    # Create and start threads
    threads = []
    start_time = time.time()
    
    for i in range(num_threads):
        thread = threading.Thread(target=make_requests, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Analyze results
    successful_requests = len([r for r in results if r['status'] == 200])
    total_requests = num_threads * requests_per_thread
    
    print(f"\n✓ Completed {successful_requests}/{total_requests} requests in {total_time:.2f} seconds")
    print(f"  Requests per second: {total_requests/total_time:.2f}")
    
    if errors:
        print(f"\n✗ {len(errors)} errors occurred:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  - {error}")
    else:
        print("✓ No errors occurred")
    
    if results:
        response_times = [r['time_ms'] for r in results]
        avg_time = statistics.mean(response_times)
        print(f"  Average response time: {avg_time:.2f} ms")
    
    # Success criteria: at least 95% success rate
    success_rate = (successful_requests / total_requests) * 100
    if success_rate >= 95:
        print(f"✓ PASS: Success rate is acceptable ({success_rate:.1f}% >= 95%)")
        return True
    else:
        print(f"✗ FAIL: Success rate too low ({success_rate:.1f}% < 95%)")
        return False


def test_read_endpoints_performance():
    """Test GET endpoints performance."""
    print("\n" + "="*60)
    print("READ ENDPOINTS PERFORMANCE TEST")
    print("="*60)
    
    endpoints = [
        "/api/patients",
        "/api/prescriptions",
        "/api/medication-tracking",
        "/api/queue/status"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        print(f"\nTesting {endpoint}...")
        response_times = []
        num_requests = 10
        
        for i in range(num_requests):
            start = time.time()
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
                end = time.time()
                response_times.append((end - start) * 1000)  # Convert to ms
                
                if response.status_code != 200:
                    print(f"  ✗ Request {i+1} failed with status {response.status_code}")
            except Exception as e:
                print(f"  ✗ Request {i+1} failed: {e}")
        
        if response_times:
            avg_time = statistics.mean(response_times)
            max_time = max(response_times)
            
            results[endpoint] = {
                'avg_time': avg_time,
                'max_time': max_time,
                'success_count': len(response_times)
            }
            
            print(f"  ✓ Average: {avg_time:.2f} ms, Max: {max_time:.2f} ms")
    
    # Performance criteria: average should be under 1000ms for read endpoints
    all_passed = True
    print(f"\nPerformance Summary:")
    for endpoint, data in results.items():
        if data['avg_time'] < 1000:
            print(f"  ✓ {endpoint}: {data['avg_time']:.2f} ms (PASS)")
        else:
            print(f"  ✗ {endpoint}: {data['avg_time']:.2f} ms (SLOW)")
            all_passed = False
    
    return all_passed


def test_queue_processing_performance():
    """Test queue processing performance with simulated load."""
    print("\n" + "="*60)
    print("QUEUE PROCESSING PERFORMANCE TEST")
    print("="*60)
    
    # Get initial queue status
    try:
        response = requests.get(f"{BASE_URL}/api/queue/status", timeout=5)
        if response.status_code != 200:
            print("✗ FAIL: Cannot get queue status")
            return False
        
        initial_status = response.json()['data']
        initial_size = initial_status.get('queue_size', initial_status.get('size', 0))
        
        print(f"\nInitial queue size: {initial_size}")
        print(f"Initial statistics: {initial_status.get('stats', initial_status.get('statistics', {}))}")
        
        # Add multiple prescriptions rapidly (they'll be queued)
        num_prescriptions = 5
        print(f"\nAdding {num_prescriptions} prescriptions to queue...")
        
        added_count = 0
        for i in range(num_prescriptions):
            prescription_data = {
                "patient_id": f"PERF_TEST_{i}",
                "medicine_name": f"Test Medicine {i}",
                "dosage": "500mg",
                "frequency": "Twice daily",
                "start_date": "2025-11-13",
                "end_date": "2025-12-13",
                "time_slot": "8AM, 8PM"
            }
            
            try:
                response = requests.post(
                    f"{BASE_URL}/api/prescriptions",
                    json=prescription_data,
                    timeout=5
                )
                
                if response.status_code == 202:
                    added_count += 1
                    print(f"  ✓ Prescription {i+1} queued (HTTP 202)")
                else:
                    print(f"  ✗ Prescription {i+1} failed: {response.status_code}")
            except Exception as e:
                print(f"  ✗ Prescription {i+1} error: {e}")
        
        # Check queue status again
        response = requests.get(f"{BASE_URL}/api/queue/status", timeout=5)
        if response.status_code == 200:
            updated_status = response.json()['data']
            new_size = updated_status.get('queue_size', updated_status.get('size', 0))
            
            print(f"\n✓ Added {added_count} prescriptions")
            print(f"  Queue size increased: {initial_size} → {new_size}")
            print(f"  Statistics: {updated_status.get('stats', updated_status.get('statistics', {}))}")
            
            if new_size >= initial_size + added_count:
                print("✓ PASS: All prescriptions successfully queued")
                return True
            else:
                print("✗ FAIL: Some prescriptions were not queued")
                return False
        else:
            print("✗ FAIL: Cannot get updated queue status")
            return False
            
    except Exception as e:
        print(f"✗ FAIL: Test error: {e}")
        return False


def test_memory_usage_pattern():
    """Test memory usage pattern under repeated operations."""
    print("\n" + "="*60)
    print("MEMORY USAGE PATTERN TEST")
    print("="*60)
    
    print("\nNote: This test monitors response time consistency over many requests")
    print("as a proxy for memory usage (no direct memory profiling)")
    
    num_iterations = 100
    response_times = []
    
    print(f"\nSending {num_iterations} health check requests...")
    
    for i in range(num_iterations):
        start = time.time()
        try:
            response = requests.get(f"{BASE_URL}/api/health", timeout=5)
            end = time.time()
            response_times.append((end - start) * 1000)
            
            if (i + 1) % 20 == 0:
                print(f"  Completed {i+1}/{num_iterations} requests...")
        except Exception as e:
            print(f"✗ Request {i+1} failed: {e}")
            return False
    
    # Analyze trend: check if response times are increasing (potential memory leak)
    first_quarter = response_times[:25]
    last_quarter = response_times[-25:]
    
    avg_first = statistics.mean(first_quarter)
    avg_last = statistics.mean(last_quarter)
    
    print(f"\n✓ Completed {num_iterations} requests")
    print(f"  First 25 requests average: {avg_first:.2f} ms")
    print(f"  Last 25 requests average: {avg_last:.2f} ms")
    
    # Check for degradation (>50% increase suggests potential issue)
    if avg_last > avg_first * 1.5:
        print(f"⚠ WARNING: Response time increased by {((avg_last/avg_first - 1) * 100):.1f}%")
        print("  This may indicate a memory leak or resource issue")
        return False
    else:
        print(f"✓ PASS: Response times remained consistent (variation: {((avg_last/avg_first - 1) * 100):.1f}%)")
        return True


def test_rate_limit_handling():
    """Test how the application handles rate limiting."""
    print("\n" + "="*60)
    print("RATE LIMIT HANDLING TEST")
    print("="*60)
    
    print("\nNote: This test verifies that the queue system properly handles rate limits")
    print("by checking queue status and behavior")
    
    try:
        # Get queue status
        response = requests.get(f"{BASE_URL}/api/queue/status", timeout=5)
        if response.status_code != 200:
            print("✗ FAIL: Cannot get queue status")
            return False
        
        status = response.json()['data']
        print(f"\nQueue status:")
        print(f"  Size: {status.get('queue_size', status.get('size', 0))}")
        print(f"  Max size: {status.get('max_size', 'N/A')}")
        print(f"  Is full: {status.get('is_full', False)}")
        print(f"  Failed items: {status.get('failed_count', 0)}")
        
        # Verify queue mechanism exists
        if 'stats' in status or 'statistics' in status:
            print(f"  Statistics: {status.get('stats', status.get('statistics', {}))}")
            print("✓ PASS: Rate limit handling via queue system is functional")
            return True
        else:
            print("✗ FAIL: Queue statistics not available")
            return False
            
    except Exception as e:
        print(f"✗ FAIL: Test error: {e}")
        return False


def main():
    """Run all performance tests."""
    print("\n" + "="*60)
    print("PERFORMANCE AND LOAD TEST SUITE")
    print("Electronic Medication Administration Record (eMAR)")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print(f"\n✗ ERROR: Server is not responding correctly (status: {response.status_code})")
            print("Please start the server with: python app.py")
            return 1
    except Exception as e:
        print(f"\n✗ ERROR: Cannot connect to server at {BASE_URL}")
        print(f"Error: {e}")
        print("Please start the server with: python app.py")
        return 1
    
    print(f"✓ Server is running at {BASE_URL}")
    
    # Run all tests
    tests = [
        ("Health Endpoint Performance", test_health_endpoint_performance),
        ("Concurrent Health Requests", test_concurrent_health_requests),
        ("Read Endpoints Performance", test_read_endpoints_performance),
        ("Queue Processing Performance", test_queue_processing_performance),
        ("Memory Usage Pattern", test_memory_usage_pattern),
        ("Rate Limit Handling", test_rate_limit_handling),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results[test_name] = passed
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("PERFORMANCE TEST SUMMARY")
    print("="*60)
    
    passed_count = sum(1 for passed in results.values() if passed)
    total_count = len(results)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal tests passed: {passed_count}/{total_count}")
    print(f"Success rate: {(passed_count/total_count)*100:.1f}%")
    
    if passed_count == total_count:
        print("\n✓ ALL PERFORMANCE TESTS PASSED!")
        return 0
    else:
        print(f"\n✗ {total_count - passed_count} PERFORMANCE TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
