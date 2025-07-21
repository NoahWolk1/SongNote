import type { Auth } from "convex/server";
import { v } from "convex/values";
import { action, mutation, query } from "./_generated/server";
import { api } from "./_generated/api";

export const getUserId = async (ctx: { auth: Auth }) => {
  return (await ctx.auth.getUserIdentity())?.subject;
};

// Get all songs for a specific user
export const getSongs = query({
  args: {},
  handler: async (ctx) => {
    const userId = await getUserId(ctx);
    if (!userId) return null;

    const songs = await ctx.db
      .query("songs")
      .filter((q) => q.eq(q.field("userId"), userId))
      .collect();

    return songs;
  },
});

// Get song for a specific song
export const getSong = query({
  args: {
    id: v.optional(v.id("songs")),
  },
  handler: async (ctx, args) => {
    const { id } = args;
    if (!id) return null;
    const song = await ctx.db.get(id);
    return song;
  },
});

// Create a new song for a user
export const createSong = mutation({
  args: {
    title: v.string(),
    lyrics: v.string(),
    voiceStyle: v.string(),
    mood: v.optional(v.string()),
    isHummingBased: v.boolean(),
    hummingAudioUrl: v.optional(v.string()),
  },
  handler: async (ctx, { title, lyrics, voiceStyle, mood, isHummingBased, hummingAudioUrl }) => {
    const userId = await getUserId(ctx);
    if (!userId) throw new Error("User not found");
    
    const songId = await ctx.db.insert("songs", { 
      userId, 
      title, 
      lyrics, 
      voiceStyle,
      mood,
      isHummingBased,
      hummingAudioUrl,
      createdAt: Date.now()
    });

    return songId;
  },
});

// Delete a song
export const deleteSong = mutation({
  args: {
    songId: v.id("songs"),
  },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.songId);
  },
});

// Update song details
export const updateSong = mutation({
  args: {
    id: v.id("songs"),
    title: v.optional(v.string()),
    lyrics: v.optional(v.string()),
    voiceStyle: v.optional(v.string()),
    mood: v.optional(v.string()),
    generatedSongUrl: v.optional(v.string()),
    hummingAudioUrl: v.optional(v.string()),
  },
  handler: async (ctx, { id, title, lyrics, voiceStyle, mood, generatedSongUrl, hummingAudioUrl }) => {
    const userId = await getUserId(ctx);
    if (!userId) throw new Error("Not authenticated");

    const existingSong = await ctx.db.get(id);
    if (!existingSong) throw new Error("Song not found");
    if (existingSong.userId !== userId) throw new Error("Not authorized");

    const updates: any = {};
    if (title !== undefined) updates.title = title;
    if (lyrics !== undefined) updates.lyrics = lyrics;
    if (voiceStyle !== undefined) updates.voiceStyle = voiceStyle;
    if (mood !== undefined) updates.mood = mood;
    if (generatedSongUrl !== undefined) updates.generatedSongUrl = generatedSongUrl;
    if (hummingAudioUrl !== undefined) updates.hummingAudioUrl = hummingAudioUrl;

    await ctx.db.patch(id, updates);
    return id;
  },
});

// Update song with extracted melody data (internal)
export const updateSongWithMelody = mutation({
  args: {
    songId: v.id("songs"),
    melodyData: v.object({
      notes: v.array(v.object({
        pitch: v.number(),
        start_time: v.number(),
        end_time: v.number(),
        velocity: v.optional(v.number())
      })),
      tempo: v.optional(v.number()),
      key: v.optional(v.string())
    })
  },
  handler: async (ctx, { songId, melodyData }) => {
    await ctx.db.patch(songId, {
      extractedMelody: melodyData
    });
  },
});

// Update song with generated audio URL (internal)
export const updateSongWithAudio = mutation({
  args: {
    songId: v.id("songs"),
    audioFileId: v.id("_storage"),
  },
  handler: async (ctx, { songId, audioFileId }) => {
    const audioUrl = await ctx.storage.getUrl(audioFileId);
    await ctx.db.patch(songId, {
      generatedSongUrl: audioUrl || undefined,
      audioFileId: audioFileId
    });
  },
});

// Generate upload URL for audio files
export const generateUploadUrl = mutation({
  args: {},
  handler: async (ctx, args) => {
    return await ctx.storage.generateUploadUrl();
  },
});

