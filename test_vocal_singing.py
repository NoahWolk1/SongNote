#!/usr/bin/env python3
"""
Test the new vocal phonetic singing synthesis
"""

import requests
import json
import base64
import time

def test_vocal_singing(lyrics, style, mood, filename):
    """Test vocal singing generation and save to file"""
    print(f"\n🎤 Testing vocal synthesis: '{lyrics}' ({style}, {mood})")
    
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
        
        print(f"✅ Generated {duration:.1f}s of {method} vocal singing")
        
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
    print("🎤 Testing Vocal Phonetic Singing Synthesis")
    print("=" * 50)
    
    # Test cases focusing on recognizable words
    test_cases = [
        # Simple words with clear vowels
        ("Hello world", "pop", "happy", "vocal_hello_world.wav"),
        
        # Words with different vowel sounds
        ("Love me do", "ballad", "happy", "vocal_love_me_do.wav"),
        
        # Test with consonant sounds
        ("This is a test", "pop", "happy", "vocal_this_test.wav"),
        
        # Longer phrase for verse pattern
        ("Walking down the street", "pop", "happy", "vocal_walking_street.wav"),
        
        # Ballad with emotional words
        ("Time to feel good", "ballad", "happy", "vocal_time_feel.wav"),
        
        # Test articulation
        ("Feel the love tonight", "ballad", "happy", "vocal_feel_love.wav")
    ]
    
    success_count = 0
    for lyrics, style, mood, filename in test_cases:
        if test_vocal_singing(lyrics, style, mood, filename):
            success_count += 1
        time.sleep(1)
    
    print(f"\n🎉 Completed {success_count}/{len(test_cases)} vocal tests successfully!")
    print("\n🎵 New vocal features:")
    print("  ✓ Formant-based vowel synthesis (ah, eh, ih, oh, oo, etc.)")
    print("  ✓ Consonant articulation (plosives, fricatives)")
    print("  ✓ Syllable-based phonetic breakdown")
    print("  ✓ Natural vocal envelope and vibrato")
    print("  ✓ Word-specific vowel mapping")
    print("  ✓ Harmonic series for vocal richness")

if __name__ == '__main__':
    main()
