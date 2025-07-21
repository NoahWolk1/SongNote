"use client";

import { api } from "@packages/backend/convex/_generated/api";
import { useMutation, useQuery } from "convex/react";
import Image from "next/image";
import { useState } from "react";
import CreateSong from "./CreateSong";
import SongItem from "./SongItem";

const Songs = () => {
  const [search, setSearch] = useState("");

  const allSongs = useQuery(api.songs.getSongs);
  const deleteSong = useMutation(api.songs.deleteSong);

  const finalSongs = search
    ? allSongs?.filter(
        (song) =>
          song.title.toLowerCase().includes(search.toLowerCase()) ||
          song.lyrics.toLowerCase().includes(search.toLowerCase())
      )
    : allSongs;

  return (
    <div className="container pb-10">
      <h1 className="text-[#2D2D2D] text-center text-[20px] sm:text-[43px] not-italic font-normal sm:font-medium leading-[114.3%] tracking-[-1.075px] sm:mt-8 my-4  sm:mb-10">
        Your AI-Generated Songs
      </h1>
      <div className="px-5 sm:px-0">
        <div className="bg-white flex items-center h-[39px] sm:h-[55px] rounded-sm border border-solid gap-2 sm:gap-5 mb-10 border-[rgba(0,0,0,0.40)] px-3 sm:px-11">
          <Image
            src={"/images/search.svg"}
            width={23}
            height={22}
            alt="search"
            className="cursor-pointer sm:w-[23px] sm:h-[22px] w-[20px] h-[20px]"
          />
          <input
            type="text"
            placeholder="Search songs or lyrics..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 text-[#2D2D2D] text-[17px] sm:text-2xl not-italic font-light leading-[114.3%] tracking-[-0.6px] focus:outline-0 focus:ring-0 focus:border-0 border-0"
          />
        </div>
      </div>

      {finalSongs && finalSongs.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-gray-500 text-lg mb-6">
            You haven't created any songs yet.
          </div>
          <div className="text-gray-400 text-base mb-8">
            Start by creating your first AI-generated song with lyrics and musical accompaniment.
          </div>
        </div>
      ) : (
        <div className="border-[0.5px] mb-20 divide-y-[0.5px] divide-[#00000096] border-[#00000096]">
          {finalSongs?.map((song) => (
            <SongItem key={song._id} song={song} deleteSong={deleteSong} />
          ))}
        </div>
      )}

      <CreateSong />
    </div>
  );
};

export default Songs;