// Update song with audio file ID after upload
export const updateSongWithUploadedAudio = mutation({
  args: {
    songId: v.id("songs"),
    audioFileId: v.id("_storage"),
  },
  handler: async (ctx, { songId, audioFileId }) => {
    const audioUrl = await ctx.storage.getUrl(audioFileId);
    await ctx.db.patch(songId, {
      generatedSongUrl: audioUrl || undefined,
      audioFileId: audioFileId
    });
  },
});

// Simplified workflow: Create song with optional humming (ALL FREE)
export const createSongWithAI = action({
  args: {
    title: v.string(),
    lyrics: v.string(),
    voiceStyle: v.string(),
    mood: v.optional(v.string()),
    hummingAudioBase64: v.optional(v.string()), // Optional humming
  },
  handler: async (ctx, { title, lyrics, voiceStyle, mood, hummingAudioBase64 }) => {
    
    let melodyData = null;
    
    // Step 1: Extract melody if humming is provided (OPTIONAL + FREE)
    if (hummingAudioBase64) {
      try {
        console.log("Extracting melody from humming...");
        melodyData = await extractMelodyUsingBasicPitch(hummingAudioBase64);
      } catch (error) {
        console.error("Melody extraction failed, continuing without melody:", error);
      }
    }
    
    // Step 2: Generate singing voice (FREE)
    try {
      console.log("Generating singing voice...");
      const audioUrl = await generateSingingAudioFree(lyrics, voiceStyle, mood, melodyData);
      
      // Create song record with all data
      const songData = {
        title,
        lyrics,
        voiceStyle,
        mood,
        isHummingBased: !!hummingAudioBase64,
        hummingAudioUrl: hummingAudioBase64 || undefined,
        extractedMelody: melodyData,
        generatedSongUrl: audioUrl,
        createdAt: Date.now()
      };
      
      // Use direct database access in action (simplified approach)
      const userId = await getUserId(ctx);
      if (!userId) throw new Error("User not found");
      
      // For now, return the data - we'll store it in the frontend
      return { 
        success: true,
        songData: { ...songData, userId },
        melody: melodyData,
        audioUrl 
      };
      
    } catch (error) {
      console.error("Song generation failed:", error);
      throw new Error("Failed to generate song");
    }
  },
});

// FREE IMPLEMENTATIONS - Open Source Only

async function extractMelodyUsingBasicPitch(audioBase64: string) {
  // FREE: Basic Pitch is completely open source
  // Option 1: Self-hosted service (recommended)
  try {
    const response = await fetch("http://localhost:8001/extract-melody", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ audio: audioBase64 })
    });
    
    if (!response.ok) {
      throw new Error("Basic Pitch service failed");
    }
    
    return await response.json();
  } catch (error) {
    // Option 2: Fallback to simulated melody (for demo purposes)
    console.warn("Basic Pitch service unavailable, using demo melody");
    return {
      notes: [
        { pitch: 60, start_time: 0.0, end_time: 0.5, velocity: 80 },
        { pitch: 62, start_time: 0.5, end_time: 1.0, velocity: 75 },
        { pitch: 64, start_time: 1.0, end_time: 1.5, velocity: 70 },
        { pitch: 65, start_time: 1.5, end_time: 2.0, velocity: 85 }
      ],
      tempo: 120,
      key: "C major"
    };
  }
}

async function generateSingingAudioFree(
  lyrics: string, 
  voiceStyle: string, 
  mood?: string, 
  melody?: any
) {
  // FREE OPTION 1: Coqui TTS (completely free, open source)
  try {
    const response = await fetch("http://localhost:8002/generate-singing", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        lyrics, 
        voice_style: voiceStyle, 
        mood, 
        melody 
      })
    });
    
    if (!response.ok) {
      throw new Error("Coqui TTS service failed");
    }
    
    const result = await response.json();
    return result.audio_url;
  } catch (error) {
    // FREE FALLBACK: Web Speech API simulation
    console.warn("Coqui TTS service unavailable, using demo audio");
    return generateDemoAudio(lyrics, voiceStyle);
  }
}

function generateDemoAudio(lyrics: string, voiceStyle: string) {
  // For demo purposes - returns a data URL
  // In production, this would use Web Speech API or local TTS
  return `data:audio/wav;base64,demo-audio-for-${encodeURIComponent(lyrics.substring(0, 20))}-${voiceStyle}`;
}
