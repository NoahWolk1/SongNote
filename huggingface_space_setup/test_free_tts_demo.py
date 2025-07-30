#!/usr/bin/env python3
"""
Test the FREE TTS Singing Service
Demonstrates no-cost TTS singing using Google and Microsoft Edge TTS
"""

import requests
import json
import base64
import os

def test_free_tts_singing():
    """Test the free TTS singing service"""
    
    # Test phrases
    test_phrases = [
        {"lyrics": "Hello world, this costs nothing at all", "style": "pop", "mood": "happy"},
        {"lyrics": "Free as a bird, flying high in the sky", "style": "ballad", "mood": "dreamy"},
        {"lyrics": "No money needed, just beautiful singing", "style": "pop", "mood": "excited"}
    ]
    
    print("🎵 Testing FREE TTS Singing Service")
    print("=" * 50)
    
    # Check service health
    try:
        health_response = requests.get("http://localhost:8002/health", timeout=10)
        health_data = health_response.json()
        
        print("✅ Service Status:")
        print(f"   - Service: {health_data['status']}")
        print(f"   - Google TTS: {'✅' if health_data.get('gtts_available') else '❌'}")
        print(f"   - Edge TTS: {'✅' if health_data.get('edge_tts_available') else '❌'}")
        print(f"   - Free TTS: {'✅' if health_data.get('free_tts_available') else '❌'}")
        print()
        
        if not health_data.get('free_tts_available'):
            print("❌ Free TTS not available!")
            return
            
    except Exception as e:
        print(f"❌ Service health check failed: {e}")
        return
    
    # Test each phrase
    for i, test_case in enumerate(test_phrases, 1):
        print(f"🎤 Test {i}: '{test_case['lyrics']}'")
        print(f"   Style: {test_case['style']}, Mood: {test_case['mood']}")
        
        try:
            # Make request
            response = requests.post(
                "http://localhost:8002/generate-singing",
                json=test_case,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                duration = result.get('duration_seconds', 0)
                method = result.get('synthesis_method', 'unknown')
                
                print(f"   ✅ Success! Duration: {duration:.1f}s, Method: {method}")
                
                # Save audio file
                if 'audio_url' in result:
                    audio_data = result['audio_url']
                    if audio_data.startswith('data:audio/wav;base64,'):
                        # Extract base64 data
                        base64_data = audio_data.split(',')[1]
                        audio_bytes = base64.b64decode(base64_data)
                        
                        # Save to file
                        filename = f"free_tts_test_{i}.wav"
                        with open(filename, 'wb') as f:
                            f.write(audio_bytes)
                        
                        print(f"   💾 Saved as: {filename}")
                        
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    print("🎉 Free TTS Testing Complete!")
    print("💰 Total cost: $0.00 (completely free!)")

if __name__ == "__main__":
    test_free_tts_singing()
