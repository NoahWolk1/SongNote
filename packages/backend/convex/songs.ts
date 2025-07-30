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
    pitch: v.optional(v.number()),
    isHummingBased: v.boolean(),
    hummingAudioUrl: v.optional(v.string()),
  },
  handler: async (ctx, { title, lyrics, voiceStyle, mood, pitch, isHummingBased, hummingAudioUrl }) => {
    const userId = await getUserId(ctx);
    if (!userId) throw new Error("User not found");
    
    const songId = await ctx.db.insert("songs", { 
      userId, 
      title, 
      lyrics, 
      voiceStyle,
      mood,
      pitch,
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
    pitch: v.optional(v.number()),
    generatedSongUrl: v.optional(v.string()),
    hummingAudioUrl: v.optional(v.string()),
  },
  handler: async (ctx, { id, title, lyrics, voiceStyle, mood, pitch, generatedSongUrl, hummingAudioUrl }) => {
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
    if (pitch !== undefined) updates.pitch = pitch;
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

// Create song with AI singing generation using Convex
export const createSongWithAI = action({
  args: {
    title: v.string(),
    lyrics: v.string(),
    voiceStyle: v.string(),
    mood: v.optional(v.string()),
    pitch: v.optional(v.number()),
    includeMusic: v.optional(v.boolean()),
  },
  handler: async (ctx, { title, lyrics, voiceStyle, mood, pitch, includeMusic }) => {
    const userId = await getUserId(ctx);
    if (!userId) throw new Error("User not found");
    
    try {
      console.log("🎤 Generating singing with Convex AI Singer...");
      
      // Generate singing using our Convex AI singer
      const singingResult = await ctx.runAction(api.ai_singer.generateSinging, {
        lyrics,
        voiceStyle,
        mood: mood || "happy",
        pitchAdjustment: pitch || 0,
        includeMusic: includeMusic ?? true,
      });
      
      if (!singingResult.success) {
        throw new Error(singingResult.error || "Failed to generate singing");
      }
      
      // Create the song record
      const songId = await ctx.runMutation(api.songs.createSong, {
        title,
        lyrics,
        voiceStyle,
        mood: mood || "happy",
        pitch: pitch || 0,
        isHummingBased: false,
      });
      
      // Update the song with the generated audio
      const audioDataUrl = `data:audio/wav;base64,${singingResult.audio}`;
      await ctx.runMutation(api.songs.updateSong, {
        id: songId,
        generatedSongUrl: audioDataUrl,
      });
      
      console.log("✅ Song created successfully with AI singing");
      
      return {
        success: true,
        songId,
        audioUrl: audioDataUrl,
        duration: singingResult.duration_seconds,
        synthesisMethod: singingResult.synthesis_method,
      };
      
    } catch (error) {
      console.error("❌ Song generation failed:", error);
      throw new Error(`Failed to generate song: ${error}`);
    }
  },
});


