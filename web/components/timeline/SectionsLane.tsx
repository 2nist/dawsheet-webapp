import React from "react";
import { Section, useTimelineStore, beatPx } from "@/lib/timelineStore";

export function SectionsLane() {
  const { sections, zoom, select, selection } = useTimelineStore((s) => ({
    sections: s.sections,
    zoom: s.zoom,
    select: s.select,
    selection: s.selection,
  }));
  return (
    <div className="relative h-8 bg-slate-800/80 border border-border rounded">
      {sections.map((s: Section) => (
        <div
          key={s.id}
          className={`absolute h-full px-2 flex items-center text-xs border-r border-border ${
            selection.kind === "section" && selection.id === s.id
              ? "bg-primary/30"
              : "bg-slate-700/60"
          }`}
          style={{
            left: beatPx(s.startBeat, zoom),
            width: beatPx(s.lengthBeats, zoom),
          }}
          onClick={() => select("section", s.id)}
          title={`${s.name}`}
        >
          <span className="truncate">{s.name}</span>
        </div>
      ))}
    </div>
  );
}
