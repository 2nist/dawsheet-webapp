export type TimeSig = { num: number; den: number }

export const DEFAULT_TS: TimeSig = { num: 4, den: 4 }

export function pxPerBeat(zoom: number) {
  return Math.max(8, 32 * zoom)
}

export function beatToX(beat: number, zoom: number) {
  return beat * pxPerBeat(zoom)
}

export function xToBeat(x: number, zoom: number) {
  return x / pxPerBeat(zoom)
}

export function beatsPerBar(ts: TimeSig = DEFAULT_TS) {
  return ts.num * (4 / ts.den)
}

export function barsForLength(totalBeats: number, ts: TimeSig = DEFAULT_TS) {
  const bpb = beatsPerBar(ts)
  return Math.max(1, Math.ceil(totalBeats / bpb))
}

export function formatBarBeat(beat: number, ts: TimeSig = DEFAULT_TS) {
  const bpb = beatsPerBar(ts)
  const bar = Math.floor(beat / bpb)
  const within = Math.floor(beat - bar * bpb)
  return `${bar + 1}.${within + 1}`
}
