#!/usr/bin/env python3
"""
Simple Singing Voice Synthesis Service
Uses harmonic synthesis with vocal characteristics for actual singing
"""

import os
import base64
import tempfile
import json
import math
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import soundfile as sf
from scipy import signal

app = Flask(__name__)
CORS(app)

class SimpleSingingVoice:
    """Simple but effective singing voice synthesizer"""
    
    def __init__(self):
        self.sample_rate = 22050
        
    def create_singing_voice(self, text, voice_style='ballad', mood='happy'):
        """Create actual singing audio from text"""
        print(f"🎵 Generating singing for: '{text}' in {voice_style} style, {mood} mood")
        
        # Basic parameters
        duration = max(3.0, len(text) * 0.2)  # At least 3 seconds
        samples = int(duration * self.sample_rate)
        time = np.linspace(0, duration, samples)
        
        # Voice style frequency ranges
        freq_ranges = {
            'ballad': (180, 350),
            'pop': (200, 400),
            'rock': (220, 450),
            'jazz': (160, 320),
            'opera': (240, 500)
        }
        
        f_min, f_max = freq_ranges.get(voice_style, freq_ranges['pop'])
        
        # Create a simple melody line
        base_freq = (f_min + f_max) / 2
        
        # Generate melody with musical intervals
        melody_notes = [0, 2, 4, 5, 7, 9, 11]  # Major scale intervals
        note_duration = duration / len(text.split())
        
        melody = []
        for i, word in enumerate(text.split()):
            note_index = i % len(melody_notes)
            semitone_offset = melody_notes[note_index]
            frequency = base_freq * (2 ** (semitone_offset / 12))  # Convert semitones to frequency
            
            # Add slight variation for each word
            word_samples = int(note_duration * self.sample_rate)
            word_time = np.linspace(0, note_duration, word_samples)
            
            # Add vibrato (essential for singing)
            vibrato = 1 + 0.05 * np.sin(2 * np.pi * word_time * 6)  # 6Hz vibrato
            freq_with_vibrato = frequency * vibrato
            
            melody.extend(freq_with_vibrato)
        
        # Ensure melody matches time array length
        melody = np.array(melody)
        if len(melody) < len(time):
            melody = np.pad(melody, (0, len(time) - len(melody)), mode='constant', constant_values=melody[-1])
        elif len(melody) > len(time):
            melody = melody[:len(time)]
        
        # Generate harmonics for human voice
        audio = np.zeros_like(time)
        
        # Harmonic series with formant-like characteristics
        harmonics = [1.0, 0.8, 0.6, 0.4, 0.3, 0.2, 0.15, 0.1]
        
        for h, amplitude in enumerate(harmonics, 1):
            harmonic_freq = melody * h
            
            # Add some frequency modulation for naturalness
            fm_mod = 1 + 0.01 * np.sin(2 * np.pi * time * (3 + h))
            harmonic_freq *= fm_mod
            
            # Generate the harmonic
            phase = 2 * np.pi * np.cumsum(harmonic_freq) / self.sample_rate
            harmonic_wave = amplitude * np.sin(phase)
            
            # Apply formant filtering for vocal tract simulation
            if h <= 3:  # Only filter lower harmonics strongly
                harmonic_wave = self.apply_formant_filter(harmonic_wave, h)
            
            audio += harmonic_wave
        
        # Apply vocal envelope (breathing, articulation)
        envelope = self.create_vocal_envelope(time, text)
        audio *= envelope
        
        # Add resonance and warmth
        audio = self.add_vocal_resonance(audio)
        
        # Dynamic processing
        audio = self.apply_singing_dynamics(audio, voice_style, mood)
        
        # Normalize
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val * 0.8
        
        print(f"✅ Generated {duration:.1f}s of singing audio")
        return audio
    
    def apply_formant_filter(self, audio, harmonic_num):
        """Apply formant filtering to simulate vocal tract"""
        # Simplified formant frequencies for singing
        formants = [600, 1200, 2400]  # F1, F2, F3
        
        filtered = audio.copy()
        for i, formant in enumerate(formants):
            if i < harmonic_num:
                # Create a bandpass filter around the formant
                try:
                    sos = signal.butter(2, [formant-150, formant+150], 
                                      btype='band', fs=self.sample_rate, output='sos')
                    formant_emphasis = signal.sosfilt(sos, audio) * 0.3
                    filtered += formant_emphasis
                except:
                    pass  # Skip if filter design fails
        
        return filtered
    
    def create_vocal_envelope(self, time, text):
        """Create realistic vocal envelope with breathing and articulation"""
        envelope = np.ones_like(time)
        
        # Word-based articulation
        words = text.split()
        word_duration = len(time) / len(words)
        
        for i, word in enumerate(words):
            start_idx = int(i * word_duration)
            end_idx = int((i + 1) * word_duration)
            
            if end_idx > len(envelope):
                end_idx = len(envelope)
            
            word_env = envelope[start_idx:end_idx]
            word_time = np.linspace(0, 1, len(word_env))
            
            # Attack and decay for each word
            attack = np.minimum(word_time / 0.1, 1.0)  # 10% attack
            decay = np.minimum((1 - word_time) / 0.2 + 0.7, 1.0)  # 20% decay
            
            envelope[start_idx:end_idx] = attack * decay
        
        # Add breathing pattern
        breath_freq = 0.3  # Slow breathing
        breath_mod = 1 + 0.1 * np.sin(2 * np.pi * time * breath_freq)
        envelope *= breath_mod
        
        return np.clip(envelope, 0.1, 1.0)
    
    def add_vocal_resonance(self, audio):
        """Add resonance characteristics of human vocal tract"""
        # Simple comb filter for resonance
        delay_samples = int(0.01 * self.sample_rate)  # 10ms delay
        resonance = np.zeros_like(audio)
        
        for i in range(delay_samples, len(audio)):
            resonance[i] = audio[i] + 0.3 * audio[i - delay_samples]
        
        return 0.7 * audio + 0.3 * resonance
    
    def apply_singing_dynamics(self, audio, voice_style, mood):
        """Apply dynamics and effects for singing styles"""
        # Compression for vocal consistency
        threshold = 0.6
        ratio = 3.0
        
        compressed = np.copy(audio)
        for i in range(len(audio)):
            if abs(audio[i]) > threshold:
                excess = abs(audio[i]) - threshold
                compressed[i] = np.sign(audio[i]) * (threshold + excess / ratio)
        
        # Mood-based processing
        if mood == 'happy':
            # Brighter, more energetic
            compressed = self.boost_frequency_range(compressed, 1000, 3000, 1.2)
        elif mood == 'sad':
            # Warmer, more mellow
            compressed = self.boost_frequency_range(compressed, 200, 800, 1.1)
        
        return compressed
    
    def boost_frequency_range(self, audio, low_freq, high_freq, gain):
        """Boost a frequency range for tonal shaping"""
        try:
            sos = signal.butter(4, [low_freq, high_freq], btype='band', 
                              fs=self.sample_rate, output='sos')
            band_audio = signal.sosfilt(sos, audio)
            return audio + (gain - 1.0) * band_audio
        except:
            return audio

