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
  orientation = "horizontal",
  editable = false,
  onChange,
}: {
  chords: Chord[];
  zoom: number;
  beatsPerBar?: number;
  totalBeats?: number;
  orientation?: "horizontal" | "vertical";
  editable?: boolean;
  onChange?: (next: Chord[]) => void;
}) {
  if (orientation === "vertical") {
    const height = totalBeats && totalBeats > 0 ? totalBeats * zoom : undefined;
    const bars =
      beatsPerBar && totalBeats ? Math.ceil(totalBeats / beatsPerBar) : 0;
    const handleDrag = (
      idx: number,
      clientY: number,
      container: HTMLDivElement | null
    ) => {
      if (!editable || !container) return;
      const rect = container.getBoundingClientRect();
      const y = clientY - rect.top;
      const beat = Math.max(0, y / zoom);
      const snap = 1; // snap to quarter-note; can be made configurable
      const snapped = Math.round(beat / snap) * snap;
      const next = chords.slice();
      next[idx] = { ...next[idx], startBeat: snapped };
      onChange?.(next);
    };
    const containerRef = React.useRef<HTMLDivElement | null>(null);
    return (
      <div
        className="relative w-full min-h-[48px] bg-slate-900 rounded border border-slate-700 overflow-hidden"
        style={{ height }}
        ref={containerRef}
      >
        {chords?.map((c, i) => (
          <div
            key={`${c.symbol}-${i}`}
            className={`absolute left-2 text-xs px-2 py-0.5 rounded bg-sky-700 text-white whitespace-nowrap border border-sky-400/30 shadow ${
              editable ? "cursor-ns-resize select-none" : ""
            }`}
            style={{
              top: `${c.startBeat * zoom}px`,
              transform: "translateY(-50%)",
            }}
            title={`Beat ${c.startBeat}`}
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
            {c.symbol}
          </div>
        ))}
        {beatsPerBar && totalBeats
          ? Array.from({ length: bars + 1 }).map((_, i) => (
              <div
                key={`vgrid-bar-${i}`}
                className="absolute left-0 right-0 h-px bg-slate-700/70"
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
