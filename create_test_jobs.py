#!/usr/bin/env python3
"""
Create test jobs for testing delete functionality
"""

import json
from pathlib import Path
from datetime import datetime

def create_test_jobs():
    """Create some test jobs"""
    
    test_jobs = [
        {
            "generator": "sketch2lifeui",
            "schedule": "0 9 * * *",
            "schedule_type": "daily",
            "schedule_data": {"time": "09:00"},
            "notify": True,
            "created_at": datetime.now().isoformat()
        },
        {
            "generator": "dogshow",
            "schedule": "0 14 * * 1,3,5",
            "schedule_type": "weekly",
            "schedule_data": {
                "time": "14:00",
                "days": ["1", "3", "5"]
            },
            "notify": False,
            "created_at": datetime.now().isoformat()
        },
        {
            "generator": "music",
            "schedule": "0 20 1 * *",
            "schedule_type": "monthly",
            "schedule_data": {
                "time": "20:00",
                "day": "1"
            },
            "notify": True,
            "created_at": datetime.now().isoformat()
        }
    ]
    
    # Save to jobs.json
    jobs_file = Path("jobs.json")
    jobs_file.write_text(json.dumps(test_jobs, indent=2))
    
    print("✅ Created test jobs:")
    for i, job in enumerate(test_jobs):
        print(f"  {i}: {job['generator']} - {job['schedule']}")
    
    print(f"\n🎯 You can now test the delete functionality at:")
    print(f"   http://localhost:5001")
    print(f"\n📊 Current jobs count: {len(test_jobs)}")

if __name__ == "__main__":
    create_test_jobs() 