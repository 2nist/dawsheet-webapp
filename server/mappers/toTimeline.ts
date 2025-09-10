import {
  SongTimeline,
  Section,
  TempoMark,
  TimeSigMark,
  ChordEvent,
  LyricEvent,
  TimelineValidationWarning,
} from "../../web/types/timeline";

// Placeholder source types (loosely based on existing import pipeline)
// Extended raw source allows authoritative beat-based placement. Any beat-based
// field takes precedence over time-based counterparts.
interface RawSongSource {
  id: string;
  title: string;
  artist?: string;
  bpm?: number;
  timeSig?: { num: number; den: number };
  chords?: Array<{
    symbol: string;
    timeSec?: number; // legacy
    durationSec?: number; // legacy
    startBeat?: number; // authoritative if present
    lengthBeats?: number; // authoritative chord duration
    durationBeats?: number; // alias support
  }>;
  lyrics?: Array<{
    timeSec?: number; // legacy (seconds)
    beat?: number; // authoritative if present
    text: string;
    id?: string;
  }>; // from LRC (per-line)
  sections?: Array<{
    name: string;
    startSec?: number; // legacy
    endSec?: number; // legacy
    startBeat?: number; // authoritative if present
    lengthBeats?: number; // authoritative if present
  }>;
  analysis?: { bpm?: number; key?: string; mode?: string };
}

interface MapOptions {
  fallbackBpm?: number; // default if not found
  fallbackTimeSig?: { num: number; den: number };
  snap?: number; // beats
}

const DEFAULT_BPM = 120; // only used if everything else missing
const DEFAULT_SIG = { num: 4, den: 4 };

function secToBeats(sec: number, tempoMap: TempoMark[]): number {
  // For now we only support constant tempo (first mark). If multiple marks exist,
  // fall back to original piecewise accumulation.
  if (tempoMap.length === 1) {
    const bpm = tempoMap[0].bpm;
    return (sec * bpm) / 60;
  }
  let beats = 0;
  for (let i = 0; i < tempoMap.length; i++) {
    const cur = tempoMap[i];
    const next = tempoMap[i + 1];
    const segEnd = next ? next.atSec : sec;
    if (sec <= cur.atSec) break;
    const effectiveEnd = Math.min(sec, segEnd);
    const dur = Math.max(0, effectiveEnd - cur.atSec);
    beats += (dur * cur.bpm) / 60;
    if (!next || sec < segEnd) break;
  }
  return beats;
}

function beatsToSec(beats: number, tempoMap: TempoMark[]): number {
  if (tempoMap.length === 0) return 0;
  // constant tempo assumption for now
  const bpm = tempoMap[0].bpm;
  return (beats * 60) / bpm;
}

function quantizeBeat(beat: number, snap: number) {
  return Math.round(beat / snap) * snap;
}

// Simple 4-gram hash for chord symbols
function chordGramHash(symbols: string[], i: number) {
  return symbols.slice(i, i + 4).join("|");
}

function guessSections(chords: ChordEvent[], lyrics: LyricEvent[]): Section[] {
  if (!chords.length) return [];
  const symbols = chords.map((c) => c.symbol);
  const hashes: Record<string, number> = {};
  for (let i = 0; i + 4 <= symbols.length; i++) {
    const h = chordGramHash(symbols, i);
    hashes[h] = (hashes[h] || 0) + 1;
  }
  const entries = Object.entries(hashes).sort((a, b) => b[1] - a[1]);
  const primary = new Set(entries.slice(0, 2).map((e) => e[0]));
  // Partition by large lyrical gaps (>4 beats)
  const lyricBeats = lyrics.map((l) => l.atBeat ?? 0).sort((a, b) => a - b);
  const gaps: number[] = [];
  for (let i = 1; i < lyricBeats.length; i++) {
    const gap = lyricBeats[i] - lyricBeats[i - 1];
    if (gap > 8) gaps.push(lyricBeats[i - 1]);
  }
  const sections: Section[] = [];
  // Very naive: treat entire song as one Verse if no repetition
  if (!entries.length) {
    sections.push({ kind: "Verse", startSec: chords[0].atSec, inferred: true });
    return sections;
  }
  // Build segments from larger gaps or chord pattern changes
  let currentStart = chords[0].atSec;
  let lastHash = chordGramHash(symbols, 0);
  for (let i = 4; i < symbols.length; i++) {
    const h = chordGramHash(symbols, i - 3);
    if (h !== lastHash) {
      // close previous
      const segEndSec = chords[i - 3].atSec;
      sections.push({
        kind: primary.has(lastHash) ? "Verse" : "Chorus",
        startSec: currentStart,
        endSec: segEndSec,
        inferred: true,
      });
      currentStart = segEndSec;
      lastHash = h;
    }
  }
  sections.push({
    kind: primary.has(lastHash) ? "Verse" : "Chorus",
    startSec: currentStart,
    inferred: true,
  });
  return sections;
}

