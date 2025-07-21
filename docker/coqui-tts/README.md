# 🎵 Musical TTS Singing Service

An advanced AI singing synthesis service that converts text to realistic singing using **TTS + Musical Post-Processing**.

## ✨ What's New

This service has been completely redesigned to address the limitations of basic harmonic synthesis:

- **Real Words**: Generates actual singing with proper pronunciation, not just musical scales
- **Natural Voice Leading**: Smooth melodic transitions with max 2-step jumps (no jarring octave leaps)
- **Musical Intelligence**: Analyzes text for syllables, emphasis, and natural phrasing
- **Vocal Effects**: Adds vibrato, formants, breath sounds, and vocal envelopes
- **Multiple Styles**: Pop, ballad, jazz with appropriate scales and vocal ranges

## 🎤 How It Works

### Option 1: TTS + Musical Processing (Premium)
When OpenAI API key is provided:
1. Converts text to natural speech using OpenAI TTS (Nova voice)
2. Analyzes text for musical phrasing and syllable structure
3. Generates intelligent melody using pentatonic scales
4. Applies pitch shifting and musical post-processing
5. Adds vocal effects (vibrato, formants, breath sounds)

### Option 2: Enhanced Harmonic Synthesis (Free)
When no API key is provided:
1. Analyzes text characteristics (syllables, word emphasis)
2. Generates text-based melody with natural voice leading
3. Creates harmonic singing with vocal formants
4. Applies vocal envelope and breathing simulation

## 🚀 Quick Start

### 1. Basic Usage (Free)
```bash
# Test the service
curl -X GET http://localhost:8002/health

# Generate singing (free harmonic synthesis)
curl -X POST http://localhost:8002/generate-singing \
  -H "Content-Type: application/json" \
  -d '{"lyrics": "Love is in the air tonight", "voice_style": "pop", "mood": "happy"}'
```

### 2. Premium Usage (TTS + Musical Processing)
```bash
# Set up OpenAI API key
cp .env.example .env
# Edit .env and add your OpenAI API key

# Restart services to enable TTS
docker-compose down && docker-compose up -d

# Generate enhanced singing
curl -X POST http://localhost:8002/generate-singing \
  -H "Content-Type: application/json" \
  -d '{"lyrics": "Love is in the air tonight", "voice_style": "pop", "mood": "happy"}'
```

## 🎼 Voice Styles & Musical Features

### Pop Style
- **Scale**: C Major Pentatonic (C, D, E, G, A)
- **Range**: 220-500 Hz (comfortable singing range)
- **Characteristics**: Catchy melodies, moderate tempo

### Ballad Style  
- **Scale**: G Major (G, A, B, C, D, E, F)
- **Range**: 180-400 Hz (lower, intimate range)
- **Characteristics**: Slower, more emotional delivery

### Jazz Style
- **Scale**: A Minor Pentatonic (A, C, D, E, G#)
- **Range**: 200-450 Hz (expressive range)
- **Characteristics**: Sophisticated harmony, swing feel

## 🎯 Musical Intelligence Features

### Smart Melody Generation
- **Syllable Counting**: Accurate estimation for proper timing
- **Word Emphasis**: Content words get melodic emphasis
- **Phrase Arcs**: Natural rise and fall within phrases
- **Voice Leading**: Maximum 2-step jumps, smooth transitions
- **Vocal Range**: Stays within comfortable singing range

### Text Analysis
- **Emphasis Detection**: "love", "heart", "dream" get high emphasis
- **Phrase Breaks**: Natural breaks at conjunctions and breath points
- **Syllable Duration**: 400ms per syllable for natural singing tempo
- **Resolution**: Phrases end on lower notes for natural closure

## 🎛️ Vocal Effects Pipeline

### TTS Mode (Premium)
1. **Pitch Shifting**: Maps speech to target melody frequencies
2. **Time Stretching**: Adjusts duration for natural singing timing
3. **Vibrato**: 5.5 Hz modulation with 2% depth
4. **Formant Enhancement**: Boosts vocal formants (650, 1080, 2650 Hz)
5. **Breath Sounds**: Subtle vocal texture and breathing
6. **Vocal Envelope**: Natural attack and release curves

### Harmonic Mode (Free)
1. **Harmonic Series**: Fundamental + octave + fifth + third
2. **Vocal Formants**: Singing-optimized frequency response
3. **Vibrato**: Natural 5.0 Hz modulation
4. **Envelope Shaping**: Attack, sustain, and decay curves
5. **Breath Simulation**: Realistic vocal breathing patterns

## 📊 API Response

```json
{
  "audio_url": "data:audio/wav;base64,UklGRn...",
  "format": "wav",
  "duration_seconds": 4.2,
  "synthesis_method": "tts_musical_processing", // or "harmonic_singing"
  "voice_style": "pop",
  "mood": "happy"
}
```

## 🔧 Configuration

### Environment Variables
```bash
# Required for TTS + Musical Processing
OPENAI_API_KEY=your_api_key_here

# Optional customization
OPENAI_TTS_MODEL=tts-1        # or tts-1-hd for higher quality
OPENAI_TTS_VOICE=nova         # optimized for singing conversion
```

### Voice Styles
- `pop`: Catchy, accessible melodies
- `ballad`: Emotional, intimate delivery  
- `jazz`: Sophisticated, expressive

### Moods
- `happy`: Uplifting melodic patterns
- `sad`: Lower register, minor inflections
- `energetic`: Dynamic range and tempo

## 🎵 Example Usage

```python
import requests

# Generate singing
response = requests.post('http://localhost:8002/generate-singing', json={
    "lyrics": "Somewhere over the rainbow, way up high",
    "voice_style": "ballad",
    "mood": "happy"
})

result = response.json()
print(f"Duration: {result['duration_seconds']}s")
print(f"Method: {result['synthesis_method']}")

# Audio is in result['audio_url'] as base64 data URL
```

## 🚀 What's Different from Before?

### ❌ Old Harmonic Service Issues:
- Generated musical scales, not singing
- No word pronunciation
- Jarring melodic jumps
- Basic harmonic tones only

### ✅ New Musical TTS Service:
- **Real Words**: Actual pronunciation and singing
- **Smart Melodies**: Text-aware melody generation
- **Natural Voice Leading**: Smooth, musical transitions
- **Vocal Realism**: Vibrato, formants, breath sounds
- **Multiple Modes**: TTS + processing OR enhanced harmonic fallback

## 🎤 Perfect for:
- Converting lyrics to singing demos
- Musical prototyping and composition
- Voice melody generation
- Singing synthesis research
- AI music applications

The service now generates **actual singing** with proper words and natural musical flow, exactly as requested! 🎵
