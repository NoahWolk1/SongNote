#!/usr/bin/env python3
"""
Test the improved singing service
"""

import requests
import json
import base64
import wave
import tempfile
import os

def test_singing_service(lyrics, style="pop", mood="happy"):
    """Test the singing service and save the audio"""
    
    print(f"🎤 Testing singing: '{lyrics}' ({style}, {mood})")
    
    # Call the singing service
    response = requests.post('http://localhost:8002/generate-singing', json={
        "lyrics": lyrics,
        "voice_style": style,
        "mood": mood
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Generated {result['duration_seconds']:.1f}s of {result['synthesis_method']}")
        
        # Extract audio data
        audio_url = result['audio_url']
        if audio_url.startswith('data:audio/wav;base64,'):
            audio_base64 = audio_url.split(',')[1]
            audio_data = base64.b64decode(audio_base64)
            
            # Save to file
            filename = f"test_singing_{style}_{mood}.wav"
            with open(filename, 'wb') as f:
                f.write(audio_data)
            
            print(f"💾 Saved audio to: {filename}")
            return filename
        else:
            print("❌ Unexpected audio format")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    return None

if __name__ == "__main__":
    print("🎵 Testing Improved Musical TTS Singing Service")
    print("=" * 50)
    
    # Test different phrases and styles
    tests = [
        ("Hello world", "pop", "happy"),
        ("This is a beautiful day", "ballad", "happy"),
        ("Love is in the air tonight", "pop", "happy"),
        ("Amazing grace how sweet the sound", "ballad", "happy")
    ]
    
    for lyrics, style, mood in tests:
        filename = test_singing_service(lyrics, style, mood)
        if filename:
            print(f"▶️  Play: {filename}")
        print()
    
    print("🎉 Testing complete!")
    print("The new service should sound more natural with:")
    print("- Less harsh oscillations")
    print("- More speech-like tones") 
    print("- Smoother pitch transitions")
    print("- Natural vocal characteristics")
