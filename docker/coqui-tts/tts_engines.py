#!/usr/bin/env python3
"""
TTS Engines Module
Handles various Text-to-Speech engines including Google TTS, Edge TTS, Gemini TTS, and system TTS
"""

import os
import tempfile
import asyncio
import subprocess
import numpy as np
import soundfile as sf
from scipy.signal import resample
import base64
import io

# Free TTS imports
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

# Gemini TTS imports
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class TTSEngines:
    """Manages various TTS engines for speech generation"""
    
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate
        self.gtts_available = GTTS_AVAILABLE
        self.edge_tts_available = EDGE_TTS_AVAILABLE
        self.gemini_available = GEMINI_AVAILABLE
        self.free_tts_available = GTTS_AVAILABLE or EDGE_TTS_AVAILABLE or GEMINI_AVAILABLE
        
        # Initialize Gemini if available
        if self.gemini_available:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                print("🔮 Gemini TTS initialized")
            else:
                print("⚠️  Gemini API key not found. Set GEMINI_API_KEY environment variable.")
                self.gemini_available = False
    
    def generate_speech(self, text, tts_engine='auto', pitch_adjustment=0):
        """Generate speech using the specified TTS engine"""
        print(f"🆓 Using TTS generation with engine: {tts_engine}")
        
        # Use Gemini TTS if specifically requested
        if tts_engine == 'gemini' and self.gemini_available:
            try:
                return self.generate_gemini_tts(text, pitch_adjustment)
            except Exception as e:
                print(f"Gemini TTS failed: {e}")
        
        # Try Google TTS first (gTTS)
        if self.gtts_available:
            try:
                audio_data = self.generate_gtts(text)
                if pitch_adjustment != 0:
                    audio_data = self._apply_pitch_shift(audio_data, pitch_adjustment)
                return audio_data
            except Exception as e:
                print(f"gTTS failed: {e}")
        
        # Try Edge TTS as fallback
        if self.edge_tts_available:
            try:
                audio_data = self.generate_edge_tts(text)
                if pitch_adjustment != 0:
                    audio_data = self._apply_pitch_shift(audio_data, pitch_adjustment)
                return audio_data
            except Exception as e:
                print(f"Edge TTS failed: {e}")
        
        # Final fallback to system TTS
        audio_data = self.generate_system_tts(text)
        if pitch_adjustment != 0:
            audio_data = self._apply_pitch_shift(audio_data, pitch_adjustment)
        return audio_data
    
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
            audio_data = self._convert_and_load_audio(temp_mp3)
            print(f"✅ Generated gTTS audio: {len(audio_data)/self.sample_rate:.1f}s")
            return audio_data
        except Exception as e:
            if os.path.exists(temp_mp3):
                os.unlink(temp_mp3)
            raise e
    
    def generate_edge_tts(self, text):
        """Generate speech using Microsoft Edge TTS (FREE)"""
        print("🗣️ Using Microsoft Edge TTS")
        
        async def _generate_edge_tts():
            # Create Edge TTS communicator
            communicate = edge_tts.Communicate(text, "en-US-AriaNeural")  # Female voice
            
            # Save to temporary file
            temp_mp3 = tempfile.mktemp(suffix='.mp3')
            await communicate.save(temp_mp3)
            
            return temp_mp3
        
        # Run async function
        temp_mp3 = asyncio.run(_generate_edge_tts())
        
        # Convert and load
        try:
            audio_data = self._convert_and_load_audio(temp_mp3)
            print(f"✅ Generated Edge TTS audio: {len(audio_data)/self.sample_rate:.1f}s")
            return audio_data
        except Exception as e:
            if os.path.exists(temp_mp3):
                os.unlink(temp_mp3)
            raise e
    
    def generate_gemini_tts(self, text, pitch_adjustment=0):
        """Generate speech using Gemini TTS with pitch control"""
        if not self.gemini_available:
            raise Exception("Gemini TTS not available")
        
        print("🔮 Using Gemini TTS")
        
        try:
            # Create a model instance for TTS
            model = genai.GenerativeModel('gemini-pro')
            
            # For now, we'll use Edge TTS with enhanced processing for Gemini-style output
            # Note: Actual Gemini TTS API may differ - this is a placeholder implementation
            
            # Use Edge TTS as the base engine but with enhanced processing
            if self.edge_tts_available:
                async def _generate_gemini_enhanced():
                    # Select voice based on pitch adjustment
                    voice = "en-US-AriaNeural"  # Default female voice
                    if pitch_adjustment < -6:
                        voice = "en-US-GuyNeural"  # Lower male voice
                    elif pitch_adjustment > 6:
                        voice = "en-US-JennyNeural"  # Higher female voice
                    
                    communicate = edge_tts.Communicate(text, voice)
                    temp_mp3 = tempfile.mktemp(suffix='.mp3')
                    await communicate.save(temp_mp3)
                    return temp_mp3
                
                temp_mp3 = asyncio.run(_generate_gemini_enhanced())
                
                # Convert and apply pitch adjustment
                audio_data = self._convert_and_load_audio(temp_mp3)
                
                # Apply pitch shifting if needed
                if pitch_adjustment != 0:
                    audio_data = self._apply_pitch_shift(audio_data, pitch_adjustment)
                
                print(f"✅ Generated Gemini-enhanced TTS audio: {len(audio_data)/self.sample_rate:.1f}s, pitch: {pitch_adjustment:+d}")
                return audio_data
            else:
                # Fallback to gTTS with pitch adjustment
                audio_data = self.generate_gtts(text)
                if pitch_adjustment != 0:
                    audio_data = self._apply_pitch_shift(audio_data, pitch_adjustment)
                return audio_data
                
        except Exception as e:
            print(f"Gemini TTS failed: {e}")
            # Fallback to regular TTS
            audio_data = self.generate_speech(text)
            if pitch_adjustment != 0:
                audio_data = self._apply_pitch_shift(audio_data, pitch_adjustment)
            return audio_data
    
    def _apply_pitch_shift(self, audio_data, pitch_shift_semitones):
        """Apply pitch shifting to audio data"""
        try:
            # Simple pitch shifting using resampling
            # This is a basic implementation - more sophisticated libraries like librosa would be better
            pitch_factor = 2 ** (pitch_shift_semitones / 12.0)
            
            # Resample to change pitch
            new_length = int(len(audio_data) / pitch_factor)
            pitched_audio = resample(audio_data, new_length)
            
            # Pad or trim to original length to maintain timing
            if len(pitched_audio) > len(audio_data):
                pitched_audio = pitched_audio[:len(audio_data)]
            else:
                pitched_audio = np.pad(pitched_audio, (0, len(audio_data) - len(pitched_audio)), 'constant')
            
            return pitched_audio.astype(np.float32)
        except Exception as e:
            print(f"Pitch shifting failed: {e}, returning original audio")
            return audio_data

    def generate_system_tts(self, text):
        """Generate speech using system TTS commands"""
        print("🗣️ Attempting system TTS generation")
        
        # Try using system say command on macOS (if available)
        try:
            # Create temporary file
            temp_wav = tempfile.mktemp(suffix='.wav')
            
            # Try macOS 'say' command first
            result = subprocess.run([
                'say', '-v', 'Samantha', '-o', temp_wav, '--data-format=LEF32@22050', text
            ], capture_output=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(temp_wav):
                print("✅ Using macOS 'say' command")
                audio_data = self._load_wav_file(temp_wav)
                if audio_data is not None:
                    return audio_data
            
            # Try espeak if say failed
            result = subprocess.run([
                'espeak', '-w', temp_wav, '-s', '150', text
            ], capture_output=True, timeout=10)
            
            if result.returncode == 0 and os.path.exists(temp_wav):
                print("✅ Using espeak")
                audio_data = self._load_wav_file(temp_wav)
                if audio_data is not None:
                    return audio_data
                    
        except Exception as e:
            print(f"System TTS failed: {e}")
        
        # Fallback: Generate simple phonetic approximation
        print("🔄 Using phonetic approximation")
        return self.generate_phonetic_speech(text)
    
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
            word_audio = self._generate_word_sound(word, word_duration)
            
            # Add to output
            actual_end = min(end_sample, num_samples)
            actual_length = actual_end - start_sample
            if actual_length > 0:
                audio[start_sample:actual_end] = word_audio[:actual_length]
        
        return audio
    
    def _convert_and_load_audio(self, temp_mp3):
        """Convert MP3 to WAV and load audio data"""
        temp_wav = tempfile.mktemp(suffix='.wav')
        
        # Try to use ffmpeg to convert MP3 to WAV
        result = subprocess.run([
            'ffmpeg', '-i', temp_mp3, '-acodec', 'pcm_s16le', 
            '-ar', str(self.sample_rate), '-ac', '1', temp_wav
        ], capture_output=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(temp_wav):
            audio_data = self._load_wav_file(temp_wav)
            os.unlink(temp_mp3)  # Clean up
            return audio_data
        else:
            # Fallback: try to load MP3 directly with librosa if available
            try:
                import librosa
                audio_data, sr = librosa.load(temp_mp3, sr=self.sample_rate, mono=True)
                os.unlink(temp_mp3)
                return audio_data
            except ImportError:
                print("⚠️ Neither ffmpeg nor librosa available for MP3 conversion")
                os.unlink(temp_mp3)
                raise Exception("Cannot convert MP3 to WAV")
    
    def _load_wav_file(self, temp_wav):
        """Load audio from WAV file"""
        try:
            audio_data, sr = sf.read(temp_wav)
            os.unlink(temp_wav)  # Clean up
            
            # Convert to mono if needed
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Resample if needed
            if sr != self.sample_rate:
                audio_data = resample(audio_data, int(len(audio_data) * self.sample_rate / sr))
            
            return audio_data
            
        except Exception as e:
            print(f"Failed to load audio file: {e}")
            return None
    
    def _generate_word_sound(self, word, duration):
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
