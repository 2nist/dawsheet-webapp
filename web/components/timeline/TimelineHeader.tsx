"use client";
import React from "react";
import { SectionsLane } from "@/components/timeline/SectionsLane";
import { BarRuler } from "@/components/timeline/BarRuler";
import { useTimelineStore } from "@/lib/timelineStore";

export function TimelineHeader({
  meta,
}: {
  meta?: { title?: string; artist?: string; timeSignature?: string; bpm?: number } | null;
}) {
  const { sections, zoom, setZoom } = useTimelineStore((s) => ({
    sections: s.sections,
    zoom: s.zoom,
    setZoom: s.setZoom,
  }));

  const totalBeats = React.useMemo(() => {
    if (!sections.length) return 32;
    const last = sections[sections.length - 1];
    return last.startBeat + last.lengthBeats + 4; // pad a bar
  }, [sections]);

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-semibold">{meta?.title || "Timeline"}</h1>
        <span className="text-xs text-muted-foreground">
          {meta?.artist ? `— ${meta.artist}` : ""}
        </span>
        {meta?.timeSignature && (
          <span className="text-xs text-muted-foreground">
            {meta.timeSignature}
            {typeof meta?.bpm === "number" ? ` • ${meta.bpm} bpm` : ""}
          </span>
        )}
        <div className="ml-auto flex items-center gap-2">
          <label className="text-xs">Zoom</label>
          <input
            type="range"
            min={4}
            max={48}
            step={1}
            value={zoom}
            onChange={(e) => setZoom(Number(e.target.value))}
          />
        </div>
      </div>
      <div className="space-y-1 overflow-x-auto">
        <SectionsLane />
        <BarRuler totalBeats={totalBeats} beatsPerBar={4} />
      </div>
    </div>
  );
}
