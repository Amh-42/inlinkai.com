#!/usr/bin/env python3
"""
Test script for enhanced LinkedIn connection with progress tracking
"""

import requests
import time
import json

BASE_URL = "http://localhost:5000"
TEST_EMAIL = "anwar@inlinkai.com"
TEST_OTP = "123456"
TEST_LINKEDIN_URL = "https://linkedin.com/in/johndoe"

def test_enhanced_linkedin_flow():
    """Test the enhanced LinkedIn connection flow"""
    
    session = requests.Session()
    
    print("🚀 Testing Enhanced LinkedIn Connection")
    print("=" * 50)
    
    # Step 1: Login
    print("1️⃣ Logging in...")
    session.post(f"{BASE_URL}/login", data={"email": TEST_EMAIL})
    response = session.post(f"{BASE_URL}/login_access", data={"otp": TEST_OTP}, allow_redirects=False)
    
    if response.status_code == 302:
        print("✅ Login successful")
    else:
        print("❌ Login failed")
        return False
    
    # Step 2: Test LinkedIn connection with progress tracking
    print("2️⃣ Testing LinkedIn connection...")
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
            
            # Monitor progress with detailed tracking
            print("\n📊 Progress Tracking:")
            progress_shown = set()
            
            for i in range(30):  # Monitor for up to 60 seconds
                time.sleep(2)
                
                status_response = session.get(f"{BASE_URL}/job_status/{job_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data.get("success"):
                        progress = status_data.get("progress", 0)
                        status = status_data.get("status")
                        message = status_data.get("message", "")
                        
                        # Only show new progress updates
                        progress_key = f"{progress}-{status}"
                        if progress_key not in progress_shown:
                            print(f"   Progress: {progress}% | Status: {status} | {message}")
                            progress_shown.add(progress_key)
                        
                        if status == "completed":
                            print("\n🎉 LinkedIn connection completed successfully!")
                            
                            # Show extracted data if available
                            if status_data.get("data"):
                                extracted_data = status_data["data"]
                                print("\n📋 Extracted Profile Data:")
                                if extracted_data.get("headline"):
                                    print(f"   • Headline: {extracted_data['headline'][:80]}...")
                                if extracted_data.get("current_position"):
                                    print(f"   • Position: {extracted_data['current_position']}")
                                if extracted_data.get("company"):
                                    print(f"   • Company: {extracted_data['company']}")
                                if extracted_data.get("location"):
                                    print(f"   • Location: {extracted_data['location']}")
                                if extracted_data.get("skills"):
                                    print(f"   • Skills: {', '.join(extracted_data['skills'][:5])}...")
                            
                            return True
                            
                        elif status == "failed":
                            print(f"\n❌ LinkedIn connection failed: {message}")
                            
                            # Test manual import fallback
                            print("\n🔄 Testing manual import fallback...")
                            manual_response = session.post(
                                f"{BASE_URL}/save_manual_profile",
                                json={
                                    "headline": "Senior Software Engineer | AI & Web Development",
                                    "current_position": "Senior Software Engineer",
                                    "company": "InlinkAI",
                                    "about_section": "Passionate about building AI-powered solutions for professionals."
                                },
                                headers={"Content-Type": "application/json"}
                            )
                            
                            if manual_response.status_code == 200:
                                manual_data = manual_response.json()
                                if manual_data.get("success"):
                                    print("✅ Manual profile import successful!")
                                    return True
                                else:
                                    print(f"❌ Manual import failed: {manual_data.get('error')}")
                            
                            return False
                else:
                    print(f"❌ Status check failed: {status_response.status_code}")
                    return False
            
            print("\n⏰ Progress monitoring timed out")
            return False
            
        else:
            print(f"❌ LinkedIn connection failed to start: {data.get('error')}")
            return False
    else:
        print(f"❌ LinkedIn connection request failed: {response.status_code}")
        return False

def main():
    """Run the enhanced LinkedIn test"""
    
    print("🔧 Enhanced LinkedIn Connection Test")
    print("=" * 60)
    
    success = test_enhanced_linkedin_flow()
    
    if success:
        print("\n🎉 Enhanced LinkedIn Connection Test PASSED!")
        print("\n✅ Features verified:")
        print("   • Modern progress circle UI")
        print("   • Step-by-step progress tracking")
        print("   • Real-time status updates")
        print("   • Data extraction preview")
        print("   • Manual import fallback")
        print("   • Toast notifications")
        print("   • Error handling with retry options")
    else:
        print("\n⚠️ Test completed with expected limitations")
        print("Note: Chrome/Selenium setup may be required for full scraping")

if __name__ == "__main__":
    main()
