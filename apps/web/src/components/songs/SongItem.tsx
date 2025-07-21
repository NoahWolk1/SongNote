import type { Id } from "@packages/backend/convex/_generated/dataModel";
import Link from "next/link";
import DeleteNote from "./DeleteSong";

interface SongItemProps {
  song: {
    _id: Id<"songs">;
    title: string;
    lyrics: string;
    _creationTime: number;
    voiceStyle?: string;
    mood?: string;
    isHummingBased?: boolean;
  };
  deleteSong: (args: { songId: Id<"songs"> }) => void;
}

const SongItem = ({ song, deleteSong }: SongItemProps) => {
  return (
    <div className="flex justify-between items-center h-[74px] bg-[#F9FAFB] py-5 px-5 sm:px-11 gap-x-5 sm:gap-x-10">
      <Link href={`/songs/${song._id}`} className="flex-1">
        <h1 className=" text-[#2D2D2D] text-[17px] sm:text-2xl not-italic font-normal leading-[114.3%] tracking-[-0.6px]">
          {song.title}
        </h1>
        <p className="text-[#666] text-sm mt-1 truncate">
          {song.lyrics.slice(0, 100)}...
        </p>
      </Link>
      <div className="hidden md:flex flex-col items-end">
        <p className="text-[#2D2D2D] text-center text-xl not-italic font-extralight leading-[114.3%] tracking-[-0.5px]">
          {new Date(Number(song._creationTime)).toLocaleDateString()}
        </p>
        {song.voiceStyle && (
          <p className="text-[#888] text-sm">
            {song.voiceStyle} • {song.mood}
          </p>
        )}
      </div>
      <DeleteNote deleteAction={() => deleteSong({ songId: song._id })} />
    </div>
  );
};

export default SongItem;
