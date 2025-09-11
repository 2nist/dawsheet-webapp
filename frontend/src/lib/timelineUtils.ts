// Basic helpers for bar/beat math
export function beatsPerBar(timeSig: { num: number; den: number } = { num: 4, den: 4 }) {
  return timeSig.num * (4 / timeSig.den)
}

export function barsForLength(totalBeats: number, ts = { num: 4, den: 4 }) {
  const bpb = beatsPerBar(ts)
  return Math.ceil(totalBeats / bpb)
}

export function barBeatAt(beat: number, ts = { num: 4, den: 4 }) {
  const bpb = beatsPerBar(ts)
  const bar = Math.floor(beat / bpb)
  const within = beat - bar * bpb
  return { bar, within }
}

export function beatAt(bar: number, withinBeat: number, ts = { num: 4, den: 4 }) {
  return bar * beatsPerBar(ts) + withinBeat
}

// Super naive romanization for C major only (demo)
const DEGREE = ['I', 'bII', 'II', 'bIII', 'III', 'IV', 'bV', 'V', 'bVI', 'VI', 'bVII', 'VII']
export function romanizeChord(symbol: string, _key: 'C' | 'Am' = 'C') {
  // parse root as letter with optional #/b, map to semitone from C
  const m = symbol.match(/^([A-G](?:#|b)?)/)
  if (!m) return symbol
  const root = m[1]
  const map: Record<string, number> = {
    C: 0,
    'C#': 1,
    Db: 1,
    D: 2,
    'D#': 3,
    Eb: 3,
    E: 4,
    F: 5,
    'F#': 6,
    Gb: 6,
    G: 7,
    'G#': 8,
    Ab: 8,
    A: 9,
    'A#': 10,
    Bb: 10,
    B: 11,
  }
  const semis = map[root]
  if (semis == null) return symbol
  const deg = DEGREE[semis % 12]
  const qual = /m|min/.test(symbol) ? 'm' : /dim|°/.test(symbol) ? '°' : ''
  return `${deg}${qual}`
}
