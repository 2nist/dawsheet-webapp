"use client";
import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useTimelineStore } from "@/lib/timelineStore";
import { SectionsLane } from "@/components/timeline/SectionsLane";
import { LyricsLane } from "@/components/timeline/LyricsLane";
import { ChordsLane } from "@/components/timeline/ChordsLane";
import { TimelineHeader } from "@/components/timeline/TimelineHeader";
import { SectionReader } from "@/components/timeline/SectionReader";
import { InspectorPanel } from "@/components/timeline/InspectorPanel";

export default function SongTimelinePage() {
  const params = useParams();
  const id = String(params?.id || "");
  const { setData, setZoom, zoom } = useTimelineStore((s) => ({
    setData: s.setData,
    setZoom: s.setZoom,
    zoom: s.zoom,
  }));
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [meta, setMeta] = useState<{
    title?: string;
    artist?: string;
    timeSignature?: string;
    bpm?: number;
  } | null>(null);
  const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!id) return;
      setLoading(true);
      setErr(null);
      try {
        const res = await fetch(`${apiBase}/v1/songs/${id}/doc`);
        if (!res.ok) throw new Error(await res.text());
        const doc = await res.json();
        if (cancelled) return;
        setMeta({
          title: String(doc?.title || ""),
          artist: String(doc?.artist || ""),
          timeSignature: String(doc?.timeSignature || "4/4"),
          bpm: typeof doc?.bpm === "number" ? doc.bpm : undefined,
        });
        const sections = Array.isArray(doc?.sections)
          ? doc.sections.map((s: any, i: number) => ({
              id: String(s.id ?? `s${i + 1}`),
              name: String(s.name ?? `Section ${i + 1}`),
              startBeat: Number(s.startBeat ?? 0),
              lengthBeats: Number(s.lengthBeats ?? 8),
              color: s.color,
            }))
          : [];
        const lyricsArr: Array<{ id: string; text: string; beat: number }> = [];
        const chordsArr: Array<{
          id: string;
          symbol: string;
          startBeat: number;
        }> = [];
        if (Array.isArray(doc?.chords)) {
          (doc.chords as any[]).forEach((c: any, i: number) => {
            const symbol = String(
              c?.symbol ?? c?.name ?? c?.chord ?? ""
            ).trim();
            const sb =
              typeof c?.startBeat === "number" ? c.startBeat : undefined;
            if (!symbol || typeof sb !== "number") return;
            chordsArr.push({ id: `c${i + 1}`, symbol, startBeat: sb });
          });
        }
        if (Array.isArray(doc?.lyrics)) {
          // Heuristic placement: align to chord starts when available, else spread every 4 beats
          const chords = (
            Array.isArray(doc?.chords) ? doc.chords : []
          ) as Array<{ startBeat?: number }>;
          let fallbackBeat = 0;
          const stride = 4;
          (doc.lyrics as any[]).forEach((ln: any, i: number) => {
            const text = String(ln?.text ?? "").trim();
            if (!text) return;
            let beat =
              typeof ln?.beat === "number"
                ? ln.beat
                : (undefined as number | undefined);
            if (typeof beat !== "number") {
              const c = chords[i];
              if (c && typeof c.startBeat === "number")
                beat = c.startBeat as number;
            }
            if (typeof beat !== "number") {
              beat = fallbackBeat;
              fallbackBeat += stride;
            }
            lyricsArr.push({ id: `l${i + 1}`, text, beat });
          });
        }
        setData({
          sections,
          lyrics: lyricsArr,
          chords: chordsArr,
          euclids: [],
        });
      } catch (e: any) {
        setErr(e?.message || String(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [id, apiBase, setData]);

  return (
    <div className="p-4 space-y-4">
      <TimelineHeader meta={{ ...meta, title: meta?.title || `Song ${id}` }} />
      {loading && <div className="text-xs text-slate-400">Loading…</div>}
      {err && <div className="text-xs text-amber-400">{err}</div>}
      <div className="grid grid-cols-12 gap-4 items-start">
        <div className="col-span-8">
          <SectionReader />
          <div className="mt-4 space-y-2 overflow-x-auto">
            <SectionsLane />
            <LyricsLane />
            <ChordsLane />
          </div>
        </div>
        <div className="col-span-4">
          <InspectorPanel />
        </div>
      </div>
    </div>
  );
}
