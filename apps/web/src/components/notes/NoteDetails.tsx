"use client";

import { api } from "@packages/backend/convex/_generated/api";
import type { Id } from "@packages/backend/convex/_generated/dataModel";
import { useMutation, useQuery } from "convex/react";
import { useState, useEffect } from "react";
import { useAudioManager } from "../common/AudioManager";

interface NoteDetailsProps {
  noteId: Id<"songs">;
}

const NoteDetails = ({ noteId }: NoteDetailsProps) => {
  const [editedLyrics, setEditedLyrics] = useState("");
  const [showSettings, setShowSettings] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const { playAudio, stopAudio } = useAudioManager();
  
  // Song generation settings
  const [voiceStyle, setVoiceStyle] = useState("pop");
  const [mood, setMood] = useState("happy");
  const [includeMusic, setIncludeMusic] = useState(true);
  const [useGeminiTTS, setUseGeminiTTS] = useState(true);
  const [pitch, setPitch] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  // Humming melody features
  const [isRecording, setIsRecording] = useState(false);
  const [recordedMelody, setRecordedMelody] = useState<string | null>(null);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [useHumming, setUseHumming] = useState(false);

  // Track original settings to detect changes
  const [originalSettings, setOriginalSettings] = useState({
    voiceStyle: "pop",
    mood: "happy",
    includeMusic: true,
    useGeminiTTS: true,
    pitch: 0,
    useHumming: false,
    hummingUrl: null as string | null
  });

  const currentSong = useQuery(api.songs.getSong, { id: noteId });
  const updateSong = useMutation(api.songs.updateSong);

  useEffect(() => {
    console.log('Song data updated:', currentSong);
    if (currentSong?.lyrics) {
      setEditedLyrics(currentSong.lyrics);
    }
    if (currentSong?.voiceStyle) {
      setVoiceStyle(currentSong.voiceStyle);
    }
    if (currentSong?.mood) {
      setMood(currentSong.mood);
    }
    if (currentSong?.generatedSongUrl) {
      console.log('Setting audioUrl from database:', currentSong.generatedSongUrl);
      setAudioUrl(currentSong.generatedSongUrl);
    }
    if (currentSong?.hummingAudioUrl) {
      setRecordedMelody(currentSong.hummingAudioUrl);
      // Only set useHumming true if the user previously had it enabled
      // Do not auto-check the box if the user disabled it
    } else {
      setRecordedMelody(null);
      setUseHumming(false);
    }

    // Set original settings when song loads
    if (currentSong) {
      const settings = {
        voiceStyle: currentSong.voiceStyle || "pop",
        mood: currentSong.mood || "happy",
        includeMusic: true,
        useGeminiTTS: true,
        pitch: 0,
        useHumming: !!currentSong.hummingAudioUrl,
        hummingUrl: currentSong.hummingAudioUrl || null
      };
      setOriginalSettings(settings);
    }

    // Check for action query parameter
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('action') === 'generate') {
      setShowSettings(true);
      // Remove the query parameter
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, [currentSong]);

  // Check for changes in lyrics and auto-save
  useEffect(() => {
    const hasLyricsChanges = editedLyrics !== currentSong?.lyrics;
    const hasSettingsChanges = 
      voiceStyle !== originalSettings.voiceStyle ||
      mood !== originalSettings.mood ||
      includeMusic !== originalSettings.includeMusic ||
      useGeminiTTS !== originalSettings.useGeminiTTS ||
      pitch !== originalSettings.pitch ||
      useHumming !== originalSettings.useHumming ||
      recordedMelody !== originalSettings.hummingUrl;
    
    const totalChanges = hasLyricsChanges || hasSettingsChanges;
    setHasChanges(totalChanges);

    if (hasLyricsChanges && editedLyrics.trim() && currentSong) {
      // Auto-save after 2 seconds of no typing
      const timeoutId = setTimeout(() => {
        handleSaveLyrics();
      }, 2000);

      return () => clearTimeout(timeoutId);
    }
  }, [editedLyrics, currentSong?.lyrics, voiceStyle, mood, includeMusic, useGeminiTTS, pitch, useHumming, recordedMelody, originalSettings]);

  const handleSaveLyrics = async () => {
    if (!currentSong) return;
    
    setIsSaving(true);
    try {
      await updateSong({
        id: currentSong._id,
        title: editedLyrics.split('\n')[0].slice(0, 50) || currentSong.title,
        lyrics: editedLyrics,
        voiceStyle,
        mood,
        hummingAudioUrl: recordedMelody || undefined,
      });
      setHasChanges(false);
      
      // Update original settings after save
      setOriginalSettings({
        voiceStyle,
        mood,
        includeMusic,
        useGeminiTTS,
        pitch,
        useHumming,
        hummingUrl: recordedMelody
      });
    } catch (error) {
      console.error('Failed to update lyrics:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const stopCurrentAudio = () => {
    stopAudio();
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: BlobPart[] = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/wav' });
        const url = URL.createObjectURL(blob);
        setRecordedMelody(url);
        
        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
      };

      setMediaRecorder(recorder);
      setIsRecording(true);
      recorder.start();
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Failed to access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      setIsRecording(false);
      setMediaRecorder(null);
    }
  };

  const handleGenerateOrPlay = async () => {
    // Stop any currently playing audio
    stopCurrentAudio();

    // If there are unsaved changes, save them first
    if (hasChanges) {
      await handleSaveLyrics();
    }

    // If song exists and no changes, just play it
    if (audioUrl && !hasChanges) {
      try {
        await playAudio(audioUrl);
      } catch (error) {
        console.error('Error playing audio:', error);
      }
      return;
    }

    // Otherwise, generate a new song
    generateSong();
  };

  const generateSong = async () => {
    if (!currentSong) return;

    // Stop any currently playing audio
    stopCurrentAudio();

    setIsGenerating(true);
    try {
      let ttsEndpoint = 'http://localhost:8002/generate-singing';
      let requestBody: any = {
        lyrics: editedLyrics,
        voice_style: voiceStyle,
        mood,
        include_music: includeMusic,
        vocal_volume: 1.0,
        music_volume: includeMusic ? 0.6 : 0.0
      };

      if (useGeminiTTS) {
        requestBody = {
          ...requestBody,
          tts_engine: 'gemini',
          pitch_adjustment: pitch,
          background_music: includeMusic,
          synthesis_method: 'gemini_tts_with_music'
        };
      } else {
        requestBody.tts_engine = 'edge_tts';
      }

      // Add humming melody if available
      if (useHumming && recordedMelody) {
        requestBody.humming_melody_url = recordedMelody;
        requestBody.match_vocal_to_humming = true;
        console.log('Including humming melody in generation:', recordedMelody);
      } else {
        // If not using humming, clear melody state
        setRecordedMelody(null);
        setUseHumming(false);
      }

      console.log('Generating song with settings:', requestBody);

      const response = await fetch(ttsEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`Failed to generate song: ${response.status}`);
      }

      const contentType = response.headers.get('content-type');
      let generatedAudioUrl: string;

      if (contentType?.includes('application/json')) {
        const responseData = await response.json();
        generatedAudioUrl = responseData.audio_url;
        console.log('Received JSON response with audio_url:', generatedAudioUrl);
      } else {
        const audioBlob = await response.blob();
        generatedAudioUrl = URL.createObjectURL(audioBlob);
        console.log('Generated blob URL:', generatedAudioUrl);
        console.warn('Generated song is a blob URL - this will not persist after page reload');
      }

      console.log('Setting local audioUrl state to:', generatedAudioUrl);
      setAudioUrl(generatedAudioUrl);
      
      // Save the generated audio URL to the database
      console.log('About to save audio URL to database. Current song ID:', currentSong._id);
      console.log('Audio URL to save:', generatedAudioUrl);
      console.log('URL type:', typeof generatedAudioUrl);
      console.log('URL length:', generatedAudioUrl.length);
      
      try {
        const result = await updateSong({
          id: currentSong._id,
          generatedSongUrl: generatedAudioUrl,
        });
        console.log('Successfully saved audio URL to database, result:', result);
        
        // Force a refresh of the current song data
        // The useQuery should automatically update, but we can ensure it happens
      } catch (saveError) {
        console.error('Error saving audio URL to database:', saveError);
        alert('Song generated but failed to save. Please try generating again.');
      }

      // Update original settings since we just generated with current settings
      setOriginalSettings({
        voiceStyle,
        mood,
        includeMusic,
        useGeminiTTS,
        pitch,
        useHumming,
        hummingUrl: recordedMelody
      });

      // Auto-play the song
      try {
        await playAudio(generatedAudioUrl);
      } catch (error) {
        console.error('Error playing generated audio:', error);
      }

    } catch (error) {
      console.error('Error generating song:', error);
      alert('Failed to generate song. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="h-screen flex flex-col">
      {/* Top Bar */}
      <div className="flex justify-between items-center p-6 border-b border-gray-200 bg-white">
        <div className="flex items-center gap-4">
          {/* Back Button */}
          <button
            onClick={() => window.history.back()}
            className="text-gray-600 hover:text-gray-800"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
            </svg>
          </button>
          
          {/* Generate/Play Button */}
          <button
            onClick={handleGenerateOrPlay}
            disabled={isGenerating}
            className={`px-6 py-2 rounded-lg font-medium transition-colors ${
              audioUrl && !hasChanges
                ? 'bg-green-600 hover:bg-green-700 text-white'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            } disabled:bg-gray-400`}
          >
            {isGenerating ? (
              "🎵 Generating..."
            ) : audioUrl && !hasChanges ? (
              "▶️ Play Song"
            ) : (
              "🎵 Generate Song"
            )}
          </button>

          {hasChanges && (
            <span className="text-orange-600 text-sm font-medium">
              {isSaving ? "💾 Saving..." : "• Unsaved changes"}
            </span>
          )}
        </div>

        {/* Settings Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>

          {/* Settings Dropdown Panel */}
          {showSettings && (
            <div className="absolute right-0 top-full mt-2 w-80 bg-white rounded-lg shadow-lg border z-20 p-6">
              <h4 className="text-lg font-semibold mb-4 text-gray-800">Song Settings</h4>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Musical Style</label>
                  <select
                    value={voiceStyle}
                    onChange={(e) => setVoiceStyle(e.target.value)}
                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  >
                    <option value="pop">Pop</option>
                    <option value="ballad">Ballad</option>
                    <option value="jazz">Jazz</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Mood</label>
                  <select
                    value={mood}
                    onChange={(e) => setMood(e.target.value)}
                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  >
                    <option value="happy">Happy</option>
                    <option value="sad">Sad</option>
                    <option value="energetic">Energetic</option>
                  </select>
                </div>

                <div className="space-y-3">
                  <label className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      checked={useGeminiTTS}
                      onChange={(e) => setUseGeminiTTS(e.target.checked)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="text-sm font-medium text-gray-700">Use Gemini TTS for enhanced vocals</span>
                  </label>
                  
                  {useGeminiTTS && (
                    <div className="ml-7">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Voice Pitch: {pitch > 0 ? `+${pitch}` : pitch}
                      </label>
                      <input
                        type="range"
                        min="-12"
                        max="12"
                        step="1"
                        value={pitch}
                        onChange={(e) => setPitch(parseInt(e.target.value))}
                        className="w-full"
                      />
                    </div>
                  )}
                  
                  <label className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      checked={includeMusic}
                      onChange={(e) => setIncludeMusic(e.target.checked)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="text-sm font-medium text-gray-700">Include instrumental accompaniment</span>
                  </label>
                  
                  <div className="border-t pt-3">
                    <label className="flex items-center space-x-3 mb-3">
                      <input
                        type="checkbox"
                        checked={useHumming}
                        onChange={(e) => setUseHumming(e.target.checked)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span className="text-sm font-medium text-gray-700">Match vocal melody to humming</span>
                    </label>
                    
                    {useHumming && (
                      <div className="ml-7 space-y-3">
                        {!recordedMelody ? (
                          <div>
                            <button
                              onClick={isRecording ? stopRecording : startRecording}
                              disabled={isGenerating}
                              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                                isRecording 
                                  ? 'bg-red-100 hover:bg-red-200 text-red-800 border border-red-300'
                                  : 'bg-blue-100 hover:bg-blue-200 text-blue-800 border border-blue-300'
                              }`}
                            >
                              {isRecording ? '🔴 Stop Recording' : '🎤 Record Melody'}
                            </button>
                            <p className="text-xs text-gray-500 mt-1">
                              Hum a melody that matches your lyrics
                            </p>
                          </div>
                        ) : (
                          <div className="space-y-2">
                            <p className="text-sm text-green-600">✓ Melody recorded</p>
                            <div className="flex space-x-2">
                              <button
                                onClick={() => {
                                  if (recordedMelody) {
                                    const audio = new Audio(recordedMelody);
                                    audio.play();
                                  }
                                }}
                                className="px-3 py-1 text-xs bg-green-100 hover:bg-green-200 text-green-800 rounded border border-green-300"
                              >
                                ▶️ Play
                              </button>
                              <button
                                onClick={() => {
                                  setRecordedMelody(null);
                                  setUseHumming(false);
                                }}
                                className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 text-gray-800 rounded border border-gray-300"
                              >
                                🗑️ Delete
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <button
                onClick={() => setShowSettings(false)}
                className="mt-4 w-full bg-gray-100 hover:bg-gray-200 text-gray-800 px-4 py-2 rounded-lg"
              >
                Close Settings
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Main Content - Full Page Lyrics Editor */}
      <div className="flex-1 p-6">
        <textarea
          value={editedLyrics}
          onChange={(e) => setEditedLyrics(e.target.value)}
          placeholder="Start writing your lyrics here..."
          className="w-full h-full text-xl leading-relaxed border-none outline-none resize-none font-light tracking-wide"
          style={{ 
            fontSize: '24px',
            lineHeight: '1.6',
            fontFamily: 'Inter, system-ui, sans-serif'
          }}
        />
      </div>

      {/* Audio Player - Fixed at bottom when song exists */}
      {audioUrl && (
        <div className="border-t border-gray-200 bg-white p-4">
          <audio 
            controls 
            className="w-full" 
            key={audioUrl}
            onPlay={stopCurrentAudio}
          >
            <source src={audioUrl} type="audio/mpeg" />
            Your browser does not support the audio element.
          </audio>
        </div>
      )}
    </div>
  );
};

export default NoteDetails;
