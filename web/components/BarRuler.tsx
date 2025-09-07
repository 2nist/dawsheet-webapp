import React from "react";

export function BarRuler({
  beatsPerBar,
  totalBeats,
  zoom,
}: {
  beatsPerBar: number;
  totalBeats: number;
  zoom: number; // px per beat
}) {
  const totalWidth = Math.max(0, totalBeats) * zoom;
  const bars = Math.max(0, Math.ceil(totalBeats / Math.max(1, beatsPerBar)));
  return (
    <div className="relative h-6 bg-slate-800/60 rounded border border-slate-700 overflow-hidden" style={{ width: totalWidth ? `${totalWidth}px` : undefined }}>
      {/* baseline */}
      <div className="absolute left-0 right-0 top-1/2 -translate-y-1/2 h-px bg-slate-600/50" />
      {Array.from({ length: bars + 1 }).map((_, barIdx) => {
        const left = barIdx * beatsPerBar * zoom;
        const label = barIdx + 1;
        return (
          <div key={`bar-${barIdx}`}>
            <div
              className="absolute top-0 bottom-0 w-px bg-slate-400"
              style={{ left: `${left}px` }}
            />
            <div
              className="absolute text-[10px] text-slate-200/90 px-1"
              style={{ left: `${left + 2}px`, top: 1 }}
            >
              {label}
            </div>
            {/* beat ticks */}
            {Array.from({ length: Math.max(0, beatsPerBar - 1) }).map((__, b) => (
              <div
                key={`beat-${barIdx}-${b}`}
                className="absolute top-0 bottom-0 w-px bg-slate-600/50"
                style={{ left: `${(barIdx * beatsPerBar + (b + 1)) * zoom}px` }}
              />
            ))}
          </div>
        );
      })}
    </div>
  );
}
