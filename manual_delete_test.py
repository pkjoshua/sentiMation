#!/usr/bin/env python3
"""
Manual test to verify delete functionality works
"""

import json
from pathlib import Path
import sys
import os

# Add the webapp directory to the path so we can import the app
sys.path.append('webapp')

def test_delete_manually():
    """Test delete functionality by directly calling the functions"""
    
    # Import the functions we need
    from app import load_jobs, save_jobs
    
    print("🧪 Manual Delete Test")
    print("=" * 30)
    
    # Load current jobs
    jobs = load_jobs()
    print(f"Current jobs: {len(jobs)}")
    
    if not jobs:
        print("No jobs to delete!")
        return
    
    # Show current jobs
    for i, job in enumerate(jobs):
        print(f"  {i}: {job['generator']} - {job['schedule']}")
    
    # Test deleting the first job
    if jobs:
        job_to_delete = jobs[0]
        print(f"\n🗑️  Deleting job: {job_to_delete['generator']}")
        
        # Remove the job
        jobs.pop(0)
        save_jobs(jobs)
        
        print(f"✅ Job deleted! New count: {len(jobs)}")
        
        # Verify the job was actually removed
        jobs_after = load_jobs()
        print(f"✅ Verification: jobs after deletion: {len(jobs_after)}")
        
        if len(jobs_after) == len(jobs):
            print("✅ Delete test PASSED!")
        else:
            print("❌ Delete test FAILED!")
    else:
        print("No jobs to delete!")

if __name__ == "__main__":
    test_delete_manually() 