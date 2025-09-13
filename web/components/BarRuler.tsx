import React from "react";

export function BarRuler({
  beatsPerBar,
  totalBeats,
  zoom,
  orientation = "horizontal",
}: {
  beatsPerBar: number;
  totalBeats: number;
  zoom: number; // px per beat
  orientation?: "horizontal" | "vertical";
}) {
  const bars = Math.max(0, Math.ceil(totalBeats / Math.max(1, beatsPerBar)));

  if (orientation === "vertical") {
    const totalHeight = Math.max(0, totalBeats) * zoom;
    return (
      <div
        className="relative w-12 bg-slate-800/60 rounded border border-slate-700 overflow-hidden"
        style={{ height: totalHeight ? `${totalHeight}px` : undefined }}
      >
        {/* baseline */}
        <div className="absolute left-1/2 -translate-x-1/2 top-0 bottom-0 w-px bg-slate-600/50" />
        {Array.from({ length: bars + 1 }).map((_, barIdx) => {
          const top = barIdx * beatsPerBar * zoom;
          const label = barIdx + 1;
          return (
            <div key={`vbar-${barIdx}`}>
              <div
                className="absolute left-0 right-0 h-px bg-slate-400"
                style={{ top: `${top}px` }}
              />
              <div
                className="absolute text-[10px] text-slate-200/90 px-1"
                style={{ top: `${top + 2}px`, left: 2 }}
              >
                {label}
              </div>
              {/* beat ticks */}
              {Array.from({ length: Math.max(0, beatsPerBar - 1) }).map(
                (__, b) => (
                  <div
                    key={`vbeat-${barIdx}-${b}`}
                    className="absolute left-0 right-0 h-px bg-slate-600/50"
                    style={{
                      top: `${(barIdx * beatsPerBar + (b + 1)) * zoom}px`,
                    }}
                  />
                )
              )}
            </div>
          );
        })}
      </div>
    );
  }

  // horizontal (default)
  const totalWidth = Math.max(0, totalBeats) * zoom;
  return (
    <div
      className="relative h-12 bg-slate-800/60 rounded border border-slate-700 overflow-hidden"
      style={{ width: totalWidth ? `${totalWidth}px` : undefined }}
    >
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
            {Array.from({ length: Math.max(0, beatsPerBar - 1) }).map(
              (__, b) => (
                <div
                  key={`beat-${barIdx}-${b}`}
                  className="absolute top-0 bottom-0 w-px bg-slate-600/50"
                  style={{
                    left: `${(barIdx * beatsPerBar + (b + 1)) * zoom}px`,
                  }}
                />
              )
            )}
          </div>
        );
      })}
    </div>
  );
}
