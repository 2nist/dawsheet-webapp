import React from "react";
import { useRouter } from "next/router";
import useSWR from "swr";
import { swrFetcher } from "@/lib/api";
import { SectionRail } from "@/components/SectionRail";
import { ChordLane } from "@/components/ChordLane";
import { BarRuler } from "@/components/BarRuler";
import { LyricLane } from "@/components/LyricLane";

export default function SongDetailPage() {
  const router = useRouter();
  const { id } = router.query;
  const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
  const [zoom, setZoom] = React.useState(8); // px per beat
  const [grid, setGrid] = React.useState<"off" | "1/4" | "1/8">("1/4");
  // orientation toggles per lane
  const [sectionsOri, setSectionsOri] = React.useState<
    "horizontal" | "vertical"
  >("horizontal");
  const [rulerOri, setRulerOri] = React.useState<"horizontal" | "vertical">(
    "horizontal"
  );
  const [chordsOri, setChordsOri] = React.useState<"horizontal" | "vertical">(
    "horizontal"
  );
  const [lyricsOri, setLyricsOri] = React.useState<"horizontal" | "vertical">(
    "horizontal"
  );
  const [editMode, setEditMode] = React.useState(false);

  const sid = React.useMemo(
    () => (id ? (Array.isArray(id) ? id[0] : id) : null),
    [id]
  );
  const docUrl = React.useMemo(
    () => (sid ? `${apiBase}/v1/songs/${sid}/doc` : null),
    [sid, apiBase]
  );
  const timelineUrl = React.useMemo(
    () => (sid ? `${apiBase}/v1/songs/${sid}/timeline` : null),
    [sid, apiBase]
  );

  const { data: docData } = useSWR(docUrl, swrFetcher);
  // Fetch timeline always (cheap) so we can fallback if doc missing chords/lyrics
  const {
    data: timelineData,
    error,
    isLoading,
    mutate,
  } = useSWR(timelineUrl, swrFetcher);

  // Normalize: prefer analyzed doc for raw structures, but if empty chords use timeline
  const analyzed = docData as any;
  const timeline = (timelineData as any)?.timeline;
  const doc = analyzed || timeline || {};
  const sections = analyzed?.sections?.length
    ? analyzed.sections
    : timeline?.sections || [];
  const chords = (
    analyzed?.chords?.length
      ? analyzed.chords.map((c: any) => ({
          symbol: c.symbol,
          startBeat: c.startBeat ?? c.atBeat,
        }))
      : timeline?.chords || []
  ) as { symbol: string; startBeat: number }[];
  const lyrics = (
    analyzed?.lyrics?.length ? analyzed.lyrics : timeline?.lyrics || []
  ) as {
    text: string;
    ts_sec?: number | null;
    beat?: number | null;
  }[];
  const issues: string[] = analyzed?.issues || [];
  const timeSig: string =
    analyzed?.timeSignature ||
    (timeline?.timeSigDefault
      ? `${timeline.timeSigDefault.num}/${timeline.timeSigDefault.den}`
      : "4/4");
  const beatsPerBar = Number(timeSig?.split("/")[0] || "4") || 4;

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

  // Lyrics search/attach helpers
  const [searching, setSearching] = React.useState(false);
  const [searchErr, setSearchErr] = React.useState<string | null>(null);
  const [found, setFound] = React.useState<{
    matched: boolean;
    synced: boolean;
    lines: { ts_sec: number | null; text: string }[];
  } | null>(null);

  async function searchLyrics() {
    if (!doc) return;
    setSearching(true);
    setSearchErr(null);
    setFound(null);
    try {
      const title = encodeURIComponent(doc?.title || "");
      const artist = encodeURIComponent(doc?.artist || "");
      const res = await fetch(
        `${apiBase}/lyrics/search?title=${title}&artist=${artist}`
      );
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setFound({
        matched: !!data.matched,
        synced: !!data.synced,
        lines: (data.lines || []) as any,
      });
    } catch (e: any) {
      setSearchErr(String(e));
    } finally {
      setSearching(false);
    }
  }

  async function attachLyrics() {
    if (!id || !found) return;
    const sid = Array.isArray(id) ? id[0] : id;
    try {
      const res = await fetch(`${apiBase}/songs/${sid}/attach-lyrics`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ lines: found.lines, mode: "append" }),
      });
      if (!res.ok) throw new Error(await res.text());
      // Refresh the analyzed doc to include newly attached lyrics
      await mutate();
      setFound(null);
    } catch (e: any) {
      alert(`Attach failed: ${String(e)}`);
    }
  }

  const [chordsLive, setChordsLive] = React.useState<typeof chords>([]);
  const [lyricsLive, setLyricsLive] = React.useState<typeof lyrics>([]);
  React.useEffect(() => {
    setChordsLive(chords);
  }, [chords]);
  React.useEffect(() => {
    setLyricsLive(lyrics);
  }, [lyrics]);

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
          {/* Quick link to the new App Router timeline view */}
          {id && (
            <a
              href={`/songs/${Array.isArray(id) ? id[0] : id}/timeline`}
              className="px-3 py-1 text-sm rounded border border-sky-500/40 bg-sky-700 hover:bg-sky-600"
              title="Open the new Timeline view"
            >
              Open Timeline (new)
            </a>
          )}
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

      {/* layout toggles */}
      <div className="flex flex-wrap gap-2 text-xs items-center">
        <label className="flex items-center gap-1">
          Edit:
          <input
            type="checkbox"
            checked={editMode}
            onChange={(e) => setEditMode(e.target.checked)}
          />
        </label>
        <label className="flex items-center gap-1">
          Sections:
          <select
            className="bg-slate-900 border border-slate-700 rounded px-1 py-0.5"
            value={sectionsOri}
            onChange={(e) => setSectionsOri(e.target.value as any)}
          >
            <option value="horizontal">Horizontal</option>
            <option value="vertical">Vertical</option>
          </select>
        </label>
        <label className="flex items-center gap-1">
          Ruler:
          <select
            className="bg-slate-900 border border-slate-700 rounded px-1 py-0.5"
            value={rulerOri}
            onChange={(e) => setRulerOri(e.target.value as any)}
          >
            <option value="horizontal">Horizontal</option>
            <option value="vertical">Vertical</option>
          </select>
        </label>
        <label className="flex items-center gap-1">
          Chords:
          <select
            className="bg-slate-900 border border-slate-700 rounded px-1 py-0.5"
            value={chordsOri}
            onChange={(e) => setChordsOri(e.target.value as any)}
          >
            <option value="horizontal">Horizontal</option>
            <option value="vertical">Vertical</option>
          </select>
        </label>
        <label className="flex items-center gap-1">
          Lyrics:
          <select
            className="bg-slate-900 border border-slate-700 rounded px-1 py-0.5"
            value={lyricsOri}
            onChange={(e) => setLyricsOri(e.target.value as any)}
          >
            <option value="horizontal">Horizontal</option>
            <option value="vertical">Vertical</option>
          </select>
        </label>
      </div>

      {/* Vertical board (side-by-side columns) when any lane is vertical */}
      {(sectionsOri === "vertical" ||
        rulerOri === "vertical" ||
        chordsOri === "vertical" ||
        lyricsOri === "vertical") && (
        <div className="flex gap-2">
          {/* Sections column */}
          <div className="flex-none" style={{ width: 72 }}>
            <SectionRail
              sections={sections}
              zoom={zoom}
              orientation="vertical"
              totalBeats={totalBeats}
            />
          </div>
          {/* Ruler column */}
          <div className="flex-none" style={{ width: 56 }}>
            <BarRuler
              beatsPerBar={beatsPerBar}
              totalBeats={totalBeats}
              zoom={zoom}
              orientation="vertical"
            />
          </div>
          {/* Chords column */}
          <div className="flex-1">
            <ChordLane
              chords={chordsLive}
              zoom={zoom}
              beatsPerBar={beatsPerBar}
              totalBeats={totalBeats}
              orientation="vertical"
              editable={editMode}
              onChange={setChordsLive}
            />
          </div>
          {/* Lyrics column */}
          <div className="flex-1">
            <LyricLane
              lyrics={lyricsLive}
              zoom={zoom}
              beatsPerBar={beatsPerBar}
              totalBeats={totalBeats}
              orientation="vertical"
              editable={editMode}
              onChange={setLyricsLive}
            />
          </div>
        </div>
      )}

      {error && (
        <div className="text-red-400">
          Failed to load: {String((error as any)?.message || error)}
        </div>
      )}
      {isLoading && <div className="text-slate-400">Loading…</div>}

      {!!sections?.length && (
        <div>
          <h2 className="text-sm mb-1 text-slate-400">Sections</h2>
          <SectionRail
            sections={sections}
            zoom={zoom}
            orientation={sectionsOri}
            totalBeats={totalBeats}
          />
        </div>
      )}

      <div>
        <h2 className="text-sm mb-1 text-slate-400">Timeline</h2>
        <BarRuler
          beatsPerBar={beatsPerBar}
          totalBeats={totalBeats}
          zoom={zoom}
          orientation={rulerOri}
        />
      </div>

      <div>
        <h2 className="text-sm mb-1 text-slate-400">Chords</h2>
        <ChordLane
          chords={qChords}
          zoom={zoom}
          beatsPerBar={beatsPerBar}
          totalBeats={totalBeats}
          orientation={chordsOri}
        />
      </div>

      {/* Only show the attach/search panel when the doc has loaded and truly has no lyrics */}
      {doc && (!lyrics || lyrics.length === 0) && (
        <div className="p-3 rounded border border-slate-700 bg-slate-900">
          <div className="flex items-center justify-between">
            <div className="text-sm text-slate-300">No lyrics attached.</div>
            <button
              className="px-3 py-1 text-sm rounded bg-emerald-700 hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed border border-emerald-500/40"
              onClick={searchLyrics}
              disabled={searching || !doc?.title || !doc?.artist}
              title={
                !doc?.title || !doc?.artist
                  ? "Needs title and artist to search"
                  : "Search timestamped lyrics via LRCLIB"
              }
            >
              {searching ? "Searching…" : "Search lyrics (LRCLIB)"}
            </button>
          </div>
          {(!doc?.title || !doc?.artist) && (
            <div className="mt-2 text-amber-300 text-xs">
              Set both title and artist to enable lyrics search.
            </div>
          )}
          {searchErr && (
            <div className="mt-2 text-amber-300 text-sm">{searchErr}</div>
          )}
          {found && (
            <div className="mt-3 text-sm">
              <div className="mb-2 text-slate-300">
                {found.matched ? (
                  <>
                    Found {found.lines.length} line
                    {found.lines.length === 1 ? "" : "s"}
                    {found.synced ? " (timestamped)" : " (plain)"}
                  </>
                ) : (
                  <>No results</>
                )}
              </div>
              {found.lines.length > 0 && (
                <>
                  <div className="max-h-40 overflow-auto bg-slate-950/60 border border-slate-700 rounded p-2 text-slate-200">
                    {found.lines.slice(0, 12).map((ln, i) => (
                      <div key={i} className="truncate">
                        {typeof ln.ts_sec === "number"
                          ? `[${ln.ts_sec.toFixed(2)}] `
                          : ""}
                        {ln.text}
                      </div>
                    ))}
                    {found.lines.length > 12 && (
                      <div className="text-slate-500">…and more</div>
                    )}
                  </div>
                  <div className="mt-2 flex gap-2">
                    <button
                      className="px-3 py-1 text-sm rounded bg-sky-700 hover:bg-sky-600 border border-sky-500/40"
                      onClick={attachLyrics}
                    >
                      Attach to song
                    </button>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      )}
      {!doc && !error && !isLoading && (
        <div className="text-xs text-slate-400">Waiting for song data…</div>
      )}

      {!!lyrics?.length && (
        <div>
          <h2 className="text-sm mb-1 text-slate-400">Lyrics</h2>
          <LyricLane
            lyrics={lyrics}
            zoom={zoom}
            beatsPerBar={beatsPerBar}
            totalBeats={totalBeats}
            orientation={lyricsOri}
          />
        </div>
      )}

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
