"use client";

import { Dialog, Transition } from "@headlessui/react";
import { api } from "@packages/backend/convex/_generated/api";
import { useMutation, useQuery } from "convex/react";
import Image from "next/image";
import { Fragment, useRef, useState } from "react";

export default function CreateSong() {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [lyrics, setLyrics] = useState("");
  const [voiceStyle, setVoiceStyle] = useState("pop");
  const [mood, setMood] = useState("happy");
  const [includeMusic, setIncludeMusic] = useState(true);
  const [useGeminiTTS, setUseGeminiTTS] = useState(true);
  const [pitch, setPitch] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const cancelButtonRef = useRef(null);

  const createSong = useMutation(api.songs.createSong);
  const openaiKeySet = useQuery(api.openai.openaiKeySet) ?? true;

  const handleClose = () => {
    if (audioUrl && audioUrl.startsWith('blob:')) {
      URL.revokeObjectURL(audioUrl);
    }
    setAudioUrl(null);
    setOpen(false);
  };

  const createUserSong = async () => {
    if (!title.trim() || !lyrics.trim()) {
      alert("Please fill in both title and lyrics");
      return;
    }

    setIsGenerating(true);
    try {
      // Create the song in the database
      const songId = await createSong({
        title,
        lyrics,
        voiceStyle,
        mood,
        isHummingBased: false,
      });

      // Choose TTS service based on user preference
      let ttsEndpoint = 'http://localhost:8002/generate-singing';
      let requestBody: any = {
        lyrics,
        voice_style: voiceStyle,
        mood,
        include_music: includeMusic,
        vocal_volume: 1.0,  // Vocals at maximum volume
        music_volume: includeMusic ? 0.6 : 0.0  // Music at 60% - balanced mix with prominent vocals
      };

      if (useGeminiTTS) {
        // Use Gemini TTS with enhanced request
        requestBody = {
          ...requestBody,
          tts_engine: 'gemini',
          pitch_adjustment: pitch,
          background_music: includeMusic,
          synthesis_method: 'gemini_tts_with_music'
        };
      } else {
        // Use Edge TTS for clearer vocals
        requestBody.tts_engine = 'edge_tts';
      }

      console.log('Sending TTS request:', requestBody);

      // Generate the singing audio
      const response = await fetch(ttsEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to generate singing audio: ${response.status} - ${errorText}`);
      }

      // Check if response is JSON (new format) or blob (old format)
      const contentType = response.headers.get('content-type');
      let audioUrl: string;

      if (contentType?.includes('application/json')) {
        const responseData = await response.json();
        console.log('Received JSON response:', responseData);
        
        if (!responseData.audio_url) {
          throw new Error('No audio URL in response');
        }
        
        // Use the data URL directly
        audioUrl = responseData.audio_url;
        setAudioUrl(audioUrl);
        console.log('Using audio data URL from service');
      } else {
        // Handle blob response (fallback)
        const audioBlob = await response.blob();
        audioUrl = URL.createObjectURL(audioBlob);
        setAudioUrl(audioUrl);
        console.log('Generated audio blob URL:', audioUrl);
      }

      // Play the generated song
      const audio = new Audio();
      
      // Add comprehensive event listeners
      audio.addEventListener('loadstart', () => {
        console.log('Audio loading started');
      });
      
      audio.addEventListener('canplay', () => {
        console.log('Audio can start playing');
      });
      
      audio.addEventListener('loadedmetadata', () => {
        console.log(`Song metadata loaded - duration: ${audio.duration} seconds`);
      });
      
      audio.addEventListener('ended', () => {
        console.log('Song finished playing');
      });
      
      audio.addEventListener('error', (e: Event) => {
        const audioElement = e.target as HTMLAudioElement;
        const error = audioElement.error;
        console.error('Audio error details:', {
          code: error?.code,
          message: error?.message,
          networkState: audioElement.networkState,
          readyState: audioElement.readyState,
          currentSrc: audioElement.currentSrc
        });
      });
      
      // Set the audio source
      audio.src = audioUrl;

      // Play the song
      try {
        console.log('Attempting to play generated song...');
        
        const playPromise = audio.play();
        
        if (playPromise !== undefined) {
          playPromise
            .then(() => {
              console.log('Song is now playing!');
              alert('🎵 Your song is playing! 🎵 Use the audio controls below to replay it.');
            })
            .catch((playError) => {
              console.error('Auto-play was prevented:', playError);
              alert('🎵 Song generated successfully! Please click the play button below to listen. 🎵');
            });
        }
      } catch (playError) {
        console.error('Error playing audio:', playError);
        alert('🎵 Song generated successfully! Please use the audio controls below to listen. 🎵');
      }

      // TODO: Store the audio data and update the song record
      console.log('Generated audio from TTS service');

      // Don't close the dialog immediately - let the user hear the song
      // setOpen(false);
      setTitle("");
      setLyrics("");
      setVoiceStyle("pop");
      setMood("happy");
      setIncludeMusic(true);
      setPitch(0);
    } catch (error) {
      console.error('Error creating song:', error);
      alert(`Failed to create song: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <>
      <div className="flex justify-center items-center">
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="button text-[#EBECEF] flex gap-4 justify-center items-center text-center px-8 sm:px-16 py-2"
        >
          <Image
            src={"/images/Add.png"}
            width={40}
            height={40}
            alt="search"
            className="float-right sm:w-[40px] sm:h-[40px] w-6 h-6"
          />
          <span className="text-[17px] sm:text-3xl not-italic font-medium leading-[79%] tracking-[-0.75px]">
            {" "}
            New Song
          </span>
        </button>
      </div>

      <Transition.Root show={open} as={Fragment}>
        <Dialog
          as="div"
          className="relative z-10"
          initialFocus={cancelButtonRef}
          onClose={handleClose}
        >
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
          </Transition.Child>

          <form className="fixed inset-0 z-10 w-screen overflow-y-auto">
            <div className="flex min-h-full items-end justify-center p-2 text-center sm:items-center sm:p-0">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300"
                enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                enterTo="opacity-100 translate-y-0 sm:scale-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100 translate-y-0 sm:scale-100"
                leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              >
                <Dialog.Panel className="relative transform overflow-hidden rounded-[10px] bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-[719px]">
                  <div className="bg-white px-4 pb-4 pt-5 sm:p-8 sm:pb-4">
                    <div className="mt-3  sm:mt-0 text-left">
                      <Dialog.Title
                        as="h3"
                        className="text-black text-center text-xl sm:text-left sm:text-[35px] pb-6 sm:pb-8 not-italic font-semibold leading-[90.3%] tracking-[-0.875px]"
                      >
                        Create New Song
                      </Dialog.Title>
                      <div className="mt-2 space-y-3">
                        <div className="pb-2">
                          <label
                            htmlFor="title"
                            className=" text-black text-[17px] sm:text-2xl not-italic font-medium leading-[90.3%] tracking-[-0.6px]"
                          >
                            Song Title
                          </label>
                          <div className="mt-2">
                            <input
                              id="title"
                              name="title"
                              type="text"
                              placeholder="Enter song title"
                              autoComplete="title"
                              value={title}
                              onChange={(e) => setTitle(e.target.value)}
                              className="border shadow-[0px_1px_2px_0px_rgba(16,24,40,0.05)] rounded-lg border-solid border-[#D0D5DD] bg-white w-full py-2.5 px-[14px] text-black text-[17px] not-italic font-light leading-[90.3%] tracking-[-0.425px] sm:text-2xl"
                            />
                          </div>
                        </div>

                        <div className="">
                          <label
                            htmlFor="lyrics"
                            className=" text-black text-[17px] sm:text-2xl not-italic font-medium leading-[90.3%] tracking-[-0.6px]"
                          >
                            Lyrics
                          </label>
                          <div className="mt-2 pb-[18px]">
                            <textarea
                              id="lyrics"
                              name="lyrics"
                              rows={8}
                              placeholder="Enter your song lyrics here..."
                              className="block w-full rounded-md border-0 py-1.5  border-[#D0D5DD] text-2xl shadow-xs ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600  sm:leading-6 text-black text-[17px] not-italic font-light leading-[90.3%] tracking-[-0.425px] sm:text-2xl"
                              value={lyrics}
                              onChange={(e) => setLyrics(e.target.value)}
                            />
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <label
                              htmlFor="voiceStyle"
                              className="text-black text-[17px] sm:text-2xl not-italic font-medium leading-[90.3%] tracking-[-0.6px]"
                            >
                              Musical Style
                            </label>
                            <select
                              id="voiceStyle"
                              value={voiceStyle}
                              onChange={(e) => setVoiceStyle(e.target.value)}
                              className="mt-2 block w-full rounded-md border-0 py-2.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 text-[17px] sm:text-2xl"
                            >
                              <option value="pop">Pop</option>
                              <option value="ballad">Ballad</option>
                              <option value="jazz">Jazz</option>
                            </select>
                          </div>
                          
                          <div>
                            <label
                              htmlFor="mood"
                              className="text-black text-[17px] sm:text-2xl not-italic font-medium leading-[90.3%] tracking-[-0.6px]"
                            >
                              Mood
                            </label>
                            <select
                              id="mood"
                              value={mood}
                              onChange={(e) => setMood(e.target.value)}
                              className="mt-2 block w-full rounded-md border-0 py-2.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 text-[17px] sm:text-2xl"
                            >
                              <option value="happy">Happy</option>
                              <option value="sad">Sad</option>
                              <option value="energetic">Energetic</option>
                            </select>
                          </div>
                        </div>

                        {/* New Gemini TTS Controls */}
                        <div className="pt-4 border-t border-gray-200">
                          <label className="flex items-center space-x-3 mb-4">
                            <input
                              type="checkbox"
                              checked={useGeminiTTS}
                              onChange={(e) => setUseGeminiTTS(e.target.checked)}
                              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                            />
                            <span className="text-black text-[17px] sm:text-2xl not-italic font-medium leading-[90.3%] tracking-[-0.6px]">
                              Use Gemini TTS for enhanced vocals
                            </span>
                          </label>
                          
                          {useGeminiTTS && (
                            <div className="ml-7">
                              <label
                                htmlFor="pitch"
                                className="text-black text-[15px] sm:text-xl not-italic font-medium leading-[90.3%] tracking-[-0.5px]"
                              >
                                Voice Pitch: {pitch > 0 ? `+${pitch}` : pitch}
                              </label>
                              <div className="mt-2">
                                <input
                                  id="pitch"
                                  name="pitch"
                                  type="range"
                                  min="-12"
                                  max="12"
                                  step="1"
                                  value={pitch}
                                  onChange={(e) => setPitch(parseInt(e.target.value))}
                                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                                />
                                <div className="flex justify-between text-xs text-gray-500 mt-1">
                                  <span>Lower</span>
                                  <span>Normal</span>
                                  <span>Higher</span>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>

                        <div className="pt-4">
                          <label className="flex items-center space-x-3">
                            <input
                              type="checkbox"
                              checked={includeMusic}
                              onChange={(e) => setIncludeMusic(e.target.checked)}
                              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                            />
                            <span className="text-black text-[17px] sm:text-2xl not-italic font-medium leading-[90.3%] tracking-[-0.6px]">
                              Include instrumental accompaniment
                            </span>
                          </label>
                        </div>

                        {/* Audio Player */}
                        {audioUrl && (
                          <div className="pt-4 border-t border-gray-200">
                            <label className="text-black text-[17px] sm:text-2xl not-italic font-medium leading-[90.3%] tracking-[-0.6px] block mb-3">
                              Generated Song
                            </label>
                            <audio 
                              controls 
                              src={audioUrl}
                              className="w-full"
                              preload="metadata"
                            >
                              Your browser does not support the audio element.
                            </audio>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className=" px-4 py-3 mb-5 flex justify-center items-center space-x-4">
                    <button
                      type="button"
                      className="border border-gray-300 text-gray-700 text-center text-[17px] sm:text-2xl not-italic font-medium leading-[90.3%] tracking-[-0.6px] px-[30px] py-2 rounded-lg hover:bg-gray-50"
                      onClick={handleClose}
                    >
                      Close
                    </button>
                    <button
                      type="button"
                      className="button text-white text-center text-[17px] sm:text-2xl not-italic font-semibold leading-[90.3%] tracking-[-0.6px] px-[70px] py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                      onClick={createUserSong}
                      disabled={isGenerating}
                    >
                      {isGenerating ? "Generating Song..." : "Create Song"}
                    </button>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </form>
        </Dialog>
      </Transition.Root>
    </>
  );
}