export function toTimeline(
  raw: RawSongSource,
  opts: MapOptions = {}
): { timeline: SongTimeline; warnings: TimelineValidationWarning[] } {
  const warnings: TimelineValidationWarning[] = [];
  const bpm = raw.bpm || raw.analysis?.bpm || opts.fallbackBpm || DEFAULT_BPM;
  const timeSig = raw.timeSig || opts.fallbackTimeSig || DEFAULT_SIG;
  if (!raw.bpm && raw.analysis?.bpm)
    warnings.push({ code: "bpm.inferred", message: "Using analysis BPM" });
  if (!raw.timeSig)
    warnings.push({
      code: "timesig.default",
      message: "Default time signature used",
    });
  const tempoMap: TempoMark[] = [{ atSec: 0, bpm }];
  const timeSigMap: TimeSigMark[] = [
    { atSec: 0, num: timeSig.num, den: timeSig.den },
  ];
  const snap = opts.snap ?? 0.25; // quarter beat

  // Helper: map section name to kind if possible
  const normalizeSectionKind = (name?: string): Section["kind"] => {
    if (!name) return "Verse";
    const n = name.toLowerCase();
    if (n.includes("chorus")) return "Chorus";
    if (n.includes("bridge")) return "Bridge";
    if (n.includes("intro")) return "Intro";
    if (n.includes("outro")) return "Outro";
    if (n.includes("pre")) return "PreChorus";
    if (n.includes("solo")) return "Solo";
    if (n.includes("instr")) return "Instrumental";
    return (name as Section["kind"]) || "Verse";
  };

  // Sections: prefer beat-based definitions if present.
  let sections: Section[] = [];
  const hasBeatSections = !!raw.sections?.some(
    (s) => typeof s.startBeat === "number"
  );
  if (raw.sections?.length) {
    sections = raw.sections.map((s) => {
      let startSec: number | undefined = s.startSec;
      let endSec: number | undefined = s.endSec;
      if (typeof s.startBeat === "number")
        startSec = beatsToSec(s.startBeat, tempoMap);
      if (typeof s.lengthBeats === "number")
        endSec = beatsToSec((s.startBeat || 0) + s.lengthBeats, tempoMap);
      return {
        kind: normalizeSectionKind(s.name),
        startSec: startSec ?? 0,
        endSec,
        name: s.name,
      };
    });
  }

  // Chords mapping (authoritative beats if provided)
  let chords: ChordEvent[] = (raw.chords || []).map((c) => {
    const hasBeat = typeof c.startBeat === "number";
    const atBeatRaw = hasBeat
      ? (c.startBeat as number)
      : secToBeats(c.timeSec || 0, tempoMap);
    const atBeat = quantizeBeat(atBeatRaw, snap);
    const atSec = hasBeat ? beatsToSec(atBeat, tempoMap) : c.timeSec || 0;
    let durationBeats = c.lengthBeats ?? c.durationBeats;
    if (durationBeats == null && c.durationSec != null)
      durationBeats = secToBeats(c.durationSec, tempoMap);
    return { symbol: c.symbol, atSec, atBeat, durationBeats } as ChordEvent;
  });

  // Sort chords by beat for duration inference
  chords.sort((a, b) => (a.atBeat ?? 0) - (b.atBeat ?? 0));
  // Infer missing durations by next chord or section end
  for (let i = 0; i < chords.length; i++) {
    const ch = chords[i];
    if (ch.durationBeats == null) {
      const next = chords[i + 1];
      if (next?.atBeat != null && ch.atBeat != null) {
        ch.durationBeats = Math.max(0.25, next.atBeat - ch.atBeat);
      }
    }
  }
  // If still missing durations, attempt fill using section boundaries
  if (sections.length) {
    for (const ch of chords) {
      if (ch.durationBeats == null && ch.atBeat != null) {
        // Find section containing chord
        const sec = sections.find(
          (s) =>
            ch.atSec >= s.startSec && (s.endSec == null || ch.atSec < s.endSec)
        );
        if (sec && sec.endSec != null) {
          const secEndBeat = secToBeats(sec.endSec, tempoMap);
          ch.durationBeats = Math.max(0.25, secEndBeat - ch.atBeat);
        }
      }
    }
  }

  // Lyrics mapping (prefer beat if provided)
  const lyrics: LyricEvent[] = (raw.lyrics || []).map((l) => {
    const hasBeat = typeof l.beat === "number";
    const atBeatRaw = hasBeat
      ? (l.beat as number)
      : secToBeats(l.timeSec || 0, tempoMap);
    const atBeat = quantizeBeat(atBeatRaw, snap);
    const atSec = hasBeat ? beatsToSec(atBeat, tempoMap) : l.timeSec || 0;
    return {
      atSec,
      atBeat,
      text: l.text,
      id: l.id || (hasBeat ? `b${atBeat}` : String(l.timeSec)),
    };
  });

  // If no sections provided, fallback to heuristic (but suppress if we had beat-based chords & lyrics - we trust beats)
  if (!sections.length) {
    sections = guessSections(chords, lyrics);
    if (sections.some((s) => s.inferred))
      warnings.push({
        code: "sections.inferred",
        message: "Sections inferred heuristically",
      });
  }

  // Pair chords to nearest lyric within 1 beat for hover linking
  if (lyrics.length && chords.length) {
    const lyricByBeat = lyrics
      .slice()
      .sort((a, b) => (a.atBeat ?? 0) - (b.atBeat ?? 0));
    for (const ch of chords) {
      if (ch.atBeat == null) continue;
      let best: LyricEvent | undefined;
      let bestDist = Infinity;
      for (const ly of lyricByBeat) {
        if (ly.atBeat == null) continue;
        const d = Math.abs(ly.atBeat - ch.atBeat);
        if (d < bestDist) {
          bestDist = d;
          best = ly;
          if (d === 0) break;
        }
        if (ly.atBeat > ch.atBeat + 1) break; // beyond window
      }
      if (best && bestDist <= 1) ch.lyricId = best.id;
    }
  }

  // Validation style warnings (only structural issues)
  // Ensure chords reside within some section when explicit sections given
  if (sections.length && !sections.some((s) => s.inferred)) {
    const outOfSection = chords.filter(
      (c) =>
        !sections.find(
          (s) =>
            c.atSec >= s.startSec && (s.endSec == null || c.atSec < s.endSec)
        )
    );
    if (outOfSection.length) {
      warnings.push({
        code: "chords.orphan",
        message: `${outOfSection.length} chord(s) outside any section`,
      });
    }
  }

  const timeline: SongTimeline = {
    id: raw.id,
    title: raw.title,
    artist: raw.artist,
    bpmDefault: bpm,
    timeSigDefault: timeSig,
    tempoMap,
    timeSigMap,
    sections,
    chords,
    lyrics,
    key: raw.analysis?.key,
    mode: raw.analysis?.mode,
  };

  return { timeline, warnings };
}

export function validateTimeline(t: SongTimeline): TimelineValidationWarning[] {
  const out: TimelineValidationWarning[] = [];
  if (!t.bpmDefault || t.bpmDefault <= 0)
    out.push({ code: "bpm.missing", message: "Missing BPM" });
  if (!t.timeSigDefault)
    out.push({ code: "timesig.missing", message: "Missing time signature" });
  if (!t.chords.length)
    out.push({ code: "chords.empty", message: "No chords present" });
  if (!t.lyrics.length)
    out.push({ code: "lyrics.empty", message: "No lyrics present" });
  return out;
}
