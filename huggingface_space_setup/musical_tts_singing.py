#!/usr/bin/env python3
"""
Musical TTS Singing Service
Converts text to speech and applies musical post-processing for realistic singing
"""

import os
import base64
import tempfile
import json
import math
import re
import io
import asyncio
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.signal import resample
import requests

# Free TTS imports
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("⚠️ gTTS not installed - run: pip install gtts")

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    print("⚠️ edge-tts not installed - run: pip install edge-tts")

app = Flask(__name__)
CORS(app)

class MusicalTTSSinger:
    """Advanced TTS + Musical Post-Processing for realistic singing"""
    
    def __init__(self):
        self.sample_rate = 22050
        # Check for free TTS options instead of OpenAI
        self.free_tts_available = GTTS_AVAILABLE or EDGE_TTS_AVAILABLE
        print(f"🎤 Free TTS available: gTTS={GTTS_AVAILABLE}, EdgeTTS={EDGE_TTS_AVAILABLE}")
        
    def create_singing_voice(self, text, voice_style='pop', mood='happy'):
        """Create singing from text using TTS + musical post-processing + full arrangement"""
        print(f"🎵 Creating full musical arrangement for: '{text}' in {voice_style} style")
        
        try:
            # Try Free TTS + Musical Processing first
            if self.free_tts_available:
                return self.text_to_musical_singing_free(text, voice_style, mood)
            else:
                print("⚠️ No free TTS available, using system TTS synthesis")
                return self.create_harmonic_singing(text, voice_style, mood)
                
        except Exception as e:
            print(f"⚠️ Free TTS failed ({e}), falling back to system synthesis")
            return self.create_harmonic_singing(text, voice_style, mood)
    
    def create_singing_voice_vocals_only(self, text, voice_style='pop', mood='happy'):
        """Create singing vocals only (no accompaniment) - original behavior"""
        print(f"🎵 Creating vocals-only singing for: '{text}' in {voice_style} style")
        
        try:
            # Try Free TTS + Musical Processing first
            if self.free_tts_available:
                return self.text_to_musical_singing_free_vocals_only(text, voice_style, mood)
            else:
                print("⚠️ No free TTS available, using system TTS synthesis")
                return self.create_harmonic_singing(text, voice_style, mood)
                
        except Exception as e:
            print(f"⚠️ Free TTS failed ({e}), falling back to system synthesis")
            return self.create_harmonic_singing(text, voice_style, mood)
    
    def create_singing_voice_gemini(self, text, voice_style='pop', mood='happy', pitch_adjustment=0):
        """Create singing from text using Gemini TTS + musical post-processing + full arrangement"""
        print(f"🔮 Creating Gemini musical arrangement for: '{text}' in {voice_style} style, pitch: {pitch_adjustment:+d}")
        
        try:
            # Import TTS engines
            from tts_engines import TTSEngines
            
            tts_engines = TTSEngines(self.sample_rate)
            
            # Generate speech using Gemini TTS
            speech = tts_engines.generate_speech(text, tts_engine='gemini', pitch_adjustment=pitch_adjustment)
            
            # Apply musical processing
            singing = self.convert_speech_to_singing(speech, voice_style, mood)
            
            # Add full musical arrangement
            full_arrangement = self.add_musical_arrangement(singing, voice_style, mood)
            
            return full_arrangement
            
        except Exception as e:
            print(f"⚠️ Gemini TTS failed ({e}), falling back to regular TTS")
            return self.create_singing_voice(text, voice_style, mood)
    
    def create_singing_voice_vocals_only_gemini(self, text, voice_style='pop', mood='happy', pitch_adjustment=0):
        """Create singing vocals only using Gemini TTS (no accompaniment)"""
        print(f"🔮 Creating Gemini vocals-only singing for: '{text}' in {voice_style} style, pitch: {pitch_adjustment:+d}")
        
        try:
            # Import TTS engines
            from tts_engines import TTSEngines
            
            tts_engines = TTSEngines(self.sample_rate)
            
            # Generate speech using Gemini TTS
            speech = tts_engines.generate_speech(text, tts_engine='gemini', pitch_adjustment=pitch_adjustment)
            
            # Apply musical processing for vocals only
            singing = self.convert_speech_to_singing(speech, voice_style, mood)
            
            return singing
            
        except Exception as e:
            print(f"⚠️ Gemini TTS failed ({e}), falling back to regular TTS")
            return self.create_singing_voice_vocals_only(text, voice_style, mood)

    def text_to_musical_singing_free_vocals_only(self, text, style="pop", mood="happy"):
        """Convert text to singing using FREE TTS + musical post-processing (vocals only)"""
        print("🎤 Using FREE TTS + Musical Post-Processing (vocals only)")
        
        # Step 1: Generate speech using free TTS
        speech_audio = self.generate_free_tts(text)
        
        # Step 2: Analyze text for musical phrasing
        phrases = self.analyze_text_phrasing(text)
        
        # Step 3: Generate appropriate melody
        melody = self.generate_melody(phrases, style, mood)
        
        # Step 4: Apply musical post-processing to create singing (vocals only)
        singing_audio = self.apply_musical_processing(speech_audio, melody, phrases)
        
        return singing_audio
    
    def text_to_musical_singing_free(self, text, style="pop", mood="happy"):
        """Convert text to singing using FREE TTS + musical post-processing"""
        print("🎤 Using FREE TTS + Musical Post-Processing")
        
        # Step 1: Generate speech using free TTS
        speech_audio = self.generate_free_tts(text)
        
        # Step 2: Analyze text for musical phrasing
        phrases = self.analyze_text_phrasing(text)
        
        # Step 3: Generate appropriate melody
        melody = self.generate_melody(phrases, style, mood)
        
        # Step 4: Apply musical post-processing to create singing
        singing_audio = self.apply_musical_processing(speech_audio, melody, phrases)
        
        # Step 5: Create full musical arrangement with accompaniment
        full_arrangement = self.create_full_musical_arrangement(singing_audio, melody, phrases, style, mood)
        
        return full_arrangement
    
    def generate_free_tts(self, text):
        """Generate speech using FREE TTS services"""
        print("🆓 Using free TTS generation")
        
        # Try Google TTS first (gTTS)
        if GTTS_AVAILABLE:
            try:
                return self.generate_gtts(text)
            except Exception as e:
                print(f"gTTS failed: {e}")
        
        # Try Edge TTS as fallback
        if EDGE_TTS_AVAILABLE:
            try:
                return self.generate_edge_tts(text)
            except Exception as e:
                print(f"Edge TTS failed: {e}")
        
        # Final fallback to system TTS
        return self.generate_simple_tts(text)
    
    def generate_gtts(self, text):
        """Generate speech using Google Text-to-Speech (FREE)"""
        print("🗣️ Using Google TTS (gTTS)")
        
        # Create gTTS object
        tts = gTTS(text=text, lang='en', slow=False, tld='com')
        
        # Save to temporary file
        temp_mp3 = tempfile.mktemp(suffix='.mp3')
        tts.save(temp_mp3)
        
        # Convert MP3 to WAV and load
        try:
            # Try to use ffmpeg or similar to convert MP3 to WAV
            temp_wav = tempfile.mktemp(suffix='.wav')
            
            # Simple approach: use system ffmpeg if available
            import subprocess
            result = subprocess.run([
                'ffmpeg', '-i', temp_mp3, '-acodec', 'pcm_s16le', 
                '-ar', str(self.sample_rate), '-ac', '1', temp_wav
            ], capture_output=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(temp_wav):
                audio_data = self.load_temp_audio(temp_wav)
                os.unlink(temp_mp3)  # Clean up
                return audio_data
            else:
                # Fallback: try to load MP3 directly with librosa if available
                try:
                    import librosa
                    audio_data, sr = librosa.load(temp_mp3, sr=self.sample_rate, mono=True)
                    os.unlink(temp_mp3)
                    print(f"✅ Generated gTTS audio: {len(audio_data)/self.sample_rate:.1f}s")
                    return audio_data
                except ImportError:
                    print("⚠️ Neither ffmpeg nor librosa available for MP3 conversion")
                    os.unlink(temp_mp3)
                    raise Exception("Cannot convert MP3 to WAV")
                    
        except Exception as e:
            if os.path.exists(temp_mp3):
                os.unlink(temp_mp3)
            raise e
    
    def generate_edge_tts(self, text):
        """Generate speech using Microsoft Edge TTS (FREE)"""
        print("🗣️ Using Microsoft Edge TTS")
        
        import asyncio
        
        async def _generate_edge_tts():
            # Create Edge TTS communicator
            communicate = edge_tts.Communicate(text, "en-US-AriaNeural")  # Female voice
            
            # Save to temporary file
            temp_mp3 = tempfile.mktemp(suffix='.mp3')
            await communicate.save(temp_mp3)
            
            return temp_mp3
        
        # Run async function
        temp_mp3 = asyncio.run(_generate_edge_tts())
        
        # Convert and load similar to gTTS
        try:
            temp_wav = tempfile.mktemp(suffix='.wav')
            
            import subprocess
            result = subprocess.run([
                'ffmpeg', '-i', temp_mp3, '-acodec', 'pcm_s16le', 
                '-ar', str(self.sample_rate), '-ac', '1', temp_wav
            ], capture_output=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(temp_wav):
                audio_data = self.load_temp_audio(temp_wav)
                os.unlink(temp_mp3)
                return audio_data
            else:
                # Fallback to librosa
                try:
                    import librosa
                    audio_data, sr = librosa.load(temp_mp3, sr=self.sample_rate, mono=True)
                    os.unlink(temp_mp3)
                    print(f"✅ Generated Edge TTS audio: {len(audio_data)/self.sample_rate:.1f}s")
                    return audio_data
                except ImportError:
                    os.unlink(temp_mp3)
                    raise Exception("Cannot convert MP3 to WAV")
                    
        except Exception as e:
            if os.path.exists(temp_mp3):
                os.unlink(temp_mp3)
            raise e
    
    def analyze_text_phrasing(self, text):
        """Analyze text to determine musical phrasing"""
        # Split into words and estimate syllables
        words = re.findall(r'\b\w+\b', text.lower())
        phrases = []
        
        current_phrase = []
        syllable_count = 0
        
        for word in words:
            syllables = self.count_syllables(word)
            current_phrase.append({
                'word': word,
                'syllables': syllables,
                'emphasis': self.get_word_emphasis(word)
            })
            syllable_count += syllables
            
            # Break into phrases at natural points (every 6-10 syllables)
            if syllable_count >= 8 or word in ['and', 'but', 'so', 'then']:
                if current_phrase:
                    phrases.append(current_phrase)
                    current_phrase = []
                    syllable_count = 0
        
        if current_phrase:
            phrases.append(current_phrase)
        
        return phrases
    
    def count_syllables(self, word):
        """Estimate syllable count in a word"""
        vowels = 'aeiouy'
        word = word.lower()
        count = 0
        prev_char_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_char_was_vowel:
                count += 1
            prev_char_was_vowel = is_vowel
        
        # Handle silent e
        if word.endswith('e') and count > 1:
            count -= 1
        
        return max(1, count)  # Every word has at least 1 syllable
    
    def get_word_emphasis(self, word):
        """Determine if word should be emphasized musically"""
        # Content words and longer words get more emphasis
        emphasis_words = ['love', 'heart', 'dream', 'night', 'light', 'time', 'life', 'world', 'feel', 'know']
        if word in emphasis_words or len(word) > 6:
            return 'high'
        elif len(word) > 3:
            return 'medium'
        else:
            return 'low'
    
    def generate_melody(self, phrases, style="pop", mood="happy"):
        """Generate a melody based on text analysis and style"""
        # Define musical scales and vocal ranges
        if style == "pop":
            # Pentatonic scale - always sounds good
            base_notes = [261.63, 293.66, 329.63, 392.00, 440.00]  # C D E G A
            vocal_range = (220, 500)  # Comfortable singing range
        elif style == "ballad":
            # Major scale with lower range
            base_notes = [196.00, 220.00, 246.94, 261.63, 293.66, 329.63, 349.23]  # G A B C D E F
            vocal_range = (180, 400)
        elif style == "jazz":
            # Minor pentatonic
            base_notes = [220.00, 261.63, 293.66, 329.63, 415.30]  # A C D E G#
            vocal_range = (200, 450)
        else:
            base_notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00]  # C major
            vocal_range = (200, 450)
        
        melody = []
        current_note_index = 2  # Start in middle of range
        phrase_arch = 0  # Track melodic arc across phrases
        
        for phrase_idx, phrase in enumerate(phrases):
            phrase_melody = []
            
            # Each phrase should have a melodic arc
            phrase_length = sum(word['syllables'] for word in phrase)
            phrase_peak = phrase_length // 2  # Peak in middle of phrase
            syllable_count = 0
            
            for word_info in phrase:
                syllables = word_info['syllables']
                emphasis = word_info['emphasis']
                
                for syl in range(syllables):
                    # Calculate position in phrase for melodic arc
                    phrase_position = syllable_count / phrase_length
                    
                    # Create melodic arc (goes up then down)
                    if syllable_count < phrase_peak:
                        arc_direction = 1  # Going up
                    else:
                        arc_direction = -1  # Coming down
                    
                    # Determine target note based on emphasis and arc
                    if emphasis == 'high':
                        if phrase_position < 0.7:  # Don't go too high at end
                            target_index = min(len(base_notes) - 1, current_note_index + arc_direction)
                        else:
                            target_index = max(0, current_note_index - 1)
                    elif emphasis == 'low':
                        target_index = max(0, current_note_index - 1)
                    else:
                        # Medium emphasis - follow the arc more subtly
                        if abs(current_note_index - len(base_notes)//2) > 2:
                            # Return towards center
                            if current_note_index > len(base_notes)//2:
                                target_index = current_note_index - 1
                            else:
                                target_index = current_note_index + 1
                        else:
                            target_index = current_note_index
                    
                    # Smooth transition (no big jumps)
                    step_size = min(1, abs(target_index - current_note_index))
                    if target_index > current_note_index:
                        current_note_index = min(len(base_notes) - 1, current_note_index + step_size)
                    elif target_index < current_note_index:
                        current_note_index = max(0, current_note_index - step_size)
                    
                    # Ensure we stay in vocal range
                    freq = base_notes[current_note_index]
                    if freq < vocal_range[0]:
                        current_note_index = min(current_note_index + 1, len(base_notes) - 1)
                        freq = base_notes[current_note_index]
                    elif freq > vocal_range[1]:
                        current_note_index = max(current_note_index - 1, 0)
                        freq = base_notes[current_note_index]
                    
                    phrase_melody.append(freq)
                    syllable_count += 1
            
            # End phrase on a lower note for natural resolution
            if phrase_melody:
                resolution_index = max(0, current_note_index - 1)
                phrase_melody[-1] = base_notes[resolution_index]
                current_note_index = resolution_index
            
            melody.extend(phrase_melody)
        
        print(f"🎼 Generated melody with {len(melody)} notes")
        return melody
    
    def apply_musical_processing(self, speech_audio, melody, phrases):
        """Apply musical post-processing to make speech sound like singing"""
        if len(speech_audio) == 0 or len(melody) == 0:
            return speech_audio
        
        print(f"🎛️ Applying musical processing to {len(speech_audio)/self.sample_rate:.1f}s speech")
        
        # Calculate timing - aim for natural syllable duration
        syllable_count = sum(sum(word['syllables'] for word in phrase) for phrase in phrases)
        target_syllable_duration = 0.4  # 400ms per syllable for singing
        target_duration = syllable_count * target_syllable_duration
        target_samples = int(target_duration * self.sample_rate)
        
        # Time-stretch speech to match singing timing
        stretched_speech = resample(speech_audio, target_samples)
        
        # Apply pitch shifting to match melody
        singing_audio = self.pitch_shift_to_melody(stretched_speech, melody)
        
        # Add singing characteristics
        singing_audio = self.add_vocal_effects(singing_audio)
        
        print(f"✅ Created {len(singing_audio)/self.sample_rate:.1f}s of singing")
        return singing_audio
    
    def create_full_musical_arrangement(self, singing_audio, melody, phrases, style="pop", mood="happy"):
        """Create a full musical arrangement with singing + instrumental accompaniment"""
        print("🎼 Creating full musical arrangement with accompaniment")
        
        duration = len(singing_audio) / self.sample_rate
        
        # Generate musical accompaniment
        accompaniment = self.generate_musical_accompaniment(melody, duration, style, mood)
        
        # Mix singing with accompaniment
        full_mix = self.mix_vocal_and_accompaniment(singing_audio, accompaniment)
        
        print(f"🎵 Created full arrangement: {len(full_mix)/self.sample_rate:.1f}s")
        return full_mix
    
    def generate_musical_accompaniment(self, melody, duration, style="pop", mood="happy"):
        """Generate instrumental accompaniment (chords, bass, drums)"""
        num_samples = int(duration * self.sample_rate)
        
        # Generate chord progression
        chords = self.generate_chord_progression(melody, style, mood)
        
        # Create instrumental tracks
        chord_track = self.create_chord_track(chords, duration, style)
        bass_track = self.create_bass_track(chords, duration, style)
        drums_track = self.create_drum_track(duration, style)
        
        # Mix instrumental tracks
        accompaniment = np.zeros(num_samples)
        
        # Add tracks with appropriate levels
        if len(chord_track) == num_samples:
            accompaniment += chord_track * 0.3  # Chords - background level
        if len(bass_track) == num_samples:
            accompaniment += bass_track * 0.4   # Bass - prominent but not overpowering
        if len(drums_track) == num_samples:
            accompaniment += drums_track * 0.2  # Drums - subtle rhythm
        
        return accompaniment
    
    def generate_chord_progression(self, melody, style="pop", mood="happy"):
        """Generate chord progression based on melody and style"""
        # Determine key from melody
        melody_notes = [freq for freq in melody if freq > 0]
        if not melody_notes:
            root_freq = 261.63  # Default to C
        else:
            root_freq = min(melody_notes)  # Use lowest note as potential root
        
        # Common chord progressions by style
        if style == "pop":
            if mood == "happy":
                # I-V-vi-IV (very popular progression)
                progression = ['I', 'V', 'vi', 'IV']
            else:
                # vi-IV-I-V (more melancholic)
                progression = ['vi', 'IV', 'I', 'V']
        elif style == "ballad":
            # I-vi-IV-V (classic ballad)
            progression = ['I', 'vi', 'IV', 'V']
        elif style == "jazz":
            # ii-V-I-vi (jazz standard)
            progression = ['ii', 'V', 'I', 'vi']
        else:
            # Default: I-IV-V-I
            progression = ['I', 'IV', 'V', 'I']
        
        # Convert roman numerals to actual chord frequencies
        chords = []
        for roman in progression:
            chord_freqs = self.roman_to_chord_frequencies(roman, root_freq)
            chords.append(chord_freqs)
        
        return chords
    
    def roman_to_chord_frequencies(self, roman, root_freq):
        """Convert roman numeral to chord frequencies"""
        # Major scale intervals (semitones from root)
        scale_intervals = [0, 2, 4, 5, 7, 9, 11]  # Major scale
        
        # Roman numeral to scale degree mapping
        roman_map = {
            'I': 0, 'ii': 1, 'iii': 2, 'IV': 3, 'V': 4, 'vi': 5, 'vii': 6
        }
        
        # Get scale degree
        scale_degree = roman_map.get(roman, 0)
        
        # Calculate root of chord
        chord_root_interval = scale_intervals[scale_degree]
        chord_root = root_freq * (2 ** (chord_root_interval / 12))
        
        # Build triad (root, third, fifth)
        if roman.islower():  # Minor chord
            third_interval = 3  # Minor third
            fifth_interval = 7  # Perfect fifth
        else:  # Major chord
            third_interval = 4  # Major third
            fifth_interval = 7  # Perfect fifth
        
        chord_frequencies = [
            chord_root,                                          # Root
            chord_root * (2 ** (third_interval / 12)),         # Third
            chord_root * (2 ** (fifth_interval / 12))          # Fifth
        ]
        
        return chord_frequencies
    
    def create_chord_track(self, chords, duration, style="pop"):
        """Create chord accompaniment track"""
        num_samples = int(duration * self.sample_rate)
        chord_track = np.zeros(num_samples)
        
        # Calculate chord duration
        chord_duration = duration / len(chords)
        chord_samples = int(chord_duration * self.sample_rate)
        
        for i, chord_freqs in enumerate(chords):
            start_sample = i * chord_samples
            end_sample = min((i + 1) * chord_samples, num_samples)
            chord_length = end_sample - start_sample
            
            if chord_length <= 0:
                continue
            
            # Create chord sound
            t = np.linspace(0, chord_length / self.sample_rate, chord_length)
            chord_sound = np.zeros(chord_length)
            
            # Add each note in the chord
            for freq in chord_freqs:
                # Create soft pad-like sound
                note_wave = 0.3 * np.sin(2 * np.pi * freq * t)
                
                # Add subtle harmonics for richness
                note_wave += 0.1 * np.sin(2 * np.pi * freq * 2 * t)
                note_wave += 0.05 * np.sin(2 * np.pi * freq * 3 * t)
                
                # Apply envelope for smooth attack/release
                envelope = self.create_chord_envelope(t, style)
                note_wave *= envelope
                
                chord_sound += note_wave
            
            # Add to track
            chord_track[start_sample:end_sample] = chord_sound
        
        return chord_track
    
    def create_chord_envelope(self, t, style="pop"):
        """Create envelope for chord sounds"""
        total_length = len(t)
        envelope = np.ones(total_length)
        
        if style == "ballad":
            # Gentle, sustained envelope
            attack_samples = int(total_length * 0.1)
            release_samples = int(total_length * 0.2)
        else:
            # More rhythmic envelope
            attack_samples = int(total_length * 0.05)
            release_samples = int(total_length * 0.1)
        
        # Attack
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Release
        if release_samples > 0:
            envelope[-release_samples:] = np.linspace(1, 0.3, release_samples)
        
        return envelope
    
    def create_bass_track(self, chords, duration, style="pop"):
        """Create bass line following the chord progression"""
        num_samples = int(duration * self.sample_rate)
        bass_track = np.zeros(num_samples)
        
        chord_duration = duration / len(chords)
        chord_samples = int(chord_duration * self.sample_rate)
        
        for i, chord_freqs in enumerate(chords):
            start_sample = i * chord_samples
            end_sample = min((i + 1) * chord_samples, num_samples)
            chord_length = end_sample - start_sample
            
            if chord_length <= 0:
                continue
            
            # Use root note of chord, one octave lower
            bass_freq = chord_freqs[0] / 2
            
            # Create bass pattern based on style
            if style == "pop":
                bass_pattern = self.create_pop_bass_pattern(bass_freq, chord_length)
            elif style == "ballad":
                bass_pattern = self.create_ballad_bass_pattern(bass_freq, chord_length)
            else:
                bass_pattern = self.create_simple_bass_pattern(bass_freq, chord_length)
            
            bass_track[start_sample:end_sample] = bass_pattern
        
        return bass_track
    
    def create_pop_bass_pattern(self, bass_freq, length):
        """Create pop-style bass pattern"""
        t = np.linspace(0, length / self.sample_rate, length)
        
        # Simple on-beat pattern
        bass_line = np.zeros(length)
        
        # Add bass hits on beats
        beat_duration = length / 4  # 4 beats per chord
        for beat in range(4):
            beat_start = int(beat * beat_duration)
            beat_end = int((beat + 1) * beat_duration)
            beat_length = beat_end - beat_start
            
            if beat_length > 0:
                beat_t = np.linspace(0, beat_length / self.sample_rate, beat_length)
                
                # Punchy bass sound
                bass_note = 0.5 * np.sin(2 * np.pi * bass_freq * beat_t)
                
                # Add some harmonics for body
                bass_note += 0.2 * np.sin(2 * np.pi * bass_freq * 2 * beat_t)
                
                # Envelope for punch
                envelope = np.exp(-beat_t * 3)  # Quick decay
                bass_note *= envelope
                
                bass_line[beat_start:beat_end] = bass_note
        
        return bass_line
    
    def create_ballad_bass_pattern(self, bass_freq, length):
        """Create ballad-style bass pattern"""
        t = np.linspace(0, length / self.sample_rate, length)
        
        # Sustained bass note
        bass_line = 0.3 * np.sin(2 * np.pi * bass_freq * t)
        
        # Add warmth with subtle harmonics
        bass_line += 0.1 * np.sin(2 * np.pi * bass_freq * 2 * t)
        
        # Gentle envelope
        envelope = np.ones_like(t)
        attack_samples = int(len(t) * 0.1)
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        bass_line *= envelope
        return bass_line
    
    def create_simple_bass_pattern(self, bass_freq, length):
        """Create simple bass pattern"""
        t = np.linspace(0, length / self.sample_rate, length)
        bass_line = 0.4 * np.sin(2 * np.pi * bass_freq * t)
        
        # Simple envelope
        envelope = np.exp(-t * 0.5)
        bass_line *= envelope
        
        return bass_line
    
    def create_drum_track(self, duration, style="pop"):
        """Create simple drum/rhythm track"""
        num_samples = int(duration * self.sample_rate)
        drum_track = np.zeros(num_samples)
        
        # Set tempo based on style
        if style == "ballad":
            bpm = 70
        elif style == "pop":
            bpm = 120
        else:
            bpm = 100
        
        # Calculate beat timing
        beats_per_second = bpm / 60
        beat_duration = 1.0 / beats_per_second
        beat_samples = int(beat_duration * self.sample_rate)
        
        num_beats = int(duration * beats_per_second)
        
        for beat in range(num_beats):
            beat_start = beat * beat_samples
            
            if beat_start >= num_samples:
                break
            
            # Create kick drum on strong beats
            if beat % 4 == 0:  # Downbeat
                kick = self.create_kick_sound()
                kick_end = min(beat_start + len(kick), num_samples)
                drum_track[beat_start:kick_end] += kick[:kick_end - beat_start]
            
            # Create hi-hat on offbeats
            elif beat % 2 == 1:  # Offbeat
                hihat = self.create_hihat_sound()
                hihat_end = min(beat_start + len(hihat), num_samples)
                drum_track[beat_start:hihat_end] += hihat[:hihat_end - beat_start]
        
        return drum_track
    
    def create_kick_sound(self):
        """Create kick drum sound"""
        duration = 0.1  # 100ms kick
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples)
        
        # Low frequency sine wave with pitch bend
        freq_start = 60  # Start frequency
        freq_end = 40    # End frequency
        freq_curve = freq_start + (freq_end - freq_start) * t / duration
        
        kick = 0.5 * np.sin(2 * np.pi * freq_curve * t)
        
        # Add click for attack
        click = 0.2 * np.random.normal(0, 1, samples)
        click *= np.exp(-t * 50)  # Very quick decay for click
        
        kick += click
        
        # Envelope
        envelope = np.exp(-t * 8)  # Quick decay
        kick *= envelope
        
        return kick
    
    def create_hihat_sound(self):
        """Create hi-hat sound"""
        duration = 0.05  # 50ms hi-hat
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples)
        
        # High frequency noise
        hihat = 0.1 * np.random.normal(0, 1, samples)
        
        # Filter to high frequencies
        # Simple high-pass effect by removing low frequencies
        hihat = np.diff(np.concatenate([[0], hihat]))
        
        # Envelope
        envelope = np.exp(-t[:-1] * 20)  # Very quick decay
        hihat *= envelope
        
        return hihat
    
    def mix_vocal_and_accompaniment(self, vocal_audio, accompaniment):
        """Mix vocal and instrumental tracks"""
        # Ensure both tracks are the same length
        min_length = min(len(vocal_audio), len(accompaniment))
        vocal_trimmed = vocal_audio[:min_length]
        accompaniment_trimmed = accompaniment[:min_length]
        
        # Mix with appropriate levels
        mixed = vocal_trimmed * 0.7 + accompaniment_trimmed * 0.5
        
        # Apply light compression to glue the mix together
        mixed = self.apply_light_compression(mixed)
        
        # Normalize
        if np.max(np.abs(mixed)) > 0:
            mixed = mixed / np.max(np.abs(mixed)) * 0.8
        
        return mixed
    
    def apply_light_compression(self, audio):
        """Apply light compression to the mix"""
        # Simple soft-knee compression
        threshold = 0.6
        ratio = 3.0
        
        compressed = audio.copy()
        
        # Find samples above threshold
        above_threshold = np.abs(audio) > threshold
        
        # Apply compression to samples above threshold
        excess = np.abs(audio[above_threshold]) - threshold
        compressed_excess = excess / ratio
        
        # Apply compression while preserving sign
        compressed[above_threshold] = np.sign(audio[above_threshold]) * (threshold + compressed_excess)
        
        return compressed
    
    def pitch_shift_to_melody(self, audio, melody):
        """Shift pitch of audio to match melody notes"""
        if len(melody) == 0:
            return audio
        
        note_length = len(audio) // len(melody)
        pitched_audio = np.zeros_like(audio)
        
        for i, target_freq in enumerate(melody):
            start_idx = i * note_length
            end_idx = min((i + 1) * note_length, len(audio))
            segment = audio[start_idx:end_idx]
            
            if len(segment) == 0:
                continue
            
            # Apply pitch shifting
            shifted_segment = self.pitch_shift_segment(segment, target_freq)
            
            # Smooth transitions between notes
            if i > 0 and len(shifted_segment) > 0:
                transition_samples = min(len(shifted_segment) // 8, 256)
                if transition_samples > 0 and start_idx >= transition_samples:
                    # Crossfade
                    fade_out = np.linspace(1, 0, transition_samples)
                    fade_in = np.linspace(0, 1, transition_samples)
                    
                    # Apply fade to previous segment end
                    pitched_audio[start_idx-transition_samples:start_idx] *= fade_out
                    
                    # Apply fade to current segment start and add
                    if len(shifted_segment) >= transition_samples:
                        shifted_segment[:transition_samples] *= fade_in
                        pitched_audio[start_idx:start_idx+transition_samples] += shifted_segment[:transition_samples]
                        shifted_segment = shifted_segment[transition_samples:]
                        start_idx += transition_samples
            
            # Add the rest of the segment
            end_idx = min(start_idx + len(shifted_segment), len(pitched_audio))
            if end_idx > start_idx:
                pitched_audio[start_idx:end_idx] = shifted_segment[:end_idx-start_idx]
        
        return pitched_audio
    
    def pitch_shift_segment(self, segment, target_freq):
        """Pitch shift a segment to target frequency with minimal artifacts"""
        if len(segment) == 0:
            return segment
            
        # Use more conservative pitch shifting - closer to natural speech
        base_freq = 200  # More realistic average speaking frequency
        shift_ratio = target_freq / base_freq
        
        # Much more conservative range - stay close to natural speech
        shift_ratio = np.clip(shift_ratio, 0.7, 1.5)  # Only 30% up or down
        
        # Apply gradual shift to avoid artifacts
        new_length = int(len(segment) / shift_ratio)
        if new_length > 0:
            try:
                shifted = resample(segment, new_length)
                
                # Maintain timing by padding or cropping more carefully
                if len(shifted) < len(segment):
                    # Pad with fade to zero
                    padded = np.zeros(len(segment))
                    padded[:len(shifted)] = shifted
                    # Add fade out to padded area
                    if len(shifted) < len(segment):
                        fade_length = min(len(segment) - len(shifted), len(segment) // 10)
                        if fade_length > 0 and len(shifted) >= fade_length:
                            fade = np.linspace(1.0, 0.0, fade_length)
                            padded[len(shifted)-fade_length:len(shifted)] *= fade
                    return padded
                else:
                    # Crop with gentle fade
                    cropped = shifted[:len(segment)]
                    fade_length = min(len(segment) // 20, 50)  # Gentle fade at end
                    if fade_length > 0:
                        fade = np.linspace(1.0, 0.8, fade_length)
                        cropped[-fade_length:] *= fade
                    return cropped
            except:
                return segment
        
        return segment
    
    def add_vocal_effects(self, audio):
        """Add subtle vocal effects to make audio sound more like natural singing"""
        # Much more subtle vibrato
        t = np.arange(len(audio)) / self.sample_rate
        vibrato_freq = 4.2  # Slower, more natural
        vibrato_depth = 0.005  # Much less modulation (0.5% instead of 2%)
        vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_freq * t)
        
        # Apply very gentle vibrato
        audio_with_vibrato = audio * vibrato
        
        # Enhance formants for vocal quality (more conservative)
        enhanced_audio = self.enhance_formants(audio_with_vibrato)
        
        # Add very subtle breath sounds
        final_audio = self.add_breath_sounds(enhanced_audio)
        
        # Apply gentle vocal envelope
        final_audio = self.apply_vocal_envelope(final_audio)
        
        # More conservative normalization
        if np.max(np.abs(final_audio)) > 0:
            final_audio = final_audio / np.max(np.abs(final_audio)) * 0.6  # Lower volume
        
        return final_audio
    
    def enhance_formants(self, audio):
        """Enhance formants to make speech sound more sung"""
        # Vocal formants for singing
        formants = [650, 1080, 2650]  # Typical singing formants
        
        enhanced = audio.copy()
        
        for formant_freq in formants:
            # Create bandpass filter around formant
            nyquist = self.sample_rate / 2
            low = max(formant_freq * 0.8 / nyquist, 0.01)
            high = min(formant_freq * 1.2 / nyquist, 0.99)
            
            try:
                b, a = signal.butter(2, [low, high], btype='band')
                formant_component = signal.filtfilt(b, a, audio)
                enhanced += formant_component * 0.2  # Boost formants
            except:
                continue
        
        return enhanced
    
    def add_breath_sounds(self, audio):
        """Add subtle breath sounds for natural singing"""
        # Add very subtle noise for breath texture
        noise_level = 0.01
        breath_noise = np.random.normal(0, noise_level, len(audio))
        
        # Filter noise to vocal frequency range
        try:
            b, a = signal.butter(4, [300 / (self.sample_rate/2), 3000 / (self.sample_rate/2)], btype='band')
            filtered_noise = signal.filtfilt(b, a, breath_noise)
            return audio + filtered_noise * 0.05
        except:
            return audio
    
    def apply_vocal_envelope(self, audio):
        """Apply vocal envelope for natural singing dynamics"""
        # Create envelope with attack and release
        envelope = np.ones_like(audio)
        
        # Gentle attack
        attack_samples = int(0.05 * self.sample_rate)  # 50ms
        if attack_samples > 0 and len(envelope) > attack_samples:
            envelope[:attack_samples] = np.linspace(0.3, 1.0, attack_samples)
        
        # Gentle release
        release_samples = int(0.1 * self.sample_rate)  # 100ms
        if release_samples > 0 and len(envelope) > release_samples:
            envelope[-release_samples:] = np.linspace(1.0, 0.2, release_samples)
        
        return audio * envelope
    
    def create_harmonic_singing(self, text, voice_style='pop', mood='happy'):
        """Create singing by using simple TTS synthesis and applying musical effects"""
        print("🎵 Creating singing using simple TTS + musical transformation")
        
        # Try to use a simple TTS approach first
        try:
            speech_audio = self.generate_simple_tts(text)
            if speech_audio is not None:
                return self.apply_singing_effects(speech_audio, text, voice_style, mood)
        except Exception as e:
            print(f"Simple TTS failed: {e}")
        
        # Fallback to basic vocal synthesis
        return self.create_basic_vocal_singing(text, voice_style, mood)
    
    def generate_simple_tts(self, text):
        """Generate simple TTS using system commands or basic synthesis"""
        print("🗣️ Attempting simple TTS generation")
        
        # Try using system say command on macOS (if available)
        try:
            import subprocess
            import tempfile
            import os
            
            # Create temporary file
            temp_wav = tempfile.mktemp(suffix='.wav')
            
            # Try macOS 'say' command first
            result = subprocess.run([
                'say', '-v', 'Samantha', '-o', temp_wav, '--data-format=LEF32@22050', text
            ], capture_output=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(temp_wav):
                print("✅ Using macOS 'say' command")
                audio_data = self.load_temp_audio(temp_wav)
                if audio_data is not None:
                    return audio_data
            
            # Try espeak if say failed
            result = subprocess.run([
                'espeak', '-w', temp_wav, '-s', '150', text
            ], capture_output=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(temp_wav):
                print("✅ Using espeak")
                audio_data = self.load_temp_audio(temp_wav)
                if audio_data is not None:
                    return audio_data
                    
        except Exception as e:
            print(f"System TTS failed: {e}")
        
        # Fallback: Generate simple phonetic approximation
        print("🔄 Using phonetic approximation")
        return self.generate_phonetic_speech(text)
    
    def load_temp_audio(self, temp_wav):
        """Load audio from temporary file"""
        try:
            import soundfile as sf
            import os
            
            audio_data, sr = sf.read(temp_wav)
            os.unlink(temp_wav)  # Clean up
            
            # Convert to mono if needed
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Resample if needed
            if sr != self.sample_rate:
                audio_data = resample(audio_data, int(len(audio_data) * self.sample_rate / sr))
            
            print(f"✅ Loaded TTS audio: {len(audio_data)/self.sample_rate:.1f}s")
            return audio_data
            
        except Exception as e:
            print(f"Failed to load temp audio: {e}")
            return None
    
    def generate_phonetic_speech(self, text):
        """Generate basic phonetic speech approximation"""
        words = text.split()
        total_duration = len(words) * 0.5  # 500ms per word
        num_samples = int(total_duration * self.sample_rate)
        audio = np.zeros(num_samples)
        
        word_duration = total_duration / len(words)
        
        for i, word in enumerate(words):
            start_time = i * word_duration
            end_time = (i + 1) * word_duration
            start_sample = int(start_time * self.sample_rate)
            end_sample = int(end_time * self.sample_rate)
            
            # Generate simple voiced sound for word
            word_audio = self.generate_word_sound(word, word_duration)
            
            # Add to output
            actual_end = min(end_sample, num_samples)
            actual_length = actual_end - start_sample
            if actual_length > 0:
                audio[start_sample:actual_end] = word_audio[:actual_length]
        
        return audio
    
    def generate_word_sound(self, word, duration):
        """Generate simple voiced sound for a word"""
        num_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, num_samples)
        
        # Base frequency around speech range
        base_freq = 150
        
        # Simple vowel detection for frequency variation
        vowel_freqs = {'a': 180, 'e': 160, 'i': 200, 'o': 140, 'u': 120}
        word_freq = base_freq
        
        for char in word.lower():
            if char in vowel_freqs:
                word_freq = vowel_freqs[char]
                break
        
        # Generate voiced sound
        fundamental = 0.5 * np.sin(2 * np.pi * word_freq * t)
        
        # Add harmonics for voice-like quality
        harmonic2 = 0.2 * np.sin(2 * np.pi * word_freq * 2 * t)
        harmonic3 = 0.1 * np.sin(2 * np.pi * word_freq * 3 * t)
        
        voice_sound = fundamental + harmonic2 + harmonic3
        
        # Add envelope
        envelope = np.ones_like(t)
        attack = int(num_samples * 0.1)
        decay = int(num_samples * 0.1)
        
        if attack > 0:
            envelope[:attack] = np.linspace(0, 1, attack)
        if decay > 0:
            envelope[-decay:] = np.linspace(1, 0, decay)
        
        return voice_sound * envelope
    
    def apply_singing_effects(self, speech_audio, text, voice_style, mood):
        """Apply musical effects to make speech sound like singing"""
        print("🎛️ Applying singing effects to speech")
        
        # Parse text for melody generation
        words = text.split()
        syllable_count = sum(self.count_syllables(word) for word in words)
        
        # Generate melody
        melody_notes = self.generate_text_based_melody(text, voice_style, mood)
        
        # Ensure melody matches syllables
        if len(melody_notes) != syllable_count:
            melody_notes = self.adjust_melody_to_syllables(melody_notes, syllable_count)
        
        # Set tempo
        if voice_style == 'ballad':
            bpm = 70
        elif voice_style == 'pop':
            bpm = 120
        else:
            bpm = 100
        
        # Calculate timing
        beat_duration = 60.0 / bpm
        syllables_per_beat = 2 if voice_style == 'ballad' else 4
        syllable_duration = beat_duration / syllables_per_beat
        target_duration = syllable_count * syllable_duration
        
        # Time-stretch the speech to match musical timing
        target_samples = int(target_duration * self.sample_rate)
        stretched_speech = resample(speech_audio, target_samples)
        
        # Apply pitch shifting to match melody
        singing_audio = self.apply_melody_to_speech(stretched_speech, melody_notes)
        
        # Add musical effects
        singing_audio = self.add_musical_effects(singing_audio, voice_style)
        
        # Apply dynamics
        singing_audio = self.apply_musical_phrasing(singing_audio, target_duration, voice_style)
        
        # Normalize
        if np.max(np.abs(singing_audio)) > 0:
            singing_audio = singing_audio / np.max(np.abs(singing_audio)) * 0.7
        
        print(f"✅ Created {target_duration:.1f}s of musical singing from speech")
        return singing_audio
    
    def apply_melody_to_speech(self, speech_audio, melody_notes):
        """Apply pitch shifting to speech to follow melody"""
        if len(melody_notes) == 0:
            return speech_audio
        
        # Divide speech into segments for each note
        segment_length = len(speech_audio) // len(melody_notes)
        pitched_audio = np.zeros_like(speech_audio)
        
        for i, target_freq in enumerate(melody_notes):
            start_idx = i * segment_length
            end_idx = min((i + 1) * segment_length, len(speech_audio))
            segment = speech_audio[start_idx:end_idx]
            
            if len(segment) == 0:
                continue
            
            # Apply conservative pitch shifting
            shifted_segment = self.pitch_shift_speech_segment(segment, target_freq)
            
            # Smooth transitions
            if i > 0 and len(shifted_segment) > 0:
                fade_length = min(len(shifted_segment) // 10, 100)
                if fade_length > 0 and start_idx >= fade_length:
                    # Crossfade
                    fade_out = np.linspace(1, 0.5, fade_length)
                    pitched_audio[start_idx-fade_length:start_idx] *= fade_out
                    
                    fade_in = np.linspace(0.5, 1, fade_length)
                    shifted_segment[:fade_length] *= fade_in
            
            # Add segment to output
            end_idx = min(start_idx + len(shifted_segment), len(pitched_audio))
            if end_idx > start_idx:
                pitched_audio[start_idx:end_idx] = shifted_segment[:end_idx-start_idx]
        
        return pitched_audio
    
    def pitch_shift_speech_segment(self, segment, target_freq):
        """Pitch shift speech segment to target frequency"""
        if len(segment) == 0:
            return segment
        
        # Estimate current fundamental frequency (very basic)
        estimated_freq = 150  # Average speech frequency
        
        # Calculate shift ratio (conservative)
        shift_ratio = target_freq / estimated_freq
        shift_ratio = np.clip(shift_ratio, 0.8, 1.4)  # Limit to realistic range
        
        # Apply pitch shift using resampling
        new_length = int(len(segment) / shift_ratio)
        if new_length > 0:
            try:
                shifted = resample(segment, new_length)
                
                # Maintain original timing
                if len(shifted) < len(segment):
                    # Pad
                    padded = np.zeros(len(segment))
                    padded[:len(shifted)] = shifted
                    return padded
                else:
                    # Crop
                    return shifted[:len(segment)]
            except:
                return segment
        
        return segment
    
    def add_musical_effects(self, audio, voice_style):
        """Add musical effects like vibrato and reverb"""
        # Add subtle vibrato
        t = np.arange(len(audio)) / self.sample_rate
        vibrato_freq = 5.0
        vibrato_depth = 0.01  # Very subtle
        vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_freq * t)
        audio_with_vibrato = audio * vibrato
        
        # Add reverb
        reverb_delay = int(0.08 * self.sample_rate)  # 80ms
        if reverb_delay < len(audio_with_vibrato):
            reverb = np.zeros_like(audio_with_vibrato)
            reverb[reverb_delay:] = audio_with_vibrato[:-reverb_delay] * 0.15
            audio_with_vibrato += reverb
        
        return audio_with_vibrato
    
    def create_basic_vocal_singing(self, text, voice_style='pop', mood='happy'):
        """Fallback: create very basic vocal singing"""
        print("🎵 Using fallback basic vocal singing")
        
        words = text.split()
        total_duration = len(words) * 0.6  # 600ms per word
        
        # Generate simple melody
        melody_notes = self.generate_text_based_melody(text, voice_style, mood)
        
        # Create audio
        num_samples = int(total_duration * self.sample_rate)
        audio = np.zeros(num_samples)
        
        note_duration = total_duration / len(melody_notes)
        
        for i, freq in enumerate(melody_notes):
            start_sample = int(i * note_duration * self.sample_rate)
            end_sample = int((i + 1) * note_duration * self.sample_rate)
            note_length = end_sample - start_sample
            
            if start_sample >= num_samples:
                break
            
            # Create simple sine wave with envelope
            t = np.linspace(0, note_duration, note_length)
            note_signal = 0.3 * np.sin(2 * np.pi * freq * t)
            
            # Simple envelope
            envelope = np.ones_like(note_signal)
            attack = int(note_length * 0.1)
            decay = int(note_length * 0.1)
            
            if attack > 0:
                envelope[:attack] = np.linspace(0, 1, attack)
            if decay > 0:
                envelope[-decay:] = np.linspace(1, 0, decay)
            
            note_signal *= envelope
            
            # Add to output
            actual_end = min(end_sample, num_samples)
            actual_length = actual_end - start_sample
            if actual_length > 0:
                audio[start_sample:actual_end] = note_signal[:actual_length]
        
        return audio
    
    def parse_text_to_syllables(self, text):
        """Parse text into syllables with phonetic information"""
        words = text.split()
        syllables_info = []
        
        for word in words:
            word_syllables = self.break_word_into_syllables(word)
            syllables_info.extend(word_syllables)
        
        return syllables_info
    
    def break_word_into_syllables(self, word):
        """Break a word into syllables with phonetic info"""
        word = word.lower().strip('.,!?";')
        
        # Simple syllable breaking (can be enhanced)
        syllables = []
        
        # Basic patterns for common words
        common_patterns = {
            'hello': [{'text': 'hel', 'consonants': 'h', 'vowel': 'eh'}, 
                     {'text': 'lo', 'consonants': 'l', 'vowel': 'oh'}],
            'world': [{'text': 'world', 'consonants': 'wrld', 'vowel': 'er'}],
            'love': [{'text': 'love', 'consonants': 'lv', 'vowel': 'uh'}],
            'this': [{'text': 'this', 'consonants': 'th s', 'vowel': 'ih'}],
            'test': [{'text': 'test', 'consonants': 't st', 'vowel': 'eh'}],
            'time': [{'text': 'time', 'consonants': 't m', 'vowel': 'ah'}],
            'feel': [{'text': 'feel', 'consonants': 'f l', 'vowel': 'ee'}],
            'good': [{'text': 'good', 'consonants': 'g d', 'vowel': 'oo'}],
            'walking': [{'text': 'walk', 'consonants': 'w lk', 'vowel': 'ah'}, 
                       {'text': 'ing', 'consonants': 'ng', 'vowel': 'ih'}],
        }
        
        if word in common_patterns:
            return common_patterns[word]
        
        # Fallback: simple vowel-based syllable breaking
        vowels = 'aeiou'
        current_syllable = ''
        consonants = ''
        vowel_found = False
        
        for i, char in enumerate(word):
            if char in vowels:
                if vowel_found and current_syllable:
                    # End previous syllable
                    syllables.append({
                        'text': current_syllable,
                        'consonants': consonants,
                        'vowel': self.map_vowel_sound(current_syllable)
                    })
                    current_syllable = char
                    consonants = ''
                else:
                    current_syllable += char
                vowel_found = True
            else:
                if vowel_found:
                    consonants += char
                current_syllable += char
        
        # Add final syllable
        if current_syllable:
            syllables.append({
                'text': current_syllable,
                'consonants': consonants,
                'vowel': self.map_vowel_sound(current_syllable)
            })
        
        # Ensure at least one syllable
        if not syllables:
            syllables.append({
                'text': word,
                'consonants': '',
                'vowel': 'ah'
            })
        
        return syllables
    
    def map_vowel_sound(self, syllable_text):
        """Map syllable text to vowel sound"""
        text = syllable_text.lower()
        
        # Simple vowel sound mapping
        if 'ee' in text or 'ea' in text or 'ie' in text:
            return 'ee'
        elif 'oo' in text or 'ou' in text:
            return 'oo'
        elif 'o' in text and text.endswith('o'):
            return 'oh'
        elif 'a' in text and len(text) > 2:
            return 'ah'
        elif 'e' in text:
            return 'eh'
        elif 'i' in text:
            return 'ih'
        elif 'o' in text:
            return 'oh'
        elif 'u' in text:
            return 'uh'
        else:
            return 'ah'  # Default
    
    def adjust_melody_to_syllables(self, melody_notes, syllable_count):
        """Adjust melody to match number of syllables"""
        if len(melody_notes) == syllable_count:
            return melody_notes
        
        if len(melody_notes) < syllable_count:
            # Extend melody by repeating patterns
            extended = list(melody_notes)
            while len(extended) < syllable_count:
                # Repeat the melody with slight variations
                for note in melody_notes:
                    if len(extended) >= syllable_count:
                        break
                    # Add small variation
                    variation = note * (0.95 + 0.1 * np.random.random())
                    extended.append(variation)
            return extended[:syllable_count]
        else:
            # Trim melody to match syllables
            return melody_notes[:syllable_count]
    
    def apply_musical_phrasing(self, audio, duration, style):
        """Apply musical phrasing and dynamics like a real song"""
        # Create musical dynamics curve
        num_samples = len(audio)
        t = np.linspace(0, duration, num_samples)
        
        # Different phrasing for different styles
        if style == 'ballad':
            # Ballad: Gentle rise and fall
            dynamics = 0.6 + 0.4 * np.sin(2 * np.pi * 0.2 * t)  # Slow breathing
        elif style == 'pop':
            # Pop: More energetic with emphasis points
            dynamics = 0.7 + 0.3 * (1 + np.sin(2 * np.pi * 0.5 * t)) / 2
        else:
            # Default: Gentle wave
            dynamics = 0.65 + 0.35 * np.sin(2 * np.pi * 0.3 * t)
        
        # Apply dynamics
        audio_with_dynamics = audio * dynamics
        
        # Add subtle reverb effect for singing quality
        reverb_delay = int(0.1 * self.sample_rate)  # 100ms reverb
        if reverb_delay < len(audio_with_dynamics):
            reverb = np.zeros_like(audio_with_dynamics)
            reverb[reverb_delay:] = audio_with_dynamics[:-reverb_delay] * 0.2
            audio_with_dynamics += reverb
        
        return audio_with_dynamics
    
    def generate_text_based_melody(self, text, style, mood):
        """Generate melody using actual song structure patterns (verse-chorus form)"""
        words = text.split()
        
        # Define proper musical scales for different styles
        if style == 'pop':
            # C major pentatonic - always sounds good
            scale = [261.63, 293.66, 329.63, 392.00, 440.00, 523.25]  # C D E G A C
            mood_modifier = 1.0 if mood == 'happy' else 0.8
        elif style == 'ballad':
            # Lower register, more intimate
            scale = [196.00, 220.00, 246.94, 261.63, 293.66, 329.63]  # G A B C D E
            mood_modifier = 0.7 if mood == 'sad' else 0.9
        else:
            # Default major scale
            scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00]  # C D E F G A
            mood_modifier = 1.0
        
        # Analyze text to create verse-like or chorus-like structure
        is_short_phrase = len(words) <= 4
        is_repetitive = len(set(words)) < len(words) * 0.7  # Lots of repeated words
        
        melody = []
        
        if is_short_phrase or is_repetitive:
            # Chorus pattern: catchy, repetitive, higher energy
            melody = self.create_chorus_melody(words, scale, mood_modifier)
        else:
            # Verse pattern: narrative, builds tension
            melody = self.create_verse_melody(words, scale, mood_modifier)
        
        print(f"🎼 Generated {'chorus' if is_short_phrase else 'verse'} melody with {len(melody)} notes")
        return melody
    
    def create_verse_melody(self, words, scale, mood_modifier):
        """Create verse-style melody that builds toward a climax"""
        melody = []
        verse_length = sum(self.count_syllables(word) for word in words)
        
        # Verse pattern: Start low, build up gradually, then resolve
        start_note = 1  # Start near bottom of scale
        peak_position = int(verse_length * 0.7)  # Peak at 70% through
        current_position = 0
        current_note = start_note
        
        for word in words:
            syllables = self.count_syllables(word)
            word_importance = min(len(word) / 8.0, 1.0)  # Longer words are more important
            
            for syl in range(syllables):
                # Calculate where we are in the verse arc
                progress = current_position / verse_length
                
                # Create melodic arc: rise to peak, then fall
                if current_position < peak_position:
                    # Rising section
                    target_height = start_note + (progress * 3 * mood_modifier)
                else:
                    # Falling section
                    remaining = (verse_length - current_position) / (verse_length - peak_position)
                    target_height = start_note + (3 * mood_modifier * remaining)
                
                # Add word emphasis
                target_height += word_importance
                
                # Smooth movement (no big jumps)
                target_note = int(min(target_height, len(scale) - 1))
                step = 1 if target_note > current_note else -1 if target_note < current_note else 0
                current_note = max(0, min(len(scale) - 1, current_note + step))
                
                melody.append(scale[current_note])
                current_position += 1
        
        return melody
    
    def create_chorus_melody(self, words, scale, mood_modifier):
        """Create chorus-style melody: catchy, repetitive, memorable"""
        melody = []
        
        # Chorus pattern: Higher energy, more repetitive intervals
        base_note = int(len(scale) / 2)  # Start in middle of range
        if mood_modifier > 0.9:  # Happy mood
            base_note = min(base_note + 1, len(scale) - 2)
        
        current_note = base_note
        
        for i, word in enumerate(words):
            syllables = self.count_syllables(word)
            is_emphasized = word.lower() in ['love', 'heart', 'you', 'me', 'life', 'time', 'feel', 'know']
            
            for syl in range(syllables):
                if is_emphasized and syl == 0:
                    # Emphasize important words by going higher
                    target_note = min(current_note + 2, len(scale) - 1)
                elif syl == 0:
                    # First syllable of word - slight rise
                    target_note = min(current_note + 1, len(scale) - 1)
                else:
                    # Other syllables - step down naturally
                    target_note = max(current_note - 1, base_note - 1)
                
                # Smooth transition
                if target_note > current_note:
                    current_note = min(current_note + 1, len(scale) - 1)
                elif target_note < current_note:
                    current_note = max(current_note - 1, 0)
                
                melody.append(scale[current_note])
            
            # Between words: return toward base for catchier pattern
            if i < len(words) - 1:
                if current_note > base_note:
                    current_note = max(current_note - 1, base_note)
        
        return melody
    
    def create_vocal_note(self, t, freq, syllable_info=None):
        """Create a vocal note that sounds like singing with recognizable vowel sounds"""
        # Get vowel sound for this syllable
        vowel = self.extract_primary_vowel(syllable_info) if syllable_info else 'ah'
        
        # Realistic vibrato
        vibrato_freq = 5.8
        vibrato_depth = 0.015  # Moderate vibrato
        vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_freq * t)
        
        # Generate voiced sound with formant structure
        voiced_sound = self.generate_voiced_sound(t, freq, vowel, vibrato)
        
        # Add consonant articulation if needed
        if syllable_info and 'consonants' in syllable_info:
            voiced_sound = self.add_consonant_articulation(voiced_sound, t, syllable_info['consonants'])
        
        # Apply singing envelope
        envelope = self.create_singing_envelope(t)
        voiced_sound *= envelope
        
        return voiced_sound
    
    def extract_primary_vowel(self, syllable_info):
        """Extract the primary vowel sound from syllable"""
        if not syllable_info or 'text' not in syllable_info:
            return 'ah'
        
        text = syllable_info['text'].lower()
        
        # Simple vowel mapping based on spelling
        vowel_map = {
            'a': 'ah', 'aa': 'ah', 'ar': 'ah',
            'e': 'eh', 'ea': 'ee', 'ee': 'ee', 'er': 'er',
            'i': 'ih', 'ie': 'ee', 'ir': 'er',
            'o': 'oh', 'oo': 'oo', 'or': 'or',
            'u': 'uh', 'ur': 'er',
            'y': 'ih'
        }
        
        # Look for vowel patterns in the text
        for pattern, vowel in vowel_map.items():
            if pattern in text:
                return vowel
        
        # Default fallback
        for char in text:
            if char in 'aeiou':
                return {'a': 'ah', 'e': 'eh', 'i': 'ih', 'o': 'oh', 'u': 'uh'}[char]
        
        return 'ah'  # Default vowel
    
    def generate_voiced_sound(self, t, freq, vowel, vibrato):
        """Generate realistic voiced sound with proper formant structure"""
        # Formant frequencies for different vowels (F1, F2, F3)
        formants = {
            'ah': (730, 1090, 2440),   # "father"
            'eh': (530, 1840, 2480),   # "bed"
            'ih': (390, 1990, 2550),   # "bit"
            'oh': (570, 840, 2410),    # "bought"
            'oo': (300, 870, 2240),    # "boot"
            'ee': (270, 2290, 3010),   # "beet"
            'uh': (520, 1190, 2390),   # "but"
            'er': (490, 1350, 1690),   # "bird"
            'or': (500, 700, 2600)     # "port"
        }
        
        f1, f2, f3 = formants.get(vowel, formants['ah'])
        
        # Generate fundamental with harmonics
        fundamental = 0.5 * np.sin(2 * np.pi * freq * vibrato * t)
        
        # Add harmonics based on formant structure
        voiced_signal = fundamental
        
        # First formant (strongest)
        formant1_strength = self.formant_response(freq, f1, 80)  # 80 Hz bandwidth
        voiced_signal += formant1_strength * 0.4 * np.sin(2 * np.pi * f1 * vibrato * t / (f1/freq))
        
        # Second formant
        formant2_strength = self.formant_response(freq, f2, 90)
        voiced_signal += formant2_strength * 0.3 * np.sin(2 * np.pi * f2 * vibrato * t / (f2/freq))
        
        # Third formant (weaker)
        formant3_strength = self.formant_response(freq, f3, 120)
        voiced_signal += formant3_strength * 0.2 * np.sin(2 * np.pi * f3 * vibrato * t / (f3/freq))
        
        # Add some harmonic content for richness
        for harmonic in range(2, 6):
            harmonic_freq = freq * harmonic
            if harmonic_freq < self.sample_rate / 2:  # Avoid aliasing
                strength = 0.1 / harmonic  # Decreasing strength
                voiced_signal += strength * np.sin(2 * np.pi * harmonic_freq * vibrato * t)
        
        return voiced_signal
    
    def formant_response(self, freq, formant_freq, bandwidth):
        """Calculate formant response strength"""
        # Simple formant response - stronger when freq is near formant
        distance = abs(freq - formant_freq)
        if distance < bandwidth:
            return 1.0 - (distance / bandwidth) * 0.5
        else:
            return 0.3  # Background level
    
    def add_consonant_articulation(self, voiced_sound, t, consonants):
        """Add consonant sounds to the beginning/end of syllables"""
        if not consonants:
            return voiced_sound
        
        total_length = len(voiced_sound)
        
        # Add noise burst for consonants like 't', 'k', 'p'
        if any(c in consonants for c in 'tkpbdg'):
            # Sharp attack with noise
            burst_length = min(int(0.02 * self.sample_rate), total_length // 10)
            if burst_length > 0:
                noise_burst = np.random.normal(0, 0.3, burst_length)
                # High-pass filter the noise
                try:
                    from scipy import signal
                    b, a = signal.butter(2, 2000 / (self.sample_rate/2), btype='high')
                    noise_burst = signal.filtfilt(b, a, noise_burst)
                except:
                    pass
                
                voiced_sound[:burst_length] = noise_burst * 0.5 + voiced_sound[:burst_length] * 0.5
        
        # Add fricative noise for 's', 'f', 'sh', etc.
        if any(c in consonants for c in 'sfzhvth'):
            fricative_length = min(int(0.05 * self.sample_rate), total_length // 5)
            if fricative_length > 0:
                fricative_noise = np.random.normal(0, 0.2, fricative_length)
                # Filter noise to appropriate frequency range
                try:
                    from scipy import signal
                    if 's' in consonants or 'z' in consonants:
                        # High frequency for sibilants
                        b, a = signal.butter(2, [4000 / (self.sample_rate/2), 8000 / (self.sample_rate/2)], btype='band')
                    else:
                        # Lower frequency for other fricatives
                        b, a = signal.butter(2, [1500 / (self.sample_rate/2), 4000 / (self.sample_rate/2)], btype='band')
                    fricative_noise = signal.filtfilt(b, a, fricative_noise)
                except:
                    pass
                
                # Add at beginning or end
                voiced_sound[:fricative_length] = fricative_noise * 0.3 + voiced_sound[:fricative_length] * 0.7
        
        return voiced_sound
    
    def create_singing_envelope(self, t):
        """Create natural singing envelope"""
        total_length = len(t)
        envelope = np.ones(total_length)
        
        # Natural vocal attack
        attack_samples = int(total_length * 0.08)
        if attack_samples > 0:
            attack_curve = np.sin(np.linspace(0, np.pi/2, attack_samples)) ** 1.5
            envelope[:attack_samples] = attack_curve
        
        # Sustain with slight decay
        sustain_start = attack_samples
        sustain_end = int(total_length * 0.85)
        if sustain_end > sustain_start:
            sustain_length = sustain_end - sustain_start
            decay_curve = np.linspace(1.0, 0.9, sustain_length)
            envelope[sustain_start:sustain_end] = decay_curve
        
        # Natural release
        release_samples = total_length - sustain_end
        if release_samples > 0:
            release_curve = np.linspace(0.9, 0.1, release_samples)
            envelope[sustain_end:] = release_curve
        
        return envelope

# Global model
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
        include_music = data.get('include_music', True)
        
        # New Gemini TTS parameters
        tts_engine = data.get('tts_engine', 'auto')
        pitch_adjustment = data.get('pitch_adjustment', 0)
        background_music = data.get('background_music', include_music)  # Alias for include_music
        synthesis_method = data.get('synthesis_method', None)
        
        if not lyrics:
            return jsonify({"error": "No lyrics provided"}), 400
        
        print(f"🎤 Received request: '{lyrics}' ({voice_style}, {mood})")
        print(f"🔧 TTS Engine: {tts_engine}, Pitch: {pitch_adjustment:+d}, Music: {background_music}")
        
        # Generate singing with new parameters
        if background_music:
            if tts_engine == 'gemini':
                audio = musical_singer.create_singing_voice_gemini(lyrics, voice_style, mood, pitch_adjustment)
                synthesis_method = "gemini_tts_with_music"
            else:
                audio = musical_singer.create_singing_voice(lyrics, voice_style, mood)
                synthesis_method = f"free_tts_musical_with_accompaniment" if musical_singer.free_tts_available else "system_tts_musical_with_accompaniment"
        else:
            # Generate vocals only
            if tts_engine == 'gemini':
                audio = musical_singer.create_singing_voice_vocals_only_gemini(lyrics, voice_style, mood, pitch_adjustment)
                synthesis_method = "gemini_tts_vocal_only"
            else:
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
            "includes_music": include_music
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
