import React from "react";

export type Section = {
  name: string;
  startBeat: number;
  lengthBeats: number;
  color?: string;
};

export function SectionRail({
  sections,
  zoom,
}: {
  sections: Section[];
  zoom: number; // px per beat
}) {
  return (
    <div className="relative w-full h-6 bg-slate-800 rounded">
      {sections?.map((s, i) => (
        <div
          key={i}
          className="absolute h-full text-xs text-white/90 flex items-center px-1"
          style={{
            left: `${s.startBeat * zoom}px`,
            width: `${Math.max(1, s.lengthBeats * zoom)}px`,
            background: s.color || "#334155",
            borderRight: "1px solid rgba(255,255,255,0.2)",
          }}
          title={`${s.name}`}
        >
          <span className="truncate">{s.name}</span>
        </div>
      ))}
    </div>
  );
}
