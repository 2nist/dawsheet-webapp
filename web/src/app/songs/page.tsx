"use client";
import React from "react";
import Link from "next/link";
import useSWR from "swr";

const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

const fetcher = (url: string) => fetch(url).then((res) => res.json());

export default function SongsPage() {
  const { data: songs, error, isLoading, mutate } = useSWR(`${apiBase}/songs`, fetcher);

  if (isLoading) return <div className="p-6">Loading songs...</div>;
  if (error) return <div className="p-6 text-red-600">Error loading songs</div>;

  return (
    <main className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Songs Library</h1>
        <Link
          href="/import"
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Import Song
        </Link>
      </div>

      {songs && songs.length > 0 ? (
        <div className="grid gap-4">
          {songs.map((song: any) => (
            <SongCard key={song.id} song={song} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">No songs in your library yet</p>
          <Link
            href="/import"
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Import Your First Song
          </Link>
        </div>
      )}
    </main>
  );
}

function SongCard({ song }: { song: any }) {
  const hasRichData = song.metadata?.imported && song.chords?.length > 0;

  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="text-lg font-semibold">{song.title}</h3>
          <p className="text-gray-600">{song.artist}</p>

          {song.album && (
            <p className="text-sm text-gray-500 mt-1">
              {song.album} {song.year && `(${song.year})`}
            </p>
          )}

          {hasRichData && (
            <div className="flex gap-4 mt-2 text-xs text-gray-500">
              {song.chords?.length > 0 && (
                <span>🎵 {song.chords.length} chords</span>
              )}
              {song.structure?.length > 0 && (
                <span>📋 {song.structure.length} sections</span>
              )}
              {song.lyrics?.verses?.length > 0 && (
                <span>🎤 {song.lyrics.verses.length} verses</span>
              )}
              {song.duration && (
                <span>⏱️ {Math.floor(song.duration / 60)}:{(song.duration % 60).toString().padStart(2, '0')}</span>
              )}
            </div>
          )}

          {song.metadata?.imported && (
            <div className="mt-2">
              <span className="inline-block px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
                Imported ({song.metadata.format})
              </span>
            </div>
          )}
        </div>

        <div className="flex gap-2 ml-4">
          {hasRichData ? (
            <Link
              href={`/songs/${song.id}/timeline`}
              className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
            >
              Timeline
            </Link>
          ) : (
            <Link
              href={`/songs/${song.id}`}
              className="px-3 py-1 bg-gray-600 text-white text-sm rounded hover:bg-gray-700"
            >
              View
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}
