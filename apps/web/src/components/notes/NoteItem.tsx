"use client";

import type { Id } from "@packages/backend/convex/_generated/dataModel";
import Link from "next/link";
import { useState, useEffect, useRef } from "react";
import DeleteNote from "../songs/DeleteSong";
import { useAudioManager } from "../common/AudioManager";

interface NoteItemProps {
  note: {
    _id: Id<"songs">;
    title: string;
    lyrics: string;
    _creationTime: number;
    voiceStyle?: string;
    mood?: string;
    isHummingBased?: boolean;
    generatedSongUrl?: string;
  };
  deleteNote: (args: { songId: Id<"songs"> }) => void;
}

const NoteItem = ({ note, deleteNote }: NoteItemProps) => {
  const [isHovered, setIsHovered] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const settingsRef = useRef<HTMLDivElement>(null);
  const { playAudio, stopAudio, isPlaying, currentAudio } = useAudioManager();

  // Check if this note's audio is currently playing
  const isThisAudioPlaying = isPlaying && currentAudio?.src === note.generatedSongUrl;

  // Close settings when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (settingsRef.current && !settingsRef.current.contains(event.target as Node)) {
        setShowSettings(false);
      }
    };

    if (showSettings) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showSettings]);

  const handlePlaySong = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (isThisAudioPlaying) {
      stopAudio();
    } else if (note.generatedSongUrl) {
      try {
        await playAudio(note.generatedSongUrl);
      } catch (error) {
        console.error('Failed to play song:', error);
      }
    }
  };

  return (
    <div 
      className="flex justify-between items-center h-[74px] bg-[#F9FAFB] py-5 px-5 sm:px-11 gap-x-5 sm:gap-x-10 relative group"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <Link href={`/notes/${note._id}`} className="flex-1">
        <h1 className=" text-[#2D2D2D] text-[17px] sm:text-2xl not-italic font-normal leading-[114.3%] tracking-[-0.6px]">
          {note.title}
        </h1>
        <p className="text-[#666] text-sm mt-1 truncate">
          {note.lyrics.slice(0, 100)}...
        </p>
      </Link>

      {/* Play button - shows on hover if song exists */}
      {isHovered && note.generatedSongUrl && (
        <button
          onClick={handlePlaySong}
          className={`absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 ${
            isThisAudioPlaying ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'
          } text-white rounded-full w-12 h-12 flex items-center justify-center shadow-lg transition-all duration-200 z-10`}
        >
          {isThisAudioPlaying ? (
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
              <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 7.5A2.25 2.25 0 017.5 5.25h9a2.25 2.25 0 012.25 2.25v9a2.25 2.25 0 01-2.25 2.25h-9a2.25 2.25 0 01-2.25-2.25v-9z" />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
              <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.348a1.125 1.125 0 01-1.667-.986V5.653z" />
            </svg>
          )}
        </button>
      )}

      <div className="hidden md:flex flex-col items-end">
        <p className="text-[#2D2D2D] text-center text-xl not-italic font-extralight leading-[114.3%] tracking-[-0.5px]">
          {new Date(Number(note._creationTime)).toLocaleDateString()}
        </p>
        {note.voiceStyle && (
          <p className="text-[#888] text-sm">
            {note.voiceStyle} voice
          </p>
        )}
        {note.generatedSongUrl && (
          <p className="text-[#10b981] text-xs font-medium">
            ♪ Song Ready (URL: {note.generatedSongUrl.substring(0, 50)}...)
          </p>
        )}
      </div>

      {/* Settings Menu (3 dots) */}
      <div className="relative" ref={settingsRef}>
        <button
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setShowSettings(!showSettings);
          }}
          className="text-gray-400 hover:text-gray-600 p-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.75a.75.75 0 110-1.5.75.75 0 010 1.5zM12 12.75a.75.75 0 110-1.5.75.75 0 010 1.5zM12 18.75a.75.75 0 110-1.5.75.75 0 010 1.5z" />
          </svg>
        </button>

        {showSettings && (
          <div className="absolute right-0 top-full mt-1 w-32 bg-white rounded-lg shadow-lg border z-20">
            <Link 
              href={`/notes/${note._id}`}
              className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-t-lg"
              onClick={() => setShowSettings(false)}
            >
              Edit Lyrics
            </Link>
            <button
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                setShowSettings(false);
                window.location.href = `/notes/${note._id}?action=generate`;
              }}
              className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
            >
              Generate Song
            </button>
            <button
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                setShowSettings(false);
                deleteNote({ songId: note._id });
              }}
              className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-b-lg"
            >
              Delete
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default NoteItem;
