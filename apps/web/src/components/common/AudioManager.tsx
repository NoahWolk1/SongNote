"use client";

import React, { createContext, useContext, useState, useRef } from 'react';

interface AudioManagerContextType {
  currentAudio: HTMLAudioElement | null;
  playAudio: (audioUrl: string) => Promise<void>;
  stopAudio: () => void;
  isPlaying: boolean;
}

const AudioManagerContext = createContext<AudioManagerContextType | undefined>(undefined);

export const useAudioManager = () => {
  const context = useContext(AudioManagerContext);
  if (!context) {
    throw new Error('useAudioManager must be used within an AudioManagerProvider');
  }
  return context;
};

export const AudioManagerProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentAudio, setCurrentAudio] = useState<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const stopAudio = () => {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
      setCurrentAudio(null);
      setIsPlaying(false);
    }
  };

  const playAudio = async (audioUrl: string) => {
    // Stop any currently playing audio
    stopAudio();

    const audio = new Audio(audioUrl);
    setCurrentAudio(audio);
    setIsPlaying(true);

    // Set up event listeners
    audio.addEventListener('ended', () => {
      setCurrentAudio(null);
      setIsPlaying(false);
    });

    audio.addEventListener('error', () => {
      setCurrentAudio(null);
      setIsPlaying(false);
    });

    audio.addEventListener('pause', () => {
      setIsPlaying(false);
    });

    audio.addEventListener('play', () => {
      setIsPlaying(true);
    });

    try {
      await audio.play();
    } catch (error) {
      console.error('Error playing audio:', error);
      setCurrentAudio(null);
      setIsPlaying(false);
      throw error;
    }
  };

  return (
    <AudioManagerContext.Provider value={{ currentAudio, playAudio, stopAudio, isPlaying }}>
      {children}
    </AudioManagerContext.Provider>
  );
};
