"use client";
import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useTimelineStore } from "@/lib/timelineStore";
import { toTimeline } from "@/lib/mappers/toTimeline"; // legacy fallback only
import { SectionsLane } from "@/components/timeline/SectionsLane";
import { LyricsLane } from "@/components/timeline/LyricsLane";
import { ChordsLane } from "@/components/timeline/ChordsLane";
import { TimelineHeader } from "@/components/timeline/TimelineHeader";
import { SectionReader } from "@/components/timeline/SectionReader";
import { InspectorPanel } from "@/components/timeline/InspectorPanel";
import { SectionChordLyricChart } from "@/components/timeline/SectionChordLyricChart";
import { CommandToolbar } from "@/components/CommandToolbar";
import { FEATURE_SECTION_CHART } from "@/lib/featureFlags";

export default function SongTimelinePage() {
  const params = useParams();
  const id = String(params?.id || "");
  const {
    setData,
    setZoom,
    zoom,
    setTimeline,
    dataStatus,
    setDataStatus,
    warnings,
    timeline,
    setValidationErrors,
    validationErrors,
  } = useTimelineStore((s) => ({
    setData: s.setData,
    setZoom: s.setZoom,
    zoom: s.zoom,
    setTimeline: s.setTimeline,
    dataStatus: s.dataStatus,
    setDataStatus: s.setDataStatus,
    warnings: s.warnings,
    timeline: s.timeline,
    setValidationErrors: s.setValidationErrors,
    validationErrors: s.validationErrors,
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
        setDataStatus("loading");
        const res = await fetch(`${apiBase}/v1/songs/${id}/timeline`);
        if (res.status === 422) {
          const detail = await res.json();
          if (cancelled) return;
          setValidationErrors(detail.detail?.validation || []);
          setDataStatus("error", "Timeline invalid");
          return;
        }
        if (!res.ok) throw new Error(await res.text());
        const timelineResp = await res.json();
        if (cancelled) return;
        const tl = timelineResp.timeline;
        const ws = timelineResp.warnings || [];
        setValidationErrors(undefined);
        setTimeline(tl, ws);
        setDataStatus("ok");
        setMeta({
          title: tl.title,
          artist: tl.artist,
          timeSignature: tl.timeSigDefault
            ? `${tl.timeSigDefault.num}/${tl.timeSigDefault.den}`
            : "4/4",
          bpm: tl.bpmDefault,
        });
      } catch (e: any) {
        setErr(e?.message || String(e));
        setDataStatus("error", e?.message || String(e));
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
    <div className="space-y-0">
      <CommandToolbar />
      <div className="p-4 space-y-4">
        <TimelineHeader
          meta={{ ...meta, title: meta?.title || timelineTitle(meta, id) }}
        />
        <StatusBanner id={id} />
        {loading && <div className="text-xs text-slate-400">Loading…</div>}
        {err && <div className="text-xs text-amber-400">{err}</div>}
        <div className="grid grid-cols-12 gap-4 items-start">
          <div className="col-span-8">
            {dataStatus === "ok" && <SectionReader />}
            {FEATURE_SECTION_CHART && dataStatus === "ok" && (
              <div className="mt-6">
                <details className="group" open>
                  <summary className="cursor-pointer select-none text-sm font-medium flex items-center gap-2">
                    <span>Chord/Lyric Chart</span>
                    <span className="text-[10px] text-slate-400 group-open:hidden">
                      (expand)
                    </span>
                    <span className="text-[10px] text-slate-400 hidden group-open:inline">
                      (collapse)
                    </span>
                  </summary>
                  <div className="mt-3">
                    <SectionChordLyricChart />
                  </div>
                </details>
              </div>
            )}
            {dataStatus === "ok" && (
              <div className="mt-4 space-y-2 overflow-x-auto">
                <SectionsLane />
                <LyricsLane />
                <ChordsLane />
              </div>
            )}
          </div>
          <div className="col-span-4">
            {dataStatus === "ok" && <InspectorPanel />}
          </div>
        </div>
      </div>
    </div>
  );
}

function timelineTitle(meta: any, id: string) {
  return meta?.title || `Song ${id}`;
}

function StatusBanner({ id }: { id: string }) {
  const { dataStatus, warnings, timeline, validationErrors } = useTimelineStore(
    (s) => ({
      dataStatus: s.dataStatus,
      warnings: s.warnings,
      timeline: s.timeline,
      validationErrors: s.validationErrors,
    })
  );
  if (dataStatus === "idle") return null;
  const baseCls =
    "text-[11px] px-2 py-1 rounded border inline-flex items-center gap-3 mb-2";
  if (dataStatus === "loading")
    return (
      <div className={`${baseCls} bg-slate-800 border-slate-600`}>
        Loading timeline…
      </div>
    );
  if (dataStatus === "error")
    return (
      <div className={`${baseCls} bg-red-900/60 border-red-500 text-red-100`}>
        Failed to load{" "}
        {validationErrors && validationErrors.length > 0 && (
          <span className="text-red-300">
            ({validationErrors.length} validation errors)
          </span>
        )}
      </div>
    );
  const secCount = timeline?.sections?.length || 0;
  const chordCount = timeline?.chords?.length || 0;
  const lyrCount = timeline?.lyrics?.length || 0;
  const bpm = timeline?.bpmDefault;
  const ts = timeline?.timeSigDefault;
  return (
    <div
      className={`${baseCls} bg-slate-900/70 border-slate-600 text-slate-200`}
    >
      <span className="font-medium">Data</span>
      <span>{secCount} sections</span>
      <span>{chordCount} chords</span>
      <span>{lyrCount} lyrics</span>
      <span>
        {ts?.num}/{ts?.den} • {bpm} bpm
      </span>
      {warnings.length > 0 && (
        <span className="text-red-300">⚠ {warnings.length}</span>
      )}
    </div>
  );
}
