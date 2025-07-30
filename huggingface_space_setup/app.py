#!/usr/bin/env python3
"""
Musical TTS Singing API Server for Hugging Face Spaces
FastAPI application providing REST API for the musical TTS singing service
"""

import os
import base64
import tempfile
import json
import soundfile as sf
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import your existing AI singing modules
from musical_singer import MusicalTTSSinger
from tts_engines import GTTS_AVAILABLE, EDGE_TTS_AVAILABLE

app = FastAPI(title="AI Singer API", description="Generate singing from text with musical accompaniment")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the musical singer
print("🎵 Initializing Musical TTS Singer...")
musical_singer = MusicalTTSSinger()
print("✅ Musical TTS Singer initialized!")

@app.get('/health')
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "musical-tts-singing",
        "model_loaded": True,
        "free_tts_available": musical_singer.free_tts_available,
        "gtts_available": GTTS_AVAILABLE,
        "edge_tts_available": EDGE_TTS_AVAILABLE
    }

@app.post('/generate-singing')
async def generate_singing(request: Request):
    """Generate singing from text with musical accompaniment"""
    try:
        data = await request.json()
        lyrics = data.get('lyrics', '')
        voice_style = data.get('voice_style', 'pop')
        mood = data.get('mood', 'happy')
        include_music = data.get('include_music', True)
        tts_engine = data.get('tts_engine', 'auto')
        vocal_volume = data.get('vocal_volume', 0.9)
        music_volume = data.get('music_volume', 0.15)
        
        if not lyrics:
            raise HTTPException(status_code=400, detail="No lyrics provided")
        
        print(f"🎤 Received request: '{lyrics}' ({voice_style}, {mood}) - Music: {include_music}, Engine: {tts_engine}")
        print(f"🎛️ Mix levels - Vocals: {vocal_volume}, Music: {music_volume}")
        
        # Set TTS engine if specified
        if tts_engine != 'auto':
            musical_singer.tts_engines.preferred_engine = tts_engine
        
        # Set mix levels
        musical_singer.audio_processor.vocal_mix_level = vocal_volume
        musical_singer.audio_processor.music_mix_level = music_volume
        
        # Generate singing
        if include_music:
            audio = musical_singer.create_singing_voice(lyrics, voice_style, mood)
            synthesis_method = f"free_tts_musical_with_accompaniment" if musical_singer.free_tts_available else "system_tts_musical_with_accompaniment"
        else:
            # Generate vocals only
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
        
        return {
            "audio_url": audio_url,
            "format": "wav",
            "duration_seconds": len(audio) / musical_singer.sample_rate,
            "synthesis_method": synthesis_method,
            "voice_style": voice_style,
            "mood": mood,
            "includes_music": include_music,
            "tts_engine": tts_engine,
            "vocal_volume": vocal_volume,
            "music_volume": music_volume
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate singing: {str(e)}")

@app.get('/test-singing')
async def test_singing():
    """Test endpoint to verify the service is working"""
    try:
        audio = musical_singer.create_singing_voice("Hello world, this is a test", 'pop', 'happy')
        synthesis_method = "free_tts_musical" if musical_singer.free_tts_available else "system_tts_musical"
        return {
            "status": "success",
            "duration": len(audio) / musical_singer.sample_rate,
            "method": synthesis_method
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/')
async def root():
    """Root endpoint with service information"""
    return {
        "message": "AI Singer API is running!",
        "endpoints": {
            "health": "/health",
            "generate_singing": "/generate-singing",
            "test_singing": "/test-singing"
        },
        "usage": {
            "POST /generate-singing": {
                "body": {
                    "lyrics": "Your song lyrics here",
                    "voice_style": "pop|rock|jazz|classical",
                    "mood": "happy|sad|energetic|calm",
                    "include_music": True,
                    "tts_engine": "auto|gtts|edge",
                    "vocal_volume": 0.9,
                    "music_volume": 0.15
                }
            }
        }
    }

if __name__ == '__main__':
    print("🎵 Starting Musical TTS Singing Service for Hugging Face Spaces...")
    print("🎤 Service ready on port 7860")
    
    if musical_singer.free_tts_available:
        print("✅ FREE TTS enabled - will use Google/Edge TTS + musical effects")
        if GTTS_AVAILABLE:
            print("  🌟 Google TTS (gTTS) available")
        if EDGE_TTS_AVAILABLE:
            print("  🌟 Microsoft Edge TTS available")
    else:
        print("⚠️ No free TTS available - will use system TTS synthesis")
        print("💡 Install free TTS: pip install gtts edge-tts librosa")
    
    uvicorn.run(app, host='0.0.0.0', port=7860) 