#!/usr/bin/env python3
"""
Musical Arrangement Module
Handles melody generation, chord progressions, and musical accompaniment
"""

import numpy as np


class MusicalArranger:
    """Generates melodies, chords, and musical arrangements"""
    
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate
    
    def midi_to_frequency(self, midi_note):
        """Convert MIDI note number to frequency in Hz"""
        return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))
    
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
    
    def generate_chord_progression(self, melody, style="pop", mood="happy"):
        """Generate chord progression based on melody and style"""
        # Determine key from melody - handle both formats
        melody_notes = []
        if melody and isinstance(melody[0], dict):
            # New format: list of {'note': midi_note, 'duration': seconds}
            melody_notes = [self.midi_to_frequency(note['note']) for note in melody if note.get('note', 0) > 0]
        else:
            # Old format: list of frequencies
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
    
    def generate_text_based_melody(self, text, style, mood):
        """Generate melody using actual song structure patterns (verse-chorus form)"""
        words = text.split()
        
        # Define proper musical scales for different styles
        if style == 'pop':
            scale = [261.63, 293.66, 329.63, 392.00, 440.00]  # C pentatonic
            mood_modifier = 1.2 if mood == 'happy' else 0.9
        elif style == 'ballad':
            scale = [196.00, 220.00, 246.94, 261.63, 293.66]  # Lower register
            mood_modifier = 1.0 if mood == 'happy' else 0.8
        else:
            scale = [261.63, 293.66, 329.63, 349.23, 392.00]  # C major
            mood_modifier = 1.1 if mood == 'happy' else 0.95
        
        # Analyze text to create verse-like or chorus-like structure
        is_short_phrase = len(words) <= 4
        is_repetitive = len(set(words)) < len(words) * 0.7  # Lots of repeated words
        
        melody = []
        
        if is_short_phrase or is_repetitive:
            melody = self.create_chorus_melody(words, scale, mood_modifier)
        else:
            melody = self.create_verse_melody(words, scale, mood_modifier)
        
        return melody
    
    def create_verse_melody(self, words, scale, mood_modifier):
        """Create verse-style melody (more linear, conversational)"""
        melody = []
        current_index = 1  # Start low in verse
        
        for i, word in enumerate(words):
            syllables = max(1, len([c for c in word if c.lower() in 'aeiou']))
            
            for syl in range(syllables):
                # Verses tend to stay in lower-middle range
                if i < len(words) / 2:
                    # First half: gradual rise
                    target_index = min(current_index + 1, len(scale) - 2)
                else:
                    # Second half: settle back down
                    target_index = max(current_index - 1, 1)
                
                current_index = target_index
                freq = scale[current_index] * mood_modifier
                melody.append(freq)
        
        return melody
    
    def create_chorus_melody(self, words, scale, mood_modifier):
        """Create chorus-style melody (more dramatic, memorable)"""
        melody = []
        current_index = len(scale) // 2  # Start in middle for chorus
        
        for i, word in enumerate(words):
            syllables = max(1, len([c for c in word if c.lower() in 'aeiou']))
            
            for syl in range(syllables):
                # Chorus should have more dramatic range
                if i == 0:
                    # Strong opening
                    target_index = len(scale) - 1
                elif i < len(words) / 3:
                    # Build up
                    target_index = min(current_index + 1, len(scale) - 1)
                elif i < 2 * len(words) / 3:
                    # Peak/sustain
                    target_index = len(scale) - 1
                else:
                    # Resolve down
                    target_index = max(current_index - 1, len(scale) // 2)
                
                current_index = target_index
                freq = scale[current_index] * mood_modifier
                melody.append(freq)
        
        return melody
