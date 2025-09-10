"use client";
import React from "react";
import { useTimelineStore } from "@/lib/timelineStore";

export function BarRuler({
  totalBeats,
  beatsPerBar = 4,
}: {
  totalBeats: number;
  beatsPerBar?: number;
}) {
  const { zoom } = useTimelineStore((s) => ({ zoom: s.zoom }));
  const widthPx = Math.max(1, Math.round(totalBeats * zoom));
  const bars = Math.ceil(totalBeats / beatsPerBar);
  const ticks: Array<{ left: number; strong: boolean; label?: string }> = [];
  for (let b = 0; b <= bars * beatsPerBar; b++) {
    const left = Math.round(b * zoom);
    const strong = b % beatsPerBar === 0;
    const label = strong ? String(Math.floor(b / beatsPerBar) + 1) : undefined;
    ticks.push({ left, strong, label });
  }
  return (
    <div className="relative h-6 bg-slate-900/70 border border-border rounded">
      <div className="relative h-full" style={{ width: widthPx }}>
        {ticks.map((t, i) => (
          <div
            key={i}
            className="absolute top-0 bottom-0"
            style={{ left: t.left }}
          >
            <div
              className={
                t.strong
                  ? "h-full w-px bg-slate-500/60"
                  : "h-full w-px bg-slate-600/30"
              }
            />
            {t.label && (
              <div className="absolute -top-5 text-[10px] text-slate-300 select-none">
                {t.label}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
