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
  orientation = "horizontal",
  totalBeats,
}: {
  sections: Section[];
  zoom: number; // px per beat
  orientation?: "horizontal" | "vertical";
  totalBeats?: number;
}) {
  if (orientation === "vertical") {
    const height = totalBeats && totalBeats > 0 ? totalBeats * zoom : undefined;
    return (
      <div className="relative w-full bg-slate-800 rounded" style={{ height }}>
        {sections?.map((s, i) => (
          <div
            key={i}
            className="absolute w-full text-xs text-white/90 flex items-center px-1"
            style={{
              top: `${s.startBeat * zoom}px`,
              height: `${Math.max(1, s.lengthBeats * zoom)}px`,
              background: s.color || "#334155",
              borderBottom: "1px solid rgba(255,255,255,0.2)",
            }}
            title={`${s.name}`}
          >
            <span
              className="truncate origin-left"
              style={{ writingMode: "vertical-rl", textOrientation: "mixed" }}
            >
              {s.name}
            </span>
          </div>
        ))}
      </div>
    );
  }

  // horizontal default
  return (
    <div className="relative w-full h-9 bg-slate-800 rounded">
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
