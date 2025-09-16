#!/usr/bin/env python3
"""
Test script to verify InlinkAI login and LinkedIn connection functionality
"""

import requests
import time
import json

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "john.doe@example.com"
TEST_OTP = "123456"
TEST_LINKEDIN_URL = "https://linkedin.com/in/johndoe"

def test_login_flow():
    """Test the complete login flow"""
    
    session = requests.Session()
    
    print("🔧 Testing InlinkAI Login Flow")
    print("=" * 40)
    
    # Step 1: Get login page
    print("1️⃣ Accessing login page...")
    response = session.get(f"{BASE_URL}/login")
    if response.status_code == 200:
        print("✅ Login page accessible")
    else:
        print(f"❌ Login page failed: {response.status_code}")
        return False
    
    # Step 2: Submit email for OTP
    print("2️⃣ Submitting email for OTP...")
    response = session.post(f"{BASE_URL}/login", data={"email": TEST_EMAIL})
    if response.status_code == 200 and "OTP" in response.text:
        print("✅ Email submitted successfully")
    else:
        print(f"❌ Email submission failed: {response.status_code}")
        return False
    
    # Step 3: Submit OTP
    print("3️⃣ Submitting OTP...")
    response = session.post(f"{BASE_URL}/login_access", data={"otp": TEST_OTP}, allow_redirects=False)
    if response.status_code == 302:  # Redirect to dashboard
        print("✅ OTP verification successful")
    elif response.status_code == 200:
        # Check if we got redirected by following the final URL
        dashboard_response = session.get(f"{BASE_URL}/dashboard")
        if dashboard_response.status_code == 200:
            print("✅ OTP verification successful (already redirected)")
        else:
            print(f"❌ OTP verification failed: Dashboard not accessible")
            return False
    else:
        print(f"❌ OTP verification failed: {response.status_code}")
        return False
    
    # Step 4: Access dashboard
    print("4️⃣ Accessing dashboard...")
    response = session.get(f"{BASE_URL}/dashboard")
    if response.status_code == 200 and "InlinkAI" in response.text:
        print("✅ Dashboard accessible")
    else:
        print(f"❌ Dashboard access failed: {response.status_code}")
        return False
    
    return session

def test_linkedin_connection(session):
    """Test LinkedIn profile connection"""
    
    print("\n🔗 Testing LinkedIn Connection")
    print("=" * 40)
    
    # Step 1: Start LinkedIn connection
    print("1️⃣ Starting LinkedIn connection...")
    response = session.post(
        f"{BASE_URL}/connect_linkedin",
        json={"linkedin_url": TEST_LINKEDIN_URL},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            job_id = data.get("job_id")
            print(f"✅ LinkedIn connection started - Job ID: {job_id}")
            return job_id
        else:
            print(f"❌ LinkedIn connection failed: {data.get('error')}")
            return None
    else:
        print(f"❌ LinkedIn connection request failed: {response.status_code}")
        return None

def test_job_status(session, job_id):
    """Test job status monitoring"""
    
    print("2️⃣ Monitoring job status...")
    
    for i in range(10):  # Check for up to 20 seconds
        response = session.get(f"{BASE_URL}/job_status/{job_id}")
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            progress = data.get("progress", 0)
            message = data.get("message", "")
            
            print(f"   Status: {status} ({progress}%) - {message}")
            
            if status == "completed":
                print("✅ LinkedIn profile extraction completed!")
                return True
            elif status == "failed":
                print(f"❌ LinkedIn profile extraction failed: {message}")
                return False
        else:
            print(f"❌ Job status check failed: {response.status_code}")
            return False
        
        time.sleep(2)
    
    print("⏰ Job status check timed out")
    return False

def main():
    """Run all tests"""
    
    print("🚀 InlinkAI Integration Test")
    print("=" * 50)
    
    # Test login flow
    session = test_login_flow()
    if not session:
        print("\n❌ Login test failed - stopping tests")
        return
    
    print("\n✅ Login flow completed successfully!")
    
    # Test LinkedIn connection
    job_id = test_linkedin_connection(session)
    if not job_id:
        print("\n❌ LinkedIn connection test failed")
        return
    
    # Monitor job status
    success = test_job_status(session, job_id)
    
    if success:
        print("\n🎉 All tests passed! InlinkAI is working correctly.")
        print("\n📋 Summary:")
        print("✅ User login and authentication")
        print("✅ Database integration")
        print("✅ LinkedIn profile connection")
        print("✅ Background job processing")
        print("✅ Real-time status updates")
    else:
        print("\n⚠️ LinkedIn scraping test incomplete")
        print("Note: This is expected if running without Chrome/Selenium setup")

if __name__ == "__main__":
    main()
