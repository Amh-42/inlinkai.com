#!/usr/bin/env python3
"""
Chrome Setup Fix for LinkedIn Scraper
This script diagnoses and fixes Chrome/ChromeDriver issues
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def check_chrome_installation():
    """Check if Chrome is properly installed"""
    
    print("🔍 Checking Chrome Installation...")
    print("=" * 40)
    
    # Common Chrome installation paths on Windows
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    
    chrome_found = False
    chrome_path = None
    
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_found = True
            chrome_path = path
            print(f"✅ Chrome found at: {path}")
            
            # Check Chrome version
            try:
                result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    version = result.stdout.strip()
                    print(f"✅ Chrome version: {version}")
                else:
                    print("⚠️ Could not get Chrome version")
            except Exception as e:
                print(f"⚠️ Error getting Chrome version: {e}")
            
            break
    
    if not chrome_found:
        print("❌ Chrome not found in standard locations")
        return False, None
    
    return True, chrome_path

def clear_chromedriver_cache():
    """Clear ChromeDriver cache"""
    
    print("\n🧹 Clearing ChromeDriver Cache...")
    print("=" * 40)
    
    cache_paths = [
        os.path.expanduser("~/.wdm"),
        os.path.expanduser("~/AppData/Local/.wdm"),
        os.path.expanduser("~/AppData/Roaming/.wdm")
    ]
    
    cleared = False
    for cache_path in cache_paths:
        if os.path.exists(cache_path):
            try:
                shutil.rmtree(cache_path)
                print(f"✅ Cleared cache: {cache_path}")
                cleared = True
            except Exception as e:
                print(f"⚠️ Could not clear {cache_path}: {e}")
    
    if not cleared:
        print("ℹ️ No cache found to clear")
    
    return cleared

def test_chromedriver_setup():
    """Test ChromeDriver setup"""
    
    print("\n🧪 Testing ChromeDriver Setup...")
    print("=" * 40)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("✅ Selenium imports successful")
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--log-level=3")
        
        print("✅ Chrome options configured")
        
        # Try to get ChromeDriver
        try:
            print("🔄 Downloading/installing ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            print("✅ ChromeDriver downloaded successfully")
            
            # Try to create driver
            print("🔄 Creating Chrome driver instance...")
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ Chrome driver created successfully")
            
            # Test basic functionality
            print("🔄 Testing basic functionality...")
            driver.get("https://www.google.com")
            title = driver.title
            print(f"✅ Page loaded successfully: {title}")
            
            driver.quit()
            print("✅ Chrome driver test completed successfully")
            
            return True
            
        except Exception as driver_error:
            print(f"❌ ChromeDriver setup failed: {driver_error}")
            return False
            
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        return False

def download_chrome():
    """Guide user to download Chrome"""
    
    print("\n📥 Chrome Download Instructions")
    print("=" * 40)
    print("Chrome is not installed. Please follow these steps:")
    print()
    print("1. Go to: https://www.google.com/chrome/")
    print("2. Click 'Download Chrome'")
    print("3. Run the installer")
    print("4. Restart your computer after installation")
    print("5. Run this script again to test")
    print()

def fix_chrome_issues():
    """Main function to fix Chrome issues"""
    
    print("🔧 Chrome Setup Fix for InlinkAI")
    print("=" * 50)
    
    # Step 1: Check Chrome installation
    chrome_installed, chrome_path = check_chrome_installation()
    
    if not chrome_installed:
        download_chrome()
        return False
    
    # Step 2: Clear cache
    clear_chromedriver_cache()
    
    # Step 3: Test setup
    success = test_chromedriver_setup()
    
    if success:
        print("\n🎉 Chrome Setup Fix SUCCESSFUL!")
        print("✅ Chrome is properly installed")
        print("✅ ChromeDriver is working")
        print("✅ LinkedIn scraping should now work")
        print("\n🚀 You can now use the LinkedIn connection feature!")
        
    else:
        print("\n⚠️ Chrome Setup Still Has Issues")
        print("💡 Try these solutions:")
        print("   1. Restart your computer")
        print("   2. Reinstall Google Chrome")
        print("   3. Run as administrator")
        print("   4. Use Manual Import instead")
        
    return success

if __name__ == "__main__":
    success = fix_chrome_issues()
    
    if success:
        print("\n🧪 Testing LinkedIn Connection...")
        # Test the actual LinkedIn connection
        try:
            import requests
            session = requests.Session()
            
            # Login
            session.post("http://localhost:5000/login", data={"email": "anwar@inlinkai.com"})
            session.post("http://localhost:5000/login_access", data={"otp": "123456"})
            
            # Test LinkedIn connection
            response = session.post(
                "http://localhost:5000/connect_linkedin",
                json={"linkedin_url": "https://linkedin.com/in/testuser"},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✅ LinkedIn connection endpoint working")
                    print("🎉 Complete fix successful!")
                else:
                    print(f"⚠️ LinkedIn connection issue: {data.get('error')}")
            else:
                print(f"❌ LinkedIn connection failed: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Could not test LinkedIn connection: {e}")
            print("Please test manually in the dashboard")
    
    sys.exit(0 if success else 1)
