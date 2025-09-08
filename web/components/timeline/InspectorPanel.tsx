"use client";
import React from "react";
import { useTimelineStore } from "@/lib/timelineStore";

export function InspectorPanel() {
  const { selection, sections, chords, lyrics, zoom, setZoom, snap, setSnap } =
    useTimelineStore((s) => ({
      selection: s.selection,
      sections: s.sections,
      chords: s.chords,
      lyrics: s.lyrics,
      zoom: s.zoom,
      setZoom: s.setZoom,
      snap: s.snap,
      setSnap: s.setSnap,
    }));

  const sel = React.useMemo(() => {
    if (!selection.kind || !selection.id) return null;
    const map: any = {
      section: sections.find((x) => x.id === selection.id),
      chord: chords.find((x) => x.id === selection.id),
      lyric: lyrics.find((x) => x.id === selection.id),
    };
    return map[selection.kind] || null;
  }, [selection, sections, chords, lyrics]);

  return (
    <div className="sticky top-4 space-y-3">
      <div className="rounded border border-border bg-slate-900/70 p-3">
        <div className="font-medium text-sm mb-2">Controls</div>
        <div className="space-y-2 text-xs">
          <div className="flex items-center gap-2">
            <label className="w-16">Zoom</label>
            <input
              type="range"
              min={4}
              max={48}
              step={1}
              value={zoom}
              onChange={(e) => setZoom(Number(e.target.value))}
            />
            <span className="tabular-nums w-8 text-right">{zoom}</span>
          </div>
          <div className="flex items-center gap-2">
            <label className="w-16">Snap</label>
            <select
              className="bg-slate-800 border border-slate-700 rounded px-2 py-1"
              value={snap}
              onChange={(e) => setSnap(Number(e.target.value))}
            >
              {[0.25, 0.5, 1, 2, 4].map((v) => (
                <option key={v} value={v}>
                  {v} beat{v !== 1 ? "s" : ""}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="rounded border border-border bg-slate-900/70 p-3">
        <div className="font-medium text-sm mb-2">Selection</div>
        {!selection.kind && <div className="text-xs text-slate-500">Nothing selected</div>}
        {selection.kind && (
          <div className="text-xs space-y-1">
            <div>
              <span className="text-slate-400">Type:</span> {selection.kind}
            </div>
            {sel && (
              <pre className="bg-slate-800/70 border border-slate-700 rounded p-2 text-[10px] overflow-x-auto">
                {JSON.stringify(sel, null, 2)}
              </pre>
            )}
          </div>
        )}
      </div>

      <div className="rounded border border-border bg-slate-900/70 p-3">
        <div className="font-medium text-sm mb-2">Transport</div>
        <div className="flex items-center gap-2 text-xs">
          <button className="px-2 py-1 rounded border border-slate-600">Play</button>
          <button className="px-2 py-1 rounded border border-slate-600">Stop</button>
          <button className="px-2 py-1 rounded border border-slate-600">Loop</button>
        </div>
      </div>
    </div>
  );
}
