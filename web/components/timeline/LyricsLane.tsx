import React, { useMemo } from "react";
import {
  useTimelineStore,
  wrapLyricsRows,
  beatPx,
  textPxWidth,
} from "@/lib/timelineStore";

export function LyricsLane() {
  const { lyrics, sections, zoom, snap, updateItem, select, selection } =
    useTimelineStore((s) => ({
      lyrics: s.lyrics,
      sections: s.sections,
      zoom: s.zoom,
      snap: s.snap,
      updateItem: s.updateItem,
      select: s.select,
      selection: s.selection,
    }));
  const placement = useMemo(
    () => wrapLyricsRows(lyrics, sections, zoom),
    [lyrics, sections, zoom]
  );
  const sectionByBeat = (beat: number) =>
    sections.find(
      (sec) => beat >= sec.startBeat && beat < sec.startBeat + sec.lengthBeats
    );

  const onDrag = (
    id: string,
    clientX: number,
    container: HTMLDivElement | null
  ) => {
    if (!container) return;
    const rect = container.getBoundingClientRect();
    const x = clientX - rect.left;
    let beat = x / zoom;
    const res = snap;
    beat = Math.round(beat / res) * res;
    updateItem("lyric", id, { beat });
  };

  const containerRef = React.useRef<HTMLDivElement | null>(null);

  return (
    <div
      ref={containerRef}
      className="relative h-16 bg-slate-900/80 border border-border rounded overflow-hidden"
    >
      {lyrics.map((l) => {
        const sec = sectionByBeat(l.beat);
        const row =
          placement[sec?.id || ""]?.find((r) => r.id === l.id)?.row ??
          l.row ??
          0;
        const top = 6 + row * 22;
        return (
          <div
            key={l.id}
            className={`absolute text-xs px-2 py-0.5 rounded bg-emerald-800/70 text-emerald-50 border border-emerald-500/30 whitespace-nowrap ${
              selection.kind === "lyric" && selection.id === l.id
                ? "ring-2 ring-primary"
                : ""
            }`}
            style={{ left: beatPx(l.beat, zoom), top }}
            onClick={() => select("lyric", l.id)}
            onDoubleClick={() => select("lyric", l.id)}
            onMouseDown={(e) => {
              if ((e.target as HTMLElement).closest("input,textarea")) return;
              e.preventDefault();
              const move = (ev: MouseEvent) =>
                onDrag(l.id, ev.clientX, containerRef.current);
              const up = () => {
                window.removeEventListener("mousemove", move);
                window.removeEventListener("mouseup", up);
              };
              window.addEventListener("mousemove", move);
              window.addEventListener("mouseup", up);
            }}
            title={`beat ${l.beat}`}
          >
            {l.text}
          </div>
        );
      })}
    </div>
  );
}
