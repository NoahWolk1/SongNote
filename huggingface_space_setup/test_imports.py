#!/usr/bin/env python3
"""
Test script to verify all AI singing modules can be imported correctly
"""

print("🧪 Testing AI singing module imports...")

try:
    print("📦 Importing musical_singer...")
    from musical_singer import MusicalTTSSinger
    print("✅ musical_singer imported successfully")
    
    print("📦 Importing tts_engines...")
    from tts_engines import GTTS_AVAILABLE, EDGE_TTS_AVAILABLE
    print("✅ tts_engines imported successfully")
    
    print("📦 Importing text_analysis...")
    from text_analysis import TextAnalyzer
    print("✅ text_analysis imported successfully")
    
    print("📦 Importing musical_arrangement...")
    from musical_arrangement import MusicalArranger
    print("✅ musical_arrangement imported successfully")
    
    print("📦 Importing audio_processing...")
    from audio_processing import AudioProcessor
    print("✅ audio_processing imported successfully")
    
    print("\n🎵 Testing MusicalTTSSinger initialization...")
    musical_singer = MusicalTTSSinger()
    print("✅ MusicalTTSSinger initialized successfully")
    
    print(f"🎤 Free TTS available: {musical_singer.free_tts_available}")
    print(f"🎤 gTTS available: {GTTS_AVAILABLE}")
    print(f"🎤 Edge TTS available: {EDGE_TTS_AVAILABLE}")
    
    print("\n🎵 Testing basic singing generation...")
    test_audio = musical_singer.create_singing_voice("Hello world", 'pop', 'happy')
    print(f"✅ Generated audio: {len(test_audio)} samples")
    
    print("\n🎉 All imports and basic functionality working!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 