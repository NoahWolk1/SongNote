# AI Singer - Hugging Face Space Setup

This directory contains all the files needed to deploy your AI singing service to Hugging Face Spaces.

## Files Included

- **`Dockerfile`** - Docker configuration for the Hugging Face Space
- **`app.py`** - FastAPI application (converted from your Flask app)
- **`requirements.txt`** - Python dependencies
- **`musical_singer.py`** - Your main AI singing orchestrator
- **`tts_engines.py`** - Text-to-speech engine management
- **`text_analysis.py`** - Text analysis for musical phrasing
- **`musical_arrangement.py`** - Musical arrangement generation
- **`audio_processing.py`** - Audio processing and effects
- **`__init__.py`** - Python package initialization

## Setup Instructions

1. **Go to your Hugging Face Space repository:**
   - Navigate to: https://huggingface.co/spaces/Rocketlaunchers/AI_Singer

2. **Upload all files:**
   - Upload all files from this directory to the root of your Space repository
   - Make sure to include all the `.py` files

3. **Commit and push:**
   - Commit all changes
   - Push to trigger the build

4. **Wait for build:**
   - Hugging Face will automatically build your Docker container
   - This may take 5-10 minutes for the first build

5. **Test the service:**
   - Once built, your Space will be available at: `https://rocketlaunchers-ai-singer.hf.space`
   - Test the health endpoint: `https://rocketlaunchers-ai-singer.hf.space/health`
   - Test singing generation: `https://rocketlaunchers-ai-singer.hf.space/generate-singing`

## API Endpoints

### Health Check
```
GET /health
```

### Generate Singing
```
POST /generate-singing
Content-Type: application/json

{
  "lyrics": "Your song lyrics here",
  "voice_style": "pop",
  "mood": "happy",
  "include_music": true,
  "tts_engine": "auto",
  "vocal_volume": 0.9,
  "music_volume": 0.15
}
```

### Test Singing
```
GET /test-singing
```

## Integration with Your Expo App

Once your Hugging Face Space is running, your Convex HTTP proxy will automatically work with it. The proxy is already configured to forward requests to:

```
https://rocketlaunchers-ai-singer.hf.space/generate-singing
```

## Troubleshooting

- **Build fails:** Check the build logs in your Hugging Face Space
- **Dependencies missing:** Ensure all files are uploaded, including `requirements.txt`
- **Audio generation fails:** Check the logs in your Space's "Logs" tab
- **CORS issues:** The FastAPI app includes CORS middleware to handle cross-origin requests

## Features

Your AI singing service includes:
- ✅ Free TTS engines (Google TTS, Microsoft Edge TTS)
- ✅ Musical post-processing and effects
- ✅ Full musical arrangement with accompaniment
- ✅ Multiple voice styles (pop, rock, jazz, classical)
- ✅ Multiple moods (happy, sad, energetic, calm)
- ✅ Adjustable vocal and music volume levels
- ✅ Base64 audio encoding for easy web/mobile integration 