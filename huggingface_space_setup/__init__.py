#!/usr/bin/env python3
"""
Musical TTS Singing Package
A modular system for converting text to realistic singing with musical accompaniment
"""

from .musical_singer import MusicalTTSSinger
from .tts_engines import TTSEngines
from .text_analysis import TextAnalyzer
from .musical_arrangement import MusicalArranger
from .audio_processing import AudioProcessor

__version__ = "1.0.0"
__author__ = "Musical TTS Team"

__all__ = [
    "MusicalTTSSinger",
    "TTSEngines", 
    "TextAnalyzer",
    "MusicalArranger",
    "AudioProcessor"
]
