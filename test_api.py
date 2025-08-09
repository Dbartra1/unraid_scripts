#!/usr/bin/env python3
"""
Simple test script to verify the API endpoints work correctly.
Run this after starting the Flask application.
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api/jobs"

def test_api():
    """Test the API endpoints."""
    print("Testing Unraid Scripts Job API...")
    print("=" * 50)
    
    # Test 1: Get all jobs (should be empty initially)
    print("\n1. Testing GET /api/jobs/")
    try:
        response = requests.get(BASE_URL)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Add a test job
    print("\n2. Testing POST /api/jobs/")
    try:
        job_data = {
            "script_name": "test_script",
            "frequency": "every_5_minutes",
            "description": "Test script for API testing"
        }
        response = requests.post(BASE_URL, json=job_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Get all jobs again (should have one job)
    print("\n3. Testing GET /api/jobs/ (after adding job)")
    try:
        response = requests.get(BASE_URL)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Get specific job
    print("\n4. Testing GET /api/jobs/test_script")
    try:
        response = requests.get(f"{BASE_URL}/test_script")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Update job frequency
    print("\n5. Testing PATCH /api/jobs/test_script")
    try:
        update_data = {
            "frequency": "hourly",
            "description": "Updated test script description"
        }
        response = requests.patch(f"{BASE_URL}/test_script", json=update_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 6: Run job immediately
    print("\n6. Testing POST /api/jobs/test_script/run")
    try:
        response = requests.post(f"{BASE_URL}/test_script/run")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 7: Get scheduler status
    print("\n7. Testing GET /api/jobs/scheduler/status")
    try:
        response = requests.get(f"{BASE_URL}/scheduler/status")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 8: Cancel job
    print("\n8. Testing DELETE /api/jobs/test_script")
    try:
        response = requests.delete(f"{BASE_URL}/test_script")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 9: Get all jobs (should be empty again)
    print("\n9. Testing GET /api/jobs/ (after deleting job)")
    try:
        response = requests.get(BASE_URL)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("API testing completed!")

if __name__ == "__main__":
    test_api()
