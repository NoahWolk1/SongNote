#!/usr/bin/env python3
"""
Audio Processing Module
Handles audio effects, pitch shifting, mixing, and accompaniment generation
"""

import numpy as np
from scipy import signal
from scipy.signal import resample


class AudioProcessor:
    """Handles all audio processing operations"""
    
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate
        # Default mix levels - vocals very prominent, music extremely quiet
        self.vocal_mix_level = 1.0  # Vocals at full volume
        self.music_mix_level = 0.05  # Music extremely quiet (5% volume)
    
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
    
    def generate_musical_accompaniment(self, melody, duration, style="pop", mood="happy"):
        """Generate instrumental accompaniment (chords, bass, drums)"""
        from musical_arrangement import MusicalArranger
        arranger = MusicalArranger(self.sample_rate)
        
        num_samples = int(duration * self.sample_rate)
        
        # Generate chord progression
        chords = arranger.generate_chord_progression(melody, style, mood)
        
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
        
        # Envelope - make sure it matches the length after diff operation
        envelope = np.exp(-t[:len(hihat)] * 20)  # Very quick decay, match hihat length
        hihat *= envelope
        
        return hihat
    
    def mix_vocal_and_accompaniment(self, vocal_audio, accompaniment):
        """Mix vocal and instrumental tracks with vocals prominently featured"""
        print(f"🎛️ MIXING DEBUG:")
        print(f"   Input vocals: {len(vocal_audio)} samples, max amplitude: {abs(vocal_audio).max():.3f}")
        print(f"   Input accompaniment: {len(accompaniment)} samples, max amplitude: {abs(accompaniment).max():.3f}")
        
        # Ensure both tracks are exactly the same length
        min_length = min(len(vocal_audio), len(accompaniment))
        vocal_trimmed = vocal_audio[:min_length].copy()
        accompaniment_trimmed = accompaniment[:min_length].copy()
        
        print(f"   After trimming - vocals: {len(vocal_trimmed)}, accompaniment: {len(accompaniment_trimmed)}")
        
        # Enhance vocals before mixing
        try:
            enhanced_vocals = self.enhance_vocal_clarity(vocal_trimmed)
            print(f"   Enhanced vocals: max amplitude: {abs(enhanced_vocals).max():.3f}")
        except Exception as e:
            print(f"   ⚠️ Vocal enhancement failed: {e}, using original vocals")
            enhanced_vocals = vocal_trimmed.copy()
        
        # Reduce accompaniment in vocal frequency range
        try:
            filtered_accompaniment = self.filter_accompaniment_for_vocals(accompaniment_trimmed)
            print(f"   Filtered accompaniment: max amplitude: {abs(filtered_accompaniment).max():.3f}")
        except Exception as e:
            print(f"   ⚠️ Accompaniment filtering failed: {e}, using original accompaniment")
            filtered_accompaniment = accompaniment_trimmed.copy()
        
        # Double-check lengths before mixing
        if len(enhanced_vocals) != len(filtered_accompaniment):
            min_len = min(len(enhanced_vocals), len(filtered_accompaniment))
            enhanced_vocals = enhanced_vocals[:min_len]
            filtered_accompaniment = filtered_accompaniment[:min_len]
            print(f"   🔧 Length mismatch fixed: both tracks now {min_len} samples")
        
        # Mix using configurable levels with vocals much louder
        try:
            mixed = enhanced_vocals * self.vocal_mix_level + filtered_accompaniment * self.music_mix_level
            print(f"   After mixing: max amplitude: {abs(mixed).max():.3f}")
            print(f"   Mix levels - vocals: {self.vocal_mix_level}, music: {self.music_mix_level}")
        except Exception as e:
            print(f"   ⚠️ Mixing failed: {e}, trying fallback approach")
            # Fallback: simple addition with length matching
            min_len = min(len(enhanced_vocals), len(filtered_accompaniment))
            mixed = (enhanced_vocals[:min_len] * self.vocal_mix_level + 
                    filtered_accompaniment[:min_len] * self.music_mix_level)
            print(f"   Fallback mixing completed: {len(mixed)} samples")
        
        # Apply light compression to glue the mix together
        try:
            mixed = self.apply_light_compression(mixed)
            print(f"   After compression: max amplitude: {abs(mixed).max():.3f}")
        except Exception as e:
            print(f"   ⚠️ Compression failed: {e}, skipping compression")
        
        # Normalize but keep vocals prominent
        if np.max(np.abs(mixed)) > 0:
            mixed = mixed / np.max(np.abs(mixed)) * 0.9  # Higher normalization level
            print(f"   After normalization: max amplitude: {abs(mixed).max():.3f}")
        else:
            print("   ⚠️ WARNING: Mixed audio is silent!")
            
        return mixed
    
    def enhance_vocal_clarity(self, vocal_audio):
        """Enhance vocal clarity by boosting vocal frequencies"""
        # Apply a gentle high-pass filter to reduce low-end muddiness
        nyquist = self.sample_rate // 2
        high_cutoff = 100 / nyquist  # 100 Hz high-pass
        b_high, a_high = signal.butter(2, high_cutoff, btype='high')
        filtered = signal.filtfilt(b_high, a_high, vocal_audio)
        
        # Boost presence frequencies (2-5 kHz) where vocals are most intelligible
        presence_low = 2000 / nyquist
        presence_high = 5000 / nyquist
        b_presence, a_presence = signal.butter(2, [presence_low, presence_high], btype='band')
        presence_boost = signal.filtfilt(b_presence, a_presence, vocal_audio)
        
        # Mix original with enhanced presence
        enhanced = filtered + presence_boost * 0.3
        
        return enhanced
    
    def filter_accompaniment_for_vocals(self, accompaniment):
        """Filter accompaniment to reduce interference with vocals"""
        # Reduce mid frequencies where vocals sit (200 Hz - 4 kHz)
        nyquist = self.sample_rate // 2
        
        # Create a notch in the vocal range
        vocal_low = 200 / nyquist
        vocal_high = 4000 / nyquist
        
        # Low-pass and high-pass components
        b_low, a_low = signal.butter(2, vocal_low, btype='low')
        b_high, a_high = signal.butter(2, vocal_high, btype='high')
        
        low_component = signal.filtfilt(b_low, a_low, accompaniment)
        high_component = signal.filtfilt(b_high, a_high, accompaniment)
        
        # Combine low and high, reducing the vocal range
        filtered = low_component * 0.7 + high_component * 0.5
        
        return filtered
    
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
    
    def apply_musical_phrasing(self, audio, duration, style):
        """Apply musical phrasing and dynamics like a real song"""
        # Create musical dynamics curve
        num_samples = len(audio)
        t = np.linspace(0, duration, num_samples)
        
        # Different phrasing for different styles
        if style == 'ballad':
            # Gentle swell and fade
            dynamics = 0.5 + 0.3 * np.sin(np.pi * t / duration)
        elif style == 'pop':
            # More consistent with slight build
            dynamics = 0.7 + 0.2 * (t / duration)
        else:
            # Default gentle dynamics
            dynamics = 0.6 + 0.2 * np.sin(np.pi * t / duration)
        
        # Apply dynamics
        audio_with_dynamics = audio * dynamics
        
        # Add subtle reverb effect for singing quality
        reverb_delay = int(0.1 * self.sample_rate)  # 100ms reverb
        if reverb_delay < len(audio_with_dynamics):
            reverb_audio = np.zeros_like(audio_with_dynamics)
            reverb_audio[reverb_delay:] = audio_with_dynamics[:-reverb_delay] * 0.15
            audio_with_dynamics += reverb_audio
        
        return audio_with_dynamics
