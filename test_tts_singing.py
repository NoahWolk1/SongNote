#!/usr/bin/env python3
"""
Test the new TTS-based singing approach
"""

import requests
import json
import base64
import time

def test_tts_singing(lyrics, style, mood, filename):
    """Test TTS-based singing generation"""
    print(f"\n🎤 Testing TTS singing: '{lyrics}' ({style}, {mood})")
    
    response = requests.post(
        'http://localhost:8002/generate-singing',
        json={
            'lyrics': lyrics,
            'voice_style': style,
            'mood': mood
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        duration = data['duration_seconds']
        method = data['synthesis_method']
        
        print(f"✅ Generated {duration:.1f}s of {method}")
        
        # Save audio
        audio_url = data['audio_url']
        if audio_url.startswith('data:audio/wav;base64,'):
            audio_base64 = audio_url[len('data:audio/wav;base64,'):]
            audio_data = base64.b64decode(audio_base64)
            
            with open(filename, 'wb') as f:
                f.write(audio_data)
            print(f"💾 Saved to {filename}")
        
        return True
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return False

def main():
    print("🎤 Testing TTS-Based Singing Synthesis")
    print("=" * 50)
    
    # Test simple words for clarity
    test_cases = [
        ("Hello", "pop", "happy", "tts_hello.wav"),
        ("World", "pop", "happy", "tts_world.wav"),
        ("Hello world", "pop", "happy", "tts_hello_world.wav"),
        ("Testing one two three", "pop", "happy", "tts_counting.wav"),
        ("This is a test", "ballad", "happy", "tts_test_ballad.wav"),
        ("Love me do", "ballad", "happy", "tts_love_me_do.wav"),
    ]
    
    success_count = 0
    for lyrics, style, mood, filename in test_cases:
        if test_tts_singing(lyrics, style, mood, filename):
            success_count += 1
        time.sleep(1)
    
    print(f"\n🎉 Completed {success_count}/{len(test_cases)} TTS tests!")
    print("\n🎵 This approach:")
    print("  ✓ Uses system TTS (macOS 'say' command) for clear speech")
    print("  ✓ Applies pitch shifting to match musical melody")
    print("  ✓ Adds musical timing and effects")
    print("  ✓ Should produce recognizable words")

if __name__ == '__main__':
    main()
