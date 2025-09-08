import { create } from "zustand";

export type Section = {
  id: string;
  name: string;
  startBeat: number;
  lengthBeats: number;
  color?: string;
};
export type Chord = {
  id: string;
  symbol: string;
  startBeat: number;
  lengthBeats?: number;
};
export type LyricLine = {
  id: string;
  text: string;
  beat: number;
  row?: number;
};
export type EuclidClip = {
  id: string;
  startBeat: number;
  lengthBeats: number;
  steps: number;
  pulses: number;
  rotation: number;
  track: "drums" | "melodic";
  channel?: number;
  velocity?: number;
  gate?: number;
  swing?: number;
  probability?: number;
  perStep?: Array<{
    index: number;
    velocity?: number;
    gate?: number;
    probability?: number;
  }>;
};

export type Selection = {
  kind: "section" | "chord" | "lyric" | "euclid" | null;
  id?: string | null;
};

export type TimelineState = {
  zoom: number; // px per beat
  snap: number; // beats per grid unit
  sections: Section[];
  chords: Chord[];
  lyrics: LyricLine[];
  euclids: EuclidClip[];
  selection: Selection;
  setZoom: (z: number) => void;
  setSnap: (s: number) => void;
  setData: (
    data: Partial<
      Pick<TimelineState, "sections" | "chords" | "lyrics" | "euclids">
    >
  ) => void;
  updateItem: (kind: Selection["kind"], id: string, patch: any) => void;
  select: (kind: Selection["kind"], id?: string | null) => void;
};

export const useTimelineStore = create<TimelineState>((set, get) => ({
  zoom: 8,
  snap: 1,
  sections: [],
  chords: [],
  lyrics: [],
  euclids: [],
  selection: { kind: null },
  setZoom: (z) => set({ zoom: Math.max(1, Math.min(64, Math.round(z))) }),
  setSnap: (s) => set({ snap: Math.max(0.125, Math.min(4, s)) }),
  setData: (data) => set(data as any),
  updateItem: (kind, id, patch) => {
    const state = get();
    const key =
      kind === "section"
        ? "sections"
        : kind === "chord"
        ? "chords"
        : kind === "lyric"
        ? "lyrics"
        : kind === "euclid"
        ? "euclids"
        : null;
    if (!key) return;
    const list: any[] = (state as any)[key] || [];
    const next = list.map((it) => (it.id === id ? { ...it, ...patch } : it));
    set({ [key]: next } as any);
  },
  select: (kind, id) => set({ selection: { kind, id: id ?? null } }),
}));

export function beatPx(beat: number, zoom: number) {
  return beat * zoom;
}

// Estimate text width in pixels (fast path). Falls back to DOM measurement in browser.
export function textPxWidth(text: string, approxPxPerChar = 7): number {
  if (typeof window === "undefined")
    return Math.max(16, text.length * approxPxPerChar);
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d");
  if (!ctx) return Math.max(16, text.length * approxPxPerChar);
  const style = getComputedStyle(document.body);
  ctx.font = `${style.fontSize} ${style.fontFamily}`;
  const m = ctx.measureText(text || " ");
  return Math.ceil(Math.max(16, m.width));
}

// Simple greedy row-wrapper: place lyrics in rows avoiding collisions within a section
export function wrapLyricsRows(
  lines: LyricLine[],
  sections: Section[],
  zoom: number,
  pad = 8
) {
  const bySection = new Map<string, LyricLine[]>();
  // Assign sectionId inferred by beat position
  sections.forEach((s) => bySection.set(s.id, []));
  for (const l of lines) {
    const s =
      sections.find(
        (sec) =>
          l.beat >= sec.startBeat && l.beat < sec.startBeat + sec.lengthBeats
      ) || sections[sections.length - 1];
    if (!s) continue;
    (bySection.get(s.id) || bySection.set(s.id, []).get(s.id)!).push(l);
  }
  const placed: Record<string, { id: string; row: number }[]> = {};
  for (const s of sections) {
    const arr = (bySection.get(s.id) || [])
      .slice()
      .sort((a, b) => a.beat - b.beat);
    const rows: { endX: number }[] = [];
    placed[s.id] = [];
    for (const l of arr) {
      const left = (l.beat - s.startBeat) * zoom;
      const w = textPxWidth(l.text);
      // find first row with no collision
      let row = 0;
      for (; row < rows.length; row++) {
        if (left >= rows[row].endX + pad) break;
      }
      if (row === rows.length) rows.push({ endX: -Infinity });
      rows[row].endX = Math.max(rows[row].endX, left + w);
      placed[s.id].push({ id: l.id, row });
    }
  }
  return placed; // map of sectionId -> [{id,row}]
}

export function saveDraftChanges(draftId: string, state: TimelineState) {
  // For now, produce a minimal patch shape; backend endpoint to be added later.
  const patch = {
    sections: state.sections,
    chords: state.chords,
    lyrics: state.lyrics,
    euclids: state.euclids,
    meta: { zoom: state.zoom, snap: state.snap },
  };
  return patch;
}