# Global model
singing_voice = SimpleSingingVoice()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "simple-singing-voice",
        "model_loaded": True
    })

@app.route('/generate-singing', methods=['POST'])
def generate_singing():
    try:
        data = request.get_json()
        lyrics = data.get('lyrics', '')
        voice_style = data.get('voice_style', 'ballad')
        mood = data.get('mood', 'happy')
        
        if not lyrics:
            return jsonify({"error": "No lyrics provided"}), 400
        
        print(f"🎤 Received request: '{lyrics}' ({voice_style}, {mood})")
        
        # Generate singing
        audio = singing_voice.create_singing_voice(lyrics, voice_style, mood)
        
        # Save to temporary file
        temp_path = tempfile.mktemp(suffix='.wav')
        sf.write(temp_path, audio, singing_voice.sample_rate)
        
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
            "duration_seconds": len(audio) / singing_voice.sample_rate,
            "synthesis_method": "harmonic_singing_voice",
            "voice_style": voice_style,
            "mood": mood
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to generate singing: {str(e)}"}), 500

@app.route('/test-singing', methods=['GET'])
def test_singing():
    try:
        audio = singing_voice.create_singing_voice("La la la", 'pop', 'happy')
        return jsonify({
            "status": "success",
            "duration": len(audio) / singing_voice.sample_rate,
            "method": "harmonic_singing_voice"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🎵 Starting Simple Singing Voice Service...")
    print("🎤 Service ready on port 8002")
    app.run(host='0.0.0.0', port=8002, debug=True)
