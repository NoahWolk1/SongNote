"use client";

import { api } from "@packages/backend/convex/_generated/api";
import type { Id } from "@packages/backend/convex/_generated/dataModel";
import { useQuery } from "convex/react";
import { useState } from "react";
import ComplexToggle from "../home/ComplexToggle";
import GenerateSong from "./GenerateSong";

interface NoteDetailsProps {
  noteId: Id<"songs">;
}

const NoteDetails = ({ noteId }: NoteDetailsProps) => {
  const [isSummary, setIsSummary] = useState(false);
  const currentSong = useQuery(api.songs.getSong, { id: noteId });

  return (
    <div className="container space-y-6 sm:space-y-9 py-20 px-[26px] sm:px-0">
      <div className="flex justify-center items-center">
        <ComplexToggle isSummary={isSummary} setIsSummary={setIsSummary} />
      </div>
      <h3 className="text-black text-center pb-5 text-xl sm:text-[32px] not-italic font-semibold leading-[90.3%] tracking-[-0.8px]">
        {currentSong?.title}
      </h3>
      
      {/* Song metadata */}
      <div className="flex justify-center gap-4 mb-6">
        {currentSong?.voiceStyle && (
          <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
            {currentSong.voiceStyle} voice
          </span>
        )}
        {currentSong?.mood && (
          <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
            {currentSong.mood}
          </span>
        )}
        {currentSong?.isHummingBased && (
          <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm">
            Humming-based
          </span>
        )}
      </div>

      {/* Main content */}
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h4 className="text-lg font-semibold mb-4 text-gray-800">
          {!isSummary ? "Lyrics" : "AI Analysis"}
        </h4>
        <div className="text-black text-xl sm:text-[28px] not-italic font-normal leading-[130.3%] tracking-[-0.7px] whitespace-pre-wrap">
          {!isSummary
            ? currentSong?.lyrics
            : "AI analysis and melody extraction coming soon..."}
        </div>
      </div>

      {/* Generated audio section */}
      {currentSong?.generatedSongUrl && (
        <div className="bg-gray-50 rounded-lg p-6">
          <h4 className="text-lg font-semibold mb-4 text-gray-800">Generated Song</h4>
          <audio controls className="w-full">
            <source src={currentSong.generatedSongUrl} type="audio/mpeg" />
            Your browser does not support the audio element.
          </audio>
        </div>
      )}

      {/* AI Song Generation */}
      {currentSong && !currentSong.generatedSongUrl && (
        <GenerateSong 
          songId={currentSong._id}
          lyrics={currentSong.lyrics}
          voiceStyle={currentSong.voiceStyle}
        />
      )}
    </div>
  );
};

export default NoteDetails;
