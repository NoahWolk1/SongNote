#!/usr/bin/env python3
"""
Diagnostic script for Hugging Face Space issues
"""

import requests
import time

def check_space_status():
    """Check the status of the Hugging Face Space"""
    print("🔍 Diagnosing Hugging Face Space...")
    print("=" * 50)
    
    # Test different possible URLs
    urls_to_test = [
        "https://rocketlaunchers-ai-singer.hf.space",
        "https://rocketlaunchers-ai_singer.hf.space", 
        "https://rocketlaunchers-ai-singer.hf.space/",
        "https://rocketlaunchers-ai_singer.hf.space/"
    ]
    
    for url in urls_to_test:
        print(f"\n🌐 Testing: {url}")
        try:
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text[:200]
                if "FastAPI" in content or "AI Singer" in content:
                    print("   ✅ Found working API!")
                    return url
                elif "404" in content:
                    print("   ❌ 404 - Space not found or not built")
                else:
                    print(f"   📄 Content preview: {content[:100]}...")
            elif response.status_code == 404:
                print("   ❌ 404 - Space not found")
            elif response.status_code == 502:
                print("   🔄 502 - Space is building")
            else:
                print(f"   ⚠️ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None

def check_space_page():
    """Check the Space page for build status"""
    print("\n📋 Checking Space page...")
    try:
        response = requests.get("https://huggingface.co/spaces/Rocketlaunchers/AI_Singer", timeout=10)
        content = response.text
        
        # Look for build status indicators
        if "Building" in content:
            print("   🔄 Space is currently building")
        elif "Running" in content:
            print("   ✅ Space is running")
        elif "Error" in content:
            print("   ❌ Space has build errors")
        else:
            print("   ⚠️ Could not determine build status")
            
        # Look for files
        if "Dockerfile" in content:
            print("   ✅ Dockerfile found")
        if "app.py" in content:
            print("   ✅ app.py found")
        if "requirements.txt" in content:
            print("   ✅ requirements.txt found")
            
    except Exception as e:
        print(f"   ❌ Error checking Space page: {e}")

def main():
    """Run diagnostics"""
    print("🧪 Hugging Face Space Diagnostics")
    print("=" * 50)
    
    # Check Space page
    check_space_page()
    
    # Test URLs
    working_url = check_space_status()
    
    print("\n" + "=" * 50)
    if working_url:
        print(f"🎉 Found working URL: {working_url}")
        print("✅ Your Space is working!")
    else:
        print("❌ No working URL found")
        print("\n💡 Possible issues:")
        print("   1. Space is still building (wait 5-10 minutes)")
        print("   2. Build failed (check logs in Space)")
        print("   3. Files not uploaded correctly")
        print("   4. Wrong URL format")
        
        print("\n🔧 Next steps:")
        print("   1. Go to: https://huggingface.co/spaces/Rocketlaunchers/AI_Singer")
        print("   2. Check the 'Logs' tab for build errors")
        print("   3. Make sure all files are uploaded")
        print("   4. Wait for build to complete")

if __name__ == "__main__":
    main() 