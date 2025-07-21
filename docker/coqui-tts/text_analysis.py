#!/usr/bin/env python3
"""
Text Analysis Module
Handles text processing for musical applications including syllable counting, 
phrasing analysis, and phonetic mapping
"""

import re


class TextAnalyzer:
    """Analyzes text for musical phrasing and syllable structures"""
    
    def __init__(self):
        self.emphasis_words = ['love', 'heart', 'dream', 'night', 'light', 'time', 'life', 'world', 'feel', 'know']
    
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
        if word in self.emphasis_words or len(word) > 6:
            return 'high'
        elif len(word) > 3:
            return 'medium'
        else:
            return 'low'
    
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
        syllables = []
        
        for i, char in enumerate(word):
            if char in vowels:
                if vowel_found and current_syllable:
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
                current_syllable += char
                consonants += char
        
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
                extended.extend(melody_notes[:min(len(melody_notes), syllable_count - len(extended))])
            return extended[:syllable_count]
        else:
            # Trim melody to match syllables
            return melody_notes[:syllable_count]
