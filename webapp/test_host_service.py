#!/usr/bin/env python3
"""
Test script for host service integration
"""
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from host_scheduler_client import HostSchedulerClient, JobSpec, JobStep, create_generator_job_steps
import config

def test_host_service_connection():
    """Test basic connection to host service"""
    print("Testing host service connection...")
    
    client = HostSchedulerClient(config.HOST_SERVICE_URL)
    
    try:
        is_available = client.is_available()
        print(f"Host service available: {is_available}")
        return is_available
    except Exception as e:
        print(f"Error checking host service: {e}")
        return False

def test_job_creation():
    """Test creating job specifications"""
    print("\nTesting job creation...")
    
    try:
        # Test music generator
        music_steps = create_generator_job_steps("music", "test_prompt")
        print(f"Music generator steps: {len(music_steps)}")
        
        # Test custom generator
        custom_steps = create_generator_job_steps("custom", "test_prompt", "test_character", "test_environment")
        print(f"Custom generator steps: {len(custom_steps)}")
        
        # Create job spec
        job_spec = JobSpec("test_job", music_steps, time="14:30")
        print(f"Job spec created: {job_spec.task_name}")
        
        return True
    except Exception as e:
        print(f"Error creating job: {e}")
        return False

def test_schedule_job():
    """Test scheduling a job with host service"""
    print("\nTesting job scheduling...")
    
    if not test_host_service_connection():
        print("Host service not available, skipping scheduling test")
        return False
    
    client = HostSchedulerClient(config.HOST_SERVICE_URL)
    
    try:
        # Create a simple test job
        steps = [JobStep("test_step", "-v /tmp:/workspace -w /workspace python:3.9-slim echo 'Hello World'")]
        job_spec = JobSpec("test_schedule_job", steps, time="15:00")
        
        result = client.schedule_job(job_spec)
        print(f"Job scheduled successfully: {result}")
        return True
        
    except Exception as e:
        print(f"Error scheduling job: {e}")
        return False

def test_run_job_now():
    """Test running a job immediately"""
    print("\nTesting immediate job execution...")
    
    if not test_host_service_connection():
        print("Host service not available, skipping execution test")
        return False
    
    client = HostSchedulerClient(config.HOST_SERVICE_URL)
    
    try:
        # Create a simple test job
        steps = [JobStep("test_step", "-v /tmp:/workspace -w /workspace python:3.9-slim echo 'Hello World'")]
        job_spec = JobSpec("test_run_now_job", steps)
        
        result = client.run_job_now(job_spec)
        print(f"Job executed successfully: {result}")
        return True
        
    except Exception as e:
        print(f"Error executing job: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Host Service Integration Tests ===\n")
    
    tests = [
        ("Connection Test", test_host_service_connection),
        ("Job Creation Test", test_job_creation),
        ("Job Scheduling Test", test_schedule_job),
        ("Immediate Execution Test", test_run_job_now)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"{test_name}: {'PASS' if result else 'FAIL'}\n")
        except Exception as e:
            print(f"{test_name}: ERROR - {e}\n")
            results.append((test_name, False))
    
    # Summary
    print("=== Test Summary ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! Host service integration is working correctly.")
    else:
        print("Some tests failed. Check the host service configuration and availability.")

if __name__ == "__main__":
    main()
