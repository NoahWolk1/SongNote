import type { Auth } from "convex/server";
import { v } from "convex/values";
import { internal } from "../convex/_generated/api";
import { mutation, query } from "./_generated/server";

export const getUserId = async (ctx: { auth: Auth }) => {
  return (await ctx.auth.getUserIdentity())?.subject;
};

// Get all songs for a specific user (legacy endpoint for notes compatibility)
export const getNotes = query({
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

// Get song for a specific song (legacy endpoint for notes compatibility)
export const getNote = query({
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

// Create a new song for a user (legacy endpoint for notes compatibility)
export const createNote = mutation({
  args: {
    title: v.string(),
    content: v.string(),
    isSummary: v.boolean(),
  },
  handler: async (ctx, { title, content, isSummary }) => {
    const userId = await getUserId(ctx);
    if (!userId) throw new Error("User not found");
    const songId = await ctx.db.insert("songs", { 
      userId, 
      title, 
      lyrics: content,  // Map content to lyrics
      voiceStyle: "pop",  // Default voice style
      mood: "happy",  // Default mood
      isHummingBased: false,  // Default to text-only
      createdAt: Date.now()
    });

    if (isSummary) {
      await ctx.scheduler.runAfter(0, internal.openai.summary, {
        id: songId,
        title,
        content,
      });
    }

    return songId;
  },
});

export const deleteNote = mutation({
  args: {
    noteId: v.id("songs"),
  },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.noteId);
  },
});
