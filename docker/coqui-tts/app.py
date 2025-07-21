#!/usr/bin/env python3
"""
Musical TTS Singing API Server
Flask application providing REST API for the musical TTS singing service
"""

import os
import base64
import tempfile
import json
import soundfile as sf
from flask import Flask, request, jsonify
from flask_cors import CORS

from musical_singer import MusicalTTSSinger
from tts_engines import GTTS_AVAILABLE, EDGE_TTS_AVAILABLE

app = Flask(__name__)
CORS(app)

# Initialize the musical singer
musical_singer = MusicalTTSSinger()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "musical-tts-singing",
        "model_loaded": True,
        "free_tts_available": musical_singer.free_tts_available,
        "gtts_available": GTTS_AVAILABLE,
        "edge_tts_available": EDGE_TTS_AVAILABLE
    })

@app.route('/generate-singing', methods=['POST'])
def generate_singing():
    try:
        data = request.get_json()
        lyrics = data.get('lyrics', '')
        voice_style = data.get('voice_style', 'pop')
        mood = data.get('mood', 'happy')
        include_music = data.get('include_music', True)  # New parameter for music
        tts_engine = data.get('tts_engine', 'auto')  # Add TTS engine selection
        vocal_volume = data.get('vocal_volume', 0.9)  # Vocal level (0.0-1.0)
        music_volume = data.get('music_volume', 0.15)  # Music level (0.0-1.0)
        
        if not lyrics:
            return jsonify({"error": "No lyrics provided"}), 400
        
        print(f"🎤 Received request: '{lyrics}' ({voice_style}, {mood}) - Music: {include_music}, Engine: {tts_engine}")
        print(f"🎛️ Mix levels - Vocals: {vocal_volume}, Music: {music_volume}")
        
        # Set TTS engine if specified
        if tts_engine != 'auto':
            musical_singer.tts_engines.preferred_engine = tts_engine
        
        # Set mix levels
        musical_singer.audio_processor.vocal_mix_level = vocal_volume
        musical_singer.audio_processor.music_mix_level = music_volume
        
        # Generate singing
        if include_music:
            audio = musical_singer.create_singing_voice(lyrics, voice_style, mood)
            synthesis_method = f"free_tts_musical_with_accompaniment" if musical_singer.free_tts_available else "system_tts_musical_with_accompaniment"
        else:
            # Generate vocals only (existing behavior)
            audio = musical_singer.create_singing_voice_vocals_only(lyrics, voice_style, mood)
            synthesis_method = "free_tts_musical" if musical_singer.free_tts_available else "system_tts_musical"
        
        # Save to temporary file
        temp_path = tempfile.mktemp(suffix='.wav')
        sf.write(temp_path, audio, musical_singer.sample_rate)
        
        # Read and encode
        with open(temp_path, 'rb') as f:
            audio_data = f.read()
        
        os.unlink(temp_path)  # Clean up
        
        # Encode to base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        audio_url = f"data:audio/wav;base64,{audio_base64}"
        
        return jsonify({
            "audio_url": audio_url,
            "format": "wav",
            "duration_seconds": len(audio) / musical_singer.sample_rate,
            "synthesis_method": synthesis_method,
            "voice_style": voice_style,
            "mood": mood,
            "includes_music": include_music,
            "tts_engine": tts_engine,
            "vocal_volume": vocal_volume,
            "music_volume": music_volume
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to generate singing: {str(e)}"}), 500

@app.route('/test-singing', methods=['GET'])
def test_singing():
    try:
        audio = musical_singer.create_singing_voice("Hello world, this is a test", 'pop', 'happy')
        synthesis_method = "free_tts_musical" if musical_singer.free_tts_available else "system_tts_musical"
        return jsonify({
            "status": "success",
            "duration": len(audio) / musical_singer.sample_rate,
            "method": synthesis_method
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🎵 Starting Musical TTS Singing Service...")
    print("🎤 Service ready on port 8002")
    
    if musical_singer.free_tts_available:
        print("✅ FREE TTS enabled - will use Google/Edge TTS + musical effects")
        if GTTS_AVAILABLE:
            print("  🌟 Google TTS (gTTS) available")
        if EDGE_TTS_AVAILABLE:
            print("  🌟 Microsoft Edge TTS available")
    else:
        print("⚠️ No free TTS available - will use system TTS synthesis")
        print("💡 Install free TTS: pip install gtts edge-tts librosa")
    
    app.run(host='0.0.0.0', port=8002, debug=True)
