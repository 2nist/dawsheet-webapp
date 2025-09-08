"use client";
import React from "react";
import { useTimelineStore, beatPx } from "@/lib/timelineStore";

export function ChordsLane() {
  const { chords, zoom } = useTimelineStore((s) => ({
    chords: s.chords,
    zoom: s.zoom,
  }));
  const width = chords.length
    ? Math.max(
        ...chords.map((c) => (c.startBeat + (c.lengthBeats ?? 4)) * zoom)
      )
    : undefined;
  return (
    <div
      className="relative w-full min-h-[44px] bg-slate-900 rounded border border-slate-700 overflow-hidden"
      style={{ width }}
    >
      {chords.map((c) => (
        <div
          key={c.id}
          className="absolute top-1/2 -translate-y-1/2 text-xs px-2 py-0.5 rounded bg-sky-800/60 text-sky-100 whitespace-nowrap border border-sky-500/30 shadow"
          style={{ left: beatPx(c.startBeat, zoom) }}
          title={`Beat ${c.startBeat}${
            c.lengthBeats ? ` • len ${c.lengthBeats}` : ""
          }`}
        >
          {c.symbol}
        </div>
      ))}
    </div>
  );
}
