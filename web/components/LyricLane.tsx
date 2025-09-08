import React from "react";

export type LyricLine = {
  text: string;
  ts_sec?: number | null;
  beat?: number | null;
};

export function LyricLane({
  lyrics,
  zoom,
  beatsPerBar,
  totalBeats,
  orientation = "horizontal",
  editable = false,
  onChange,
}: {
  lyrics: LyricLine[];
  zoom: number;
  beatsPerBar?: number;
  totalBeats?: number;
  orientation?: "horizontal" | "vertical";
  editable?: boolean;
  onChange?: (next: LyricLine[]) => void;
}) {
  if (orientation === "vertical") {
    const height = totalBeats && totalBeats > 0 ? totalBeats * zoom : undefined;
    const bars =
      beatsPerBar && totalBeats ? Math.ceil(totalBeats / beatsPerBar) : 0;
    const containerRef = React.useRef<HTMLDivElement | null>(null);
    const handleDrag = (
      idx: number,
      clientY: number,
      container: HTMLDivElement | null
    ) => {
      if (!editable || !container) return;
      const rect = container.getBoundingClientRect();
      const y = clientY - rect.top;
      const beat = Math.max(0, y / zoom);
      const snap = 1; // quarter-note snap grid
      const snapped = Math.round(beat / snap) * snap;
      const next = lyrics.slice();
      next[idx] = { ...(next[idx] || {}), beat: snapped };
      onChange?.(next);
    };
    return (
      <div
        className="relative w-full min-h-[48px] bg-slate-900 rounded border border-slate-700 overflow-hidden"
        style={{ height }}
        ref={containerRef}
      >
        {lyrics?.map((l, i) => {
          const top = typeof l.beat === "number" ? l.beat * zoom : i * 24 + 8;
          return (
            <div
              key={`ly-${i}`}
              className={`absolute left-2 text-xs px-2 py-0.5 rounded bg-emerald-800/60 text-emerald-100 whitespace-nowrap border border-emerald-500/30 shadow ${
                editable ? "cursor-ns-resize select-none" : ""
              }`}
              style={{ top, transform: "translateY(-50%)" }}
              title={
                typeof l.ts_sec === "number"
                  ? `${l.ts_sec.toFixed(2)}s`
                  : undefined
              }
              onMouseDown={(e) => {
                if (!editable) return;
                e.preventDefault();
                const move = (ev: MouseEvent) =>
                  handleDrag(i, ev.clientY, containerRef.current);
                const up = () => {
                  window.removeEventListener("mousemove", move);
                  window.removeEventListener("mouseup", up);
                };
                window.addEventListener("mousemove", move);
                window.addEventListener("mouseup", up);
              }}
            >
              {l.text}
            </div>
          );
        })}
        {beatsPerBar && totalBeats
          ? Array.from({ length: bars + 1 }).map((_, i) => (
              <div
                key={`vgrid-bar-${i}`}
                className="absolute left-0 right-0 h-px bg-slate-700/50"
                style={{ top: `${i * beatsPerBar * zoom}px` }}
              />
            ))
          : null}
      </div>
    );
  }

  // horizontal default
  const width = totalBeats && totalBeats > 0 ? totalBeats * zoom : undefined;
  const bars =
    beatsPerBar && totalBeats ? Math.ceil(totalBeats / beatsPerBar) : 0;
  return (
    <div
      className="relative w-full min-h-[48px] bg-slate-900 rounded border border-slate-700 overflow-hidden"
      style={{ width }}
    >
      {lyrics?.map((l, i) => {
        const left = typeof l.beat === "number" ? l.beat * zoom : i * 120;
        return (
          <div
            key={`ly-${i}`}
            className="absolute top-1/2 -translate-y-1/2 text-xs px-2 py-0.5 rounded bg-emerald-800/60 text-emerald-100 whitespace-nowrap border border-emerald-500/30 shadow"
            style={{ left }}
            title={
              typeof l.ts_sec === "number"
                ? `${l.ts_sec.toFixed(2)}s`
                : undefined
            }
          >
            {l.text}
          </div>
        );
      })}
      {beatsPerBar && totalBeats
        ? Array.from({ length: bars + 1 }).map((_, i) => (
            <div
              key={`grid-bar-${i}`}
              className="absolute top-0 bottom-0 w-px bg-slate-700/50"
              style={{ left: `${i * beatsPerBar * zoom}px` }}
            />
          ))
        : null}
    </div>
  );
}
