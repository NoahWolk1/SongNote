#!/usr/bin/env python3
"""
Test script for the Hugging Face Space AI Singer API
"""

import requests
import json
import time

# Your Hugging Face Space URL
API_BASE_URL = "https://rocketlaunchers-ai-singer.hf.space"

def test_health():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed!")
            print(f"   Status: {data.get('status')}")
            print(f"   Free TTS available: {data.get('free_tts_available')}")
            print(f"   gTTS available: {data.get('gtts_available')}")
            print(f"   Edge TTS available: {data.get('edge_tts_available')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_root():
    """Test the root endpoint"""
    print("\n🏠 Testing root endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint working!")
            print(f"   Message: {data.get('message')}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def test_singing_generation():
    """Test singing generation"""
    print("\n🎤 Testing singing generation...")
    
    test_data = {
        "lyrics": "Hello world, this is a test song",
        "voice_style": "pop",
        "mood": "happy",
        "include_music": True,
        "tts_engine": "auto",
        "vocal_volume": 0.9,
        "music_volume": 0.15
    }
    
    try:
        print("   Sending request...")
        response = requests.post(
            f"{API_BASE_URL}/generate-singing",
            json=test_data,
            timeout=60  # Longer timeout for audio generation
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Singing generation successful!")
            print(f"   Duration: {data.get('duration_seconds', 0):.2f} seconds")
            print(f"   Format: {data.get('format')}")
            print(f"   Voice style: {data.get('voice_style')}")
            print(f"   Mood: {data.get('mood')}")
            print(f"   Includes music: {data.get('includes_music')}")
            print(f"   Synthesis method: {data.get('synthesis_method')}")
            
            # Check if audio URL is present
            audio_url = data.get('audio_url', '')
            if audio_url and audio_url.startswith('data:audio/wav;base64,'):
                print("✅ Audio URL generated successfully!")
                print(f"   Audio URL length: {len(audio_url)} characters")
            else:
                print("⚠️ Audio URL missing or invalid")
            
            return True
        else:
            print(f"❌ Singing generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Singing generation error: {e}")
        return False

def test_simple_singing():
    """Test simple singing generation"""
    print("\n🎵 Testing simple singing generation...")
    
    test_data = {
        "lyrics": "Testing one two three",
        "voice_style": "pop",
        "mood": "happy",
        "include_music": False,  # Just vocals
        "tts_engine": "auto"
    }
    
    try:
        print("   Sending request...")
        response = requests.post(
            f"{API_BASE_URL}/generate-singing",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Simple singing generation successful!")
            print(f"   Duration: {data.get('duration_seconds', 0):.2f} seconds")
            print(f"   Synthesis method: {data.get('synthesis_method')}")
            return True
        else:
            print(f"❌ Simple singing generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Simple singing generation error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Hugging Face Space AI Singer API")
    print("=" * 50)
    print(f"🌐 API URL: {API_BASE_URL}")
    print()
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Simple Singing", test_simple_singing),
        ("Full Singing", test_singing_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your API is working correctly.")
        print("✅ Your Expo app should now be able to generate songs!")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        print("💡 Make sure your Hugging Face Space is built and running.")

if __name__ == "__main__":
    main() 