"use client";

import { api } from "@packages/backend/convex/_generated/api";
import type { Id } from "@packages/backend/convex/_generated/dataModel";
import { useMutation } from "convex/react";
import { useState } from "react";

interface GenerateSongProps {
  songId: Id<"songs">;
  lyrics: string;
  voiceStyle: string;
  disabled?: boolean;
}

const GenerateSong = ({ songId, lyrics, voiceStyle, disabled }: GenerateSongProps) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const generateUploadUrl = useMutation(api.songs.generateUploadUrl);
  const updateSongWithUploadedAudio = useMutation(api.songs.updateSongWithUploadedAudio);

  const generateSong = async () => {
    setIsGenerating(true);
    setError(null);
    
    try {
      // Call our AI backend to generate singing
      const response = await fetch('http://localhost:8002/generate-singing', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          lyrics: lyrics,
          voice_style: voiceStyle
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate song');
      }

      const data = await response.json();
      
      if (data.audio_url) {
        // Convert base64 data URL to blob
        const base64Data = data.audio_url.split(',')[1];
        const audioBlob = new Blob([
          Uint8Array.from(atob(base64Data), c => c.charCodeAt(0))
        ], { type: 'audio/wav' });
        
        // Get upload URL from Convex
        const uploadUrl = await generateUploadUrl();
        
        // Upload the audio file
        const uploadResponse = await fetch(uploadUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'audio/wav' },
          body: audioBlob,
        });
        
        if (!uploadResponse.ok) {
          throw new Error('Failed to upload audio file');
        }
        
        const { storageId } = await uploadResponse.json();
        
        // Update the song with the uploaded file
        await updateSongWithUploadedAudio({
          songId: songId,
          audioFileId: storageId
        });
        
        setSuccess(true);
      } else {
        throw new Error('No audio generated');
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate song');
    } finally {
      setIsGenerating(false);
    }
  };

  if (success) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex">
          <div className="ml-3">
            <p className="text-sm font-medium text-green-800">
              Song generated successfully! 🎵
            </p>
            <p className="text-sm text-green-700 mt-1">
              Your AI-generated song is ready to play.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-2">
        🎤 Generate AI Song
      </h3>
      <p className="text-gray-600 mb-4">
        Transform your lyrics into a beautiful AI-generated song using our advanced text-to-speech technology.
      </p>
      
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}
      
      <button
        onClick={generateSong}
        disabled={disabled || isGenerating || !lyrics.trim()}
        className={`px-6 py-3 rounded-lg font-medium text-white transition-colors ${
          isGenerating || disabled || !lyrics.trim()
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-purple-600 hover:bg-purple-700 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2'
        }`}
      >
        {isGenerating ? (
          <div className="flex items-center">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Generating Song...
          </div>
        ) : (
          '🎵 Generate Song'
        )}
      </button>
      
      {!lyrics.trim() && (
        <p className="text-sm text-gray-500 mt-2">
          Add lyrics to generate your song
        </p>
      )}
    </div>
  );
};

export default GenerateSong;
