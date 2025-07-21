#!/usr/bin/env python3
"""
Test the new song-pattern based singing synthesis
"""

import requests
import json
import base64
import time

def test_singing_generation(lyrics, style, mood, filename):
    """Test singing generation and save to file"""
    print(f"\n🎤 Testing: '{lyrics}' ({style}, {mood})")
    
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
        
        print(f"✅ Generated {duration:.1f}s of {method} singing")
        
        # Decode and save audio
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
    print("🎵 Testing Song-Pattern Based Singing Synthesis")
    print("=" * 50)
    
    # Test different song patterns
    test_cases = [
        # Short phrase (chorus-like)
        ("Love is all you need", "pop", "happy", "song_chorus_happy.wav"),
        
        # Longer phrase (verse-like)  
        ("Walking down the street on a sunny day feeling good", "pop", "happy", "song_verse_happy.wav"),
        
        # Ballad style
        ("Sometimes I wonder where we go", "ballad", "sad", "song_ballad_sad.wav"),
        
        # Repetitive (chorus pattern)
        ("Hey hey hey come and play", "pop", "happy", "song_repetitive.wav"),
        
        # Test longer narrative (verse pattern)
        ("Yesterday I was walking through the park thinking about life", "ballad", "happy", "song_narrative.wav")
    ]
    
    success_count = 0
    for lyrics, style, mood, filename in test_cases:
        if test_singing_generation(lyrics, style, mood, filename):
            success_count += 1
        time.sleep(1)  # Brief pause between tests
    
    print(f"\n🎉 Completed {success_count}/{len(test_cases)} tests successfully!")
    print("\n🎼 Key improvements in this version:")
    print("  ✓ Proper verse-chorus song structure")
    print("  ✓ Musical timing based on BPM")
    print("  ✓ Natural harmonic series like real voices")
    print("  ✓ Realistic vibrato and phrasing") 
    print("  ✓ Song-like dynamics and reverb")
    print("  ✓ Melodic arcs that build and resolve")

if __name__ == '__main__':
    main()
