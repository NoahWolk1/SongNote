"use client";

import { Dialog, Transition } from "@headlessui/react";
import { api } from "@packages/backend/convex/_generated/api";
import { useMutation, useQuery } from "convex/react";
import Image from "next/image";
import { Fragment, useRef, useState } from "react";

export default function CreateNote() {
  const [open, setOpen] = useState(false);
  const [lyrics, setLyrics] = useState("");

  const cancelButtonRef = useRef(null);

  const createSong = useMutation(api.songs.createSong);
  const openaiKeySet = useQuery(api.openai.openaiKeySet) ?? true;

  const createUserSong = async () => {
    if (!lyrics.trim()) {
      alert("Please write your lyrics first");
      return;
    }

    // Generate a title from the first line of lyrics
    const firstLine = lyrics.split('\n')[0].slice(0, 50);
    const generatedTitle = firstLine.length < lyrics.split('\n')[0].length 
      ? firstLine + "..." 
      : firstLine || "Untitled Song";

    await createSong({
      title: generatedTitle,
      lyrics,
      voiceStyle: "pop", // Default values
      mood: "happy",
      isHummingBased: false,
    });
    setOpen(false);
    setLyrics("");
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
            Write Lyrics
          </span>
        </button>
      </div>

      <Transition.Root show={open} as={Fragment}>
        <Dialog
          as="div"
          className="relative z-10"
          initialFocus={cancelButtonRef}
          onClose={setOpen}
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
                        Write Lyrics
                      </Dialog.Title>
                      <div className="mt-2">
                        <div className="">
                          <label
                            htmlFor="lyrics"
                            className=" text-black text-[17px] sm:text-2xl not-italic font-medium leading-[90.3%] tracking-[-0.6px]"
                          >
                            Your Lyrics
                          </label>
                          <div className="mt-2 pb-[18px]">
                            <textarea
                              id="lyrics"
                              name="lyrics"
                              rows={12}
                              placeholder="Start writing your lyrics here..."
                              className="block w-full rounded-md border-0 py-1.5  border-[#D0D5DD] text-2xl shadow-xs ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600  sm:leading-6 text-black text-[17px] not-italic font-light leading-[90.3%] tracking-[-0.425px] sm:text-2xl"
                              value={lyrics}
                              onChange={(e) => setLyrics(e.target.value)}
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className=" px-4 py-3 mb-5 flex justify-center items-center">
                    <button
                      type="button"
                      className="button text-white text-center text-[17px] sm:text-2xl not-italic font-semibold leading-[90.3%] tracking-[-0.6px] px-[70px] py-2"
                      onClick={createUserSong}
                    >
                      Save Lyrics
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
