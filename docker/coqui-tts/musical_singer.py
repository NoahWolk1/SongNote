#!/usr/bin/env python3
"""
Musical Singer Module
Main orchestrator class that combines TTS, text analysis, musical arrangement, and audio processing
"""

from tts_engines import TTSEngines
from text_analysis import TextAnalyzer
from musical_arrangement import MusicalArranger
from audio_processing import AudioProcessor


class MusicalTTSSinger:
    """Advanced TTS + Musical Post-Processing for realistic singing"""
    
    def __init__(self):
        self.sample_rate = 22050
        
        # Initialize components
        self.tts_engines = TTSEngines(self.sample_rate)
        self.text_analyzer = TextAnalyzer()
        self.musical_arranger = MusicalArranger(self.sample_rate)
        self.audio_processor = AudioProcessor(self.sample_rate)
        
        # Check for free TTS options
        self.free_tts_available = self.tts_engines.free_tts_available
        print(f"🎤 Free TTS available: gTTS={self.tts_engines.gtts_available}, EdgeTTS={self.tts_engines.edge_tts_available}")
        
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
    
    def text_to_musical_singing_free_vocals_only(self, text, style="pop", mood="happy"):
        """Convert text to singing using FREE TTS + musical post-processing (vocals only)"""
        print("🎤 Using FREE TTS + Musical Post-Processing (vocals only)")
        
        # Step 1: Generate speech using free TTS
        speech_audio = self.tts_engines.generate_speech(text)
        
        # Step 2: Analyze text for musical phrasing
        phrases = self.text_analyzer.analyze_text_phrasing(text)
        
        # Step 3: Generate appropriate melody
        melody = self.musical_arranger.generate_melody(phrases, style, mood)
        
        # Step 4: Apply musical post-processing to create singing (vocals only)
        singing_audio = self.audio_processor.apply_musical_processing(speech_audio, melody, phrases)
        
        return singing_audio
    
    def text_to_musical_singing_free(self, text, style="pop", mood="happy"):
        """Convert text to singing using FREE TTS + musical post-processing"""
        print("🎤 Using FREE TTS + Musical Post-Processing")
        
        # Step 1: Generate speech using free TTS
        speech_audio = self.tts_engines.generate_speech(text)
        print(f"📢 Generated speech audio: {len(speech_audio)} samples, max amplitude: {abs(speech_audio).max():.3f}")
        
        # Step 2: Analyze text for musical phrasing
        phrases = self.text_analyzer.analyze_text_phrasing(text)
        
        # Step 3: Generate appropriate melody
        melody = self.musical_arranger.generate_melody(phrases, style, mood)
        
        # Step 4: Apply musical post-processing to create singing
        singing_audio = self.audio_processor.apply_musical_processing(speech_audio, melody, phrases)
        print(f"🎵 Generated singing audio: {len(singing_audio)} samples, max amplitude: {abs(singing_audio).max():.3f}")
        
        # Step 5: Create full musical arrangement with accompaniment
        full_arrangement = self.create_full_musical_arrangement(singing_audio, melody, phrases, style, mood)
        print(f"🎼 Final arrangement: {len(full_arrangement)} samples, max amplitude: {abs(full_arrangement).max():.3f}")
        
        return full_arrangement
    
    def create_full_musical_arrangement(self, singing_audio, melody, phrases, style="pop", mood="happy"):
        """Create a full musical arrangement with singing + instrumental accompaniment"""
        print("🎼 Creating full musical arrangement with accompaniment")
        print(f"📢 Input singing audio: {len(singing_audio)} samples, max amplitude: {abs(singing_audio).max():.3f}")
        
        duration = len(singing_audio) / self.sample_rate
        
        # Generate musical accompaniment
        accompaniment = self.audio_processor.generate_musical_accompaniment(melody, duration, style, mood)
        print(f"🎹 Generated accompaniment: {len(accompaniment)} samples, max amplitude: {abs(accompaniment).max():.3f}")
        
        # Mix singing with accompaniment
        full_mix = self.audio_processor.mix_vocal_and_accompaniment(singing_audio, accompaniment)
        print(f"🎵 Final mix: {len(full_mix)} samples, max amplitude: {abs(full_mix).max():.3f}")
        
        return full_mix
    
    def create_harmonic_singing(self, text, voice_style='pop', mood='happy'):
        """Create singing by using simple TTS synthesis and applying musical effects"""
        print("🎵 Creating singing using simple TTS + musical transformation")
        
        # Try to use a simple TTS approach first
        try:
            speech_audio = self.tts_engines.generate_system_tts(text)
            if speech_audio is not None:
                return self.apply_singing_effects(speech_audio, text, voice_style, mood)
        except Exception as e:
            print(f"Simple TTS failed: {e}")
        
        # Fallback to basic vocal synthesis
        return self.create_basic_vocal_singing(text, voice_style, mood)
    
    def apply_singing_effects(self, speech_audio, text, voice_style, mood):
        """Apply musical effects to make speech sound like singing"""
        print("🎛️ Applying singing effects to speech")
        
        # Parse text for melody generation
        words = text.split()
        syllable_count = sum(self.text_analyzer.count_syllables(word) for word in words)
        
        # Generate melody
        melody_notes = self.musical_arranger.generate_text_based_melody(text, voice_style, mood)
        
        # Ensure melody matches syllables
        if len(melody_notes) != syllable_count:
            melody_notes = self.text_analyzer.adjust_melody_to_syllables(melody_notes, syllable_count)
        
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
        from scipy.signal import resample
        target_samples = int(target_duration * self.sample_rate)
        stretched_speech = resample(speech_audio, target_samples)
        
        # Apply pitch shifting to match melody
        singing_audio = self.apply_melody_to_speech(stretched_speech, melody_notes)
        
        # Add musical effects
        singing_audio = self.add_musical_effects(singing_audio, voice_style)
        
        # Apply dynamics
        singing_audio = self.audio_processor.apply_musical_phrasing(singing_audio, target_duration, voice_style)
        
        # Normalize
        import numpy as np
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
        import numpy as np
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
        import numpy as np
        shift_ratio = np.clip(shift_ratio, 0.8, 1.4)  # Limit to realistic range
        
        # Apply pitch shift using resampling
        new_length = int(len(segment) / shift_ratio)
        if new_length > 0:
            try:
                from scipy.signal import resample
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
        import numpy as np
        
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
        melody_notes = self.musical_arranger.generate_text_based_melody(text, voice_style, mood)
        
        # Create audio
        import numpy as np
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
