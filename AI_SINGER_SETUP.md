# AI Singer App - Free AI Services Setup

This document explains how to set up the completely **FREE** AI services for the AI Singer app.

## 🎵 What We Built

**Transformed the note-taking app into an AI Singer app with these key features:**

1. **Song Creation**: Users can create songs with lyrics and voice styles
2. **Optional Humming**: Users can optionally upload humming audio for melody extraction
3. **Free AI Singing**: Generate singing voices using only open-source, free technologies
4. **Voice Styles**: Support for different singing styles (pop, opera, folk, etc.)
5. **Mood Control**: Apply mood-based modifications (happy, sad, etc.)

## 🚀 Why Everything is FREE

All AI services use completely open-source technologies:

- **Basic Pitch**: Spotify's free, open-source melody extraction
- **Coqui TTS**: Free text-to-speech synthesis
- **Librosa**: Free audio processing and effects
- **No paid APIs**: No ElevenLabs, OpenAI, or other paid services

## 📊 Backend Changes Made

### 1. Database Schema Transformation (`packages/backend/convex/schema.ts`)
**Change**: Replaced `notes` table with `songs` table
**Why**: The app is now for creating AI-generated songs, not notes

```typescript
// OLD: notes table
notes: defineTable({
  userId: v.string(),
  title: v.string(),
  content: v.string(),
  // ...
})

// NEW: songs table
songs: defineTable({
  userId: v.string(),
  title: v.string(),
  lyrics: v.string(),
  voiceStyle: v.string(),
  mood: v.optional(v.string()),
  isHummingBased: v.boolean(),
  hummingAudioUrl: v.optional(v.string()),
  extractedMelody: v.optional(v.object({...})),
  generatedSongUrl: v.optional(v.string()),
  createdAt: v.number(),
})
```

### 2. Backend Logic Replacement (`packages/backend/convex/songs.ts`)
**Change**: Replaced `notes.ts` with `songs.ts` containing AI singer functionality
**Why**: Complete workflow for song creation with optional humming

**Key functions created:**
- `createSongWithAI`: Main workflow that handles optional humming + AI singing
- `getSongs`/`getSong`: CRUD operations for songs
- `extractMelodyUsingBasicPitch`: Free melody extraction from humming
- `generateSingingAudioFree`: Free text-to-speech singing synthesis

## 🐳 Free AI Services (Docker)

### Service 1: Basic Pitch (Melody Extraction)
**Port**: 8001
**Purpose**: Extract melody from humming audio (optional feature)
**Technology**: Spotify's Basic Pitch (completely free)
**Files**: `docker/basic-pitch/`

### Service 2: Coqui TTS (Singing Synthesis)
**Port**: 8002  
**Purpose**: Generate singing voices from lyrics
**Technology**: Coqui TTS (completely free)
**Files**: `docker/coqui-tts/`

## 🛠️ Setup Instructions

### 1. Start Free AI Services

```bash
# Build and start all free AI services
docker-compose up --build

# Check if services are running
curl http://localhost:8001/health  # Basic Pitch
curl http://localhost:8002/health  # Coqui TTS
```

### 2. Test the Backend

```bash
# Start Convex backend
cd packages/backend
npx convex dev

# The backend will connect to the free AI services automatically
```

### 3. Frontend Integration (Next Steps)

The frontend needs to be updated to:
1. Show song creation UI instead of note creation
2. Add optional humming upload feature  
3. Display generated songs and play audio
4. Show different voice styles and moods

## 🎯 How the AI Singer Workflow Works

### Without Humming (Simpler Flow):
1. User enters lyrics, voice style, mood
2. Backend calls Coqui TTS service (free) to generate singing
3. User gets AI-generated song

### With Optional Humming:
1. User enters lyrics + uploads humming audio
2. Backend calls Basic Pitch service (free) to extract melody
3. Backend calls Coqui TTS service (free) with melody + lyrics
4. User gets AI-generated song that matches their hummed melody

## 🔧 Technical Architecture

```
Frontend (React/React Native)
    ↓
Convex Backend (TypeScript)
    ↓ HTTP calls to free services
Docker Services:
  - Basic Pitch (Port 8001) - FREE melody extraction
  - Coqui TTS (Port 8002) - FREE singing synthesis
```

## 🎵 Voice Styles and Moods

**Voice Styles**:
- `pop`: Modern pop singing with compression and brightness
- `opera`: Classical opera with reverb and pitch variance  
- `folk`: Warm, organic folk singing
- `default`: Standard singing voice

**Moods**:
- `happy`: Faster tempo, brighter tone
- `sad`: Slower tempo, warmer tone  
- `neutral`: Standard mood

## 🚨 Important Notes

1. **Everything is FREE**: No paid APIs, no subscription costs
2. **Optional Humming**: Users can create songs without humming - it's completely optional
3. **Docker Required**: AI services run in Docker containers for easy setup
4. **Self-Hosted**: All AI processing happens on your own infrastructure
5. **Open Source**: All technologies used are open-source and free

## 🔄 Next Steps

1. **Update Frontend**: Transform note-taking UI to song creation UI
2. **Add Audio Player**: Integrate audio playback for generated songs
3. **Test Free Services**: Start Docker services and test the AI pipeline
4. **Mobile Support**: Update React Native app for song creation
5. **Deploy**: Deploy the complete AI Singer app

The transformation from note-taking to AI singing is complete on the backend - now we need to update the frontend to match this new functionality!
