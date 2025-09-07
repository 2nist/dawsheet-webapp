import React from "react";

export type Chord = {
  symbol: string;
  startBeat: number;
};

export function ChordLane({
  chords,
  zoom,
  beatsPerBar,
  totalBeats,
}: {
  chords: Chord[];
  zoom: number;
  beatsPerBar?: number;
  totalBeats?: number;
}) {
  const width = totalBeats && totalBeats > 0 ? totalBeats * zoom : undefined;
  const bars = beatsPerBar && totalBeats ? Math.ceil(totalBeats / beatsPerBar) : 0;
  return (
    <div
      className="relative w-full h-10 bg-slate-900 rounded border border-slate-700 overflow-hidden"
      style={{ width }}
    >
      {chords?.map((c, i) => (
        <div
          key={`${c.symbol}-${i}`}
          className="absolute -translate-x-1/2 top-1/2 -translate-y-1/2 text-xs px-2 py-0.5 rounded bg-sky-700 text-white whitespace-nowrap border border-sky-400/30 shadow"
          style={{ left: `${c.startBeat * zoom}px` }}
          title={`Beat ${c.startBeat}`}
        >
          {c.symbol}
        </div>
      ))}
      {/* bar grid lines if beatsPerBar provided */}
      {beatsPerBar && totalBeats
        ? Array.from({ length: bars + 1 }).map((_, i) => (
            <div
              key={`grid-bar-${i}`}
              className="absolute top-0 bottom-0 w-px bg-slate-700/70"
              style={{ left: `${i * beatsPerBar * zoom}px` }}
            />
          ))
        : null}
    </div>
  );
}
