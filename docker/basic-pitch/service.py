#!/usr/bin/env python3
"""
FREE Basic Pitch Service - Melody extraction from humming
Uses Spotify's open-source Basic Pitch model (completely free)
"""

import os
import base64
import tempfile
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import librosa
import soundfile as sf
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "basic-pitch"})

@app.route('/extract-melody', methods=['POST'])
def extract_melody():
    try:
        data = request.get_json()
        audio_base64 = data.get('audio')
        
        if not audio_base64:
            return jsonify({"error": "No audio data provided"}), 400
        
        # Decode base64 audio
        audio_data = base64.b64decode(audio_base64)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
        
        try:
            # Load audio using librosa
            audio, sample_rate = librosa.load(temp_path, sr=22050)
            
            # Use Basic Pitch to extract melody (FREE!)
            model_output, midi_data, note_events = predict(
                audio_path=temp_path,
                model_path=ICASSP_2022_MODEL_PATH
            )
            
            # Extract notes from the MIDI data
            notes = []
            if note_events is not None and len(note_events) > 0:
                for note in note_events:
                    notes.append({
                        "pitch": int(note[2]),  # MIDI note number
                        "start_time": float(note[0]),  # Start time in seconds
                        "end_time": float(note[1]),    # End time in seconds
                        "velocity": int(note[3]) if len(note) > 3 else 80
                    })
            
            # Estimate tempo and key (basic analysis)
            tempo, _ = librosa.beat.beat_track(y=audio, sr=sample_rate)
            chroma = librosa.feature.chroma_stft(y=audio, sr=sample_rate)
            key_index = np.argmax(np.mean(chroma, axis=1))
            keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            estimated_key = keys[key_index]
            
            melody_data = {
                "notes": notes,
                "tempo": float(tempo),
                "key": f"{estimated_key} major"
            }
            
            return jsonify(melody_data)
            
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        print(f"Error extracting melody: {str(e)}")
        return jsonify({"error": f"Failed to extract melody: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8001))
    print(f"Starting Basic Pitch service on port {port}")
    print("This service is completely FREE using Spotify's open-source Basic Pitch")
    app.run(host='0.0.0.0', port=port, debug=False)
