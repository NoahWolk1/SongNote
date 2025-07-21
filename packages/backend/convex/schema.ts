import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  songs: defineTable({
    userId: v.string(),
    title: v.string(),
    lyrics: v.string(),
    
    // Optional humming-related fields
    hummingAudioUrl: v.optional(v.string()),
    extractedMelody: v.optional(v.object({
      notes: v.array(v.object({
        pitch: v.number(),
        start_time: v.number(),
        end_time: v.number(),
        velocity: v.optional(v.number())
      })),
      tempo: v.optional(v.number()),
      key: v.optional(v.string())
    })),
    
    // AI-generated results
    generatedSongUrl: v.optional(v.string()),
    audioFileId: v.optional(v.id("_storage")), // Reference to stored audio file
    voiceStyle: v.string(), // "male", "female", "child", etc.
    mood: v.optional(v.string()), // "happy", "sad", "energetic", etc.
    summary: v.optional(v.string()), // AI-generated summary (legacy)
    
    // Metadata
    createdAt: v.number(),
    isHummingBased: v.boolean(), // true if user provided humming, false for text-only
  }),
});
