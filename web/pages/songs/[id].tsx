import React from "react";
import { useRouter } from "next/router";
import useSWR from "swr";
import { swrFetcher } from "@/lib/api";
import { SectionRail } from "@/components/SectionRail";
import { ChordLane } from "@/components/ChordLane";
import { BarRuler } from "@/components/BarRuler";

export default function SongDetailPage() {
  const router = useRouter();
  const { id } = router.query;
  const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
  const [zoom, setZoom] = React.useState(8); // px per beat
  const [grid, setGrid] = React.useState<"off" | "1/4" | "1/8">("1/4");

  const url = React.useMemo(() => {
    if (!id) return null;
    const sid = Array.isArray(id) ? id[0] : id;
    return `${apiBase}/v1/songs/${sid}/doc`;
  }, [id, apiBase]);

  const { data, error, isLoading } = useSWR(url, swrFetcher);

  const doc = data as any;
  const sections = doc?.sections || [];
  const chords = (doc?.chords || []) as { symbol: string; startBeat: number }[];
  const issues: string[] = doc?.issues || [];
  const timeSig: string = doc?.timeSignature || "4/4";
  const beatsPerBar = Number((timeSig?.split("/")[0] || "4")) || 4;

  // visual quantize (no refetch): rounds startBeat in the view
  const gridStep = grid === "off" ? 0 : grid === "1/4" ? 1 : 0.5;
  const qChords = React.useMemo(() => {
    if (!Array.isArray(chords)) return [] as typeof chords;
    if (!gridStep) return chords;
    return chords.map((c) => ({
      ...c,
      startBeat: Math.round(c.startBeat / gridStep) * gridStep,
    }));
  }, [chords, gridStep]);

  const totalBeats = React.useMemo(() => {
    const last = (qChords[qChords.length - 1]?.startBeat ?? 0) + beatsPerBar;
    return Math.max(beatsPerBar, last);
  }, [qChords, beatsPerBar]);

  return (
    <div className="p-4 space-y-4">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">
            {doc?.title || "Song"}{" "}
            <span className="text-slate-500">
              {doc?.artist ? `— ${doc.artist}` : ""}
            </span>
          </h1>
          <p className="text-sm text-slate-500">
            {timeSig} • {doc?.bpm} bpm
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="text-sm">Zoom: {zoom}px/beat</label>
          <input
            type="range"
            min={4}
            max={24}
            step={1}
            value={zoom}
            onChange={(e) => setZoom(parseInt(e.target.value, 10))}
          />
          <select
            className="border rounded px-2 py-1 text-sm bg-slate-900 border-slate-700"
            value={grid}
            onChange={(e) => setGrid(e.target.value as any)}
            title="Quantize preview (visual only)"
          >
            <option value="off">Grid: off</option>
            <option value="1/4">Grid: 1/4</option>
            <option value="1/8">Grid: 1/8</option>
          </select>
        </div>
      </header>

      {error && (
        <div className="text-red-400">
          Failed to load: {String((error as any)?.message || error)}
        </div>
      )}
      {isLoading && <div className="text-slate-400">Loading…</div>}

      {!!sections?.length && (
        <div>
          <h2 className="text-sm mb-1 text-slate-400">Sections</h2>
          <SectionRail sections={sections} zoom={zoom} />
        </div>
      )}

      <div>
        <h2 className="text-sm mb-1 text-slate-400">Timeline</h2>
        <BarRuler
          beatsPerBar={beatsPerBar}
          totalBeats={totalBeats}
          zoom={zoom}
        />
      </div>

      <div>
        <h2 className="text-sm mb-1 text-slate-400">Chords</h2>
        <ChordLane
          chords={qChords}
          zoom={zoom}
          beatsPerBar={beatsPerBar}
          totalBeats={totalBeats}
        />
      </div>

      {!!issues?.length && (
        <div>
          <h2 className="text-sm mb-1 text-slate-400">Issues</h2>
          <ul className="list-disc ml-5 text-sm text-amber-300">
            {issues.map((i, idx) => (
              <li key={idx}>{i}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
