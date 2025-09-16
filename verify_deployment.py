#!/usr/bin/env python3
"""
Deployment verification script
Run this to test all endpoints and verify no 500 errors
"""

import requests
import json
import sys

def test_endpoint(url, expected_status=200, method='GET', data=None):
    """Test a single endpoint"""
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        
        status = response.status_code
        success = status == expected_status or (200 <= status < 400)
        
        print(f"{'✅' if success else '❌'} {method} {url} - Status: {status}")
        
        if not success:
            print(f"   Response: {response.text[:200]}...")
            
        return success
    except Exception as e:
        print(f"❌ {method} {url} - Error: {e}")
        return False

def verify_deployment(base_url):
    """Verify all critical endpoints"""
    
    print(f'🔍 Testing InlinkAI Deployment: {base_url}')
    print('=' * 60)
    
    endpoints = [
        # Public pages
        ('GET', '/', 200),
        ('GET', '/health', 200),
        ('GET', '/features', 200),
        ('GET', '/login', 200),
        
        # Static assets
        ('GET', '/static/css/style.css', 200),
        ('GET', '/static/js/main.js', 200),
        ('GET', '/static/images/logo.svg', 200),
        
    ]
    
    passed = 0
    total = len(endpoints)
    
    for method, endpoint, expected in endpoints:
        url = f"{base_url.rstrip('/')}{endpoint}"
        
        if isinstance(expected, list):
            # Multiple acceptable status codes
            success = False
            for exp_status in expected:
                if test_endpoint(url, exp_status, method):
                    success = True
                    break
            if success:
                passed += 1
        else:
            if test_endpoint(url, expected, method):
                passed += 1
    
    print('\n' + '=' * 60)
    print(f'📊 Results: {passed}/{total} endpoints passed')
    
    if passed == total:
        print('🎉 All endpoints working correctly!')
        print('✅ Deployment verification PASSED')
        return True
    else:
        print('⚠️  Some endpoints failed')
        print('❌ Deployment verification FAILED')
        return False

if __name__ == '__main__':
    # Default to localhost for testing
    base_url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:5000'
    
    print(f'Testing deployment at: {base_url}')
    success = verify_deployment(base_url)
    
    if not success:
        print('\n💡 Tips:')
        print('- Check cPanel error logs')
        print('- Verify all dependencies installed')
        print('- Confirm database connection')
        print('- Check file permissions')
        
    sys.exit(0 if success else 1)
