#!/usr/bin/env python3
"""
ChromeDriver Version Checker and Downloader
This script helps you get the correct ChromeDriver for your Chrome version
"""

import subprocess
import sys
import os
import platform
import requests
import zipfile
import json

def get_chrome_version():
    """Get installed Chrome version"""
    
    print("🔍 Detecting Chrome version...")
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    
    for chrome_path in chrome_paths:
        if os.path.exists(chrome_path):
            try:
                # Get Chrome version
                result = subprocess.run([chrome_path, "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    version_text = result.stdout.strip()
                    # Extract version number (e.g., "Google Chrome 118.0.5993.88" -> "118.0.5993.88")
                    version = version_text.split()[-1]
                    print(f"✅ Found Chrome version: {version}")
                    print(f"✅ Chrome location: {chrome_path}")
                    return version
                    
            except Exception as e:
                print(f"⚠️ Error getting version from {chrome_path}: {e}")
                continue
    
    print("❌ Chrome not found or version detection failed")
    return None

def get_system_architecture():
    """Detect system architecture"""
    
    arch = platform.machine().lower()
    is_64bit = platform.architecture()[0] == '64bit'
    
    print(f"🖥️ System architecture: {arch}")
    print(f"🖥️ 64-bit system: {is_64bit}")
    
    if is_64bit and 'amd64' in arch or 'x86_64' in arch:
        return 'win64'
    else:
        return 'win32'

def get_compatible_chromedriver_version(chrome_version):
    """Get compatible ChromeDriver version for Chrome version"""
    
    print(f"🔍 Finding compatible ChromeDriver for Chrome {chrome_version}...")
    
    try:
        # Get major version (e.g., "118.0.5993.88" -> "118")
        major_version = chrome_version.split('.')[0]
        
        # ChromeDriver endpoint for version mapping
        url = f"https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_{major_version}"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            driver_version = response.text.strip()
            print(f"✅ Compatible ChromeDriver version: {driver_version}")
            return driver_version
        else:
            print(f"⚠️ Could not get version mapping, status: {response.status_code}")
            # Fallback: use Chrome version as-is
            return chrome_version
            
    except Exception as e:
        print(f"⚠️ Error getting ChromeDriver version: {e}")
        # Fallback: use Chrome version as-is
        return chrome_version

def download_chromedriver(version, architecture):
    """Download the correct ChromeDriver"""
    
    print(f"📥 Downloading ChromeDriver {version} for {architecture}...")
    
    try:
        # ChromeDriver download URL
        download_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/{architecture}/chromedriver-{architecture}.zip"
        
        print(f"🔗 Download URL: {download_url}")
        
        # Download the zip file
        response = requests.get(download_url, timeout=30)
        
        if response.status_code == 200:
            zip_filename = f"chromedriver-{version}-{architecture}.zip"
            
            # Save zip file
            with open(zip_filename, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Downloaded: {zip_filename}")
            
            # Extract chromedriver.exe
            with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
                # Find chromedriver.exe in the zip
                for file_info in zip_ref.filelist:
                    if file_info.filename.endswith('chromedriver.exe'):
                        # Extract to current directory as chromedriver.exe
                        with zip_ref.open(file_info) as source, open('chromedriver.exe', 'wb') as target:
                            target.write(source.read())
                        
                        print(f"✅ Extracted: chromedriver.exe")
                        
                        # Make executable (on Unix systems)
                        if os.name != 'nt':
                            os.chmod('chromedriver.exe', 0o755)
                        
                        # Clean up zip file
                        os.remove(zip_filename)
                        print(f"🧹 Cleaned up: {zip_filename}")
                        
                        return True
            
            print("❌ chromedriver.exe not found in zip file")
            return False
            
        else:
            print(f"❌ Download failed, status code: {response.status_code}")
            print("💡 Try downloading manually from: https://chromedriver.chromium.org/")
            return False
            
    except Exception as e:
        print(f"❌ Download error: {e}")
        return False

def test_chromedriver():
    """Test if the ChromeDriver works"""
    
    if not os.path.exists('chromedriver.exe'):
        print("❌ chromedriver.exe not found")
        return False
    
    print("🧪 Testing ChromeDriver...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--log-level=3")
        
        # Test ChromeDriver
        service = Service('./chromedriver.exe')
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Simple test
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"✅ ChromeDriver test successful! Page title: {title}")
        return True
        
    except Exception as e:
        print(f"❌ ChromeDriver test failed: {e}")
        return False

def main():
    """Main function"""
    
    print("🚀 ChromeDriver Setup Assistant")
    print("=" * 50)
    
    # Step 1: Get Chrome version
    chrome_version = get_chrome_version()
    if not chrome_version:
        print("\n❌ Cannot proceed without Chrome version")
        print("💡 Please install Google Chrome first")
        return False
    
    # Step 2: Get system architecture
    architecture = get_system_architecture()
    
    # Step 3: Get compatible ChromeDriver version
    driver_version = get_compatible_chromedriver_version(chrome_version)
    
    # Step 4: Check if we already have the right version
    current_driver = './chromedriver.exe'
    if os.path.exists(current_driver):
        print(f"\n📁 Found existing chromedriver.exe")
        
        # Test current driver
        if test_chromedriver():
            print("🎉 Current ChromeDriver is working! No download needed.")
            return True
        else:
            print("⚠️ Current ChromeDriver is not working, downloading new one...")
            os.remove(current_driver)
    
    # Step 5: Download correct ChromeDriver
    print(f"\n📥 Downloading ChromeDriver...")
    print(f"   Chrome Version: {chrome_version}")
    print(f"   Driver Version: {driver_version}")
    print(f"   Architecture: {architecture}")
    
    success = download_chromedriver(driver_version, architecture)
    
    if success:
        # Step 6: Test the downloaded driver
        if test_chromedriver():
            print("\n🎉 SUCCESS! ChromeDriver setup complete!")
            print("✅ LinkedIn scraping should now work properly")
            return True
        else:
            print("\n⚠️ Download successful but driver test failed")
            print("💡 You may need to manually download from https://chromedriver.chromium.org/")
            return False
    else:
        print("\n❌ Download failed")
        print("💡 Manual download instructions:")
        print(f"   1. Go to: https://chromedriver.chromium.org/")
        print(f"   2. Download ChromeDriver {driver_version} for {architecture}")
        print(f"   3. Extract chromedriver.exe to this directory")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🧪 Testing LinkedIn Connection...")
        # Quick test of the LinkedIn connection
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
                    print("🎉 LinkedIn connection endpoint working!")
                    print("✅ Complete setup successful!")
                else:
                    print(f"⚠️ LinkedIn connection issue: {data.get('error')}")
            else:
                print(f"❌ LinkedIn connection failed: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Could not test LinkedIn connection: {e}")
            print("Please test manually in the dashboard")
    
    sys.exit(0 if success else 1)
