import { useMemo, useState } from 'react'
import { useTimelineStore } from '@/lib/timelineStore'
import { barsForLength, beatAt } from '@/lib/timelineUtils'
import { DEFAULT_TS, beatsPerBar } from '@/lib/units'

export function ChordLyricView() {
  const doc = useTimelineStore((s) => s.doc)
  const splitLyric = useTimelineStore((s) => s.splitLyric)
  const mergeLyricWithNext = useTimelineStore((s) => s.mergeLyricWithNext)
  const splitChord = useTimelineStore((s) => s.splitChord)
  const mergeChordWithNext = useTimelineStore((s) => s.mergeChordWithNext)
  const [lockEdits, setLockEdits] = useState(true)

  const totalBeats = useMemo(() => doc?.sections.reduce((a, s) => a + s.len, 0) ?? 32, [doc])
  const ts = useMemo(() => DEFAULT_TS, [])
  const bars = barsForLength(totalBeats, ts)
  const bpb = beatsPerBar(ts)

  const mismatch = useMemo(() => {
    if (!doc) return false
    // naive: mismatch when counts differ per bar
    for (let bar = 0; bar < bars; bar++) {
      const start = beatAt(bar, 0, ts)
      const end = beatAt(bar + 1, 0, ts)
      const chords = doc.chords.filter((c) => c.t >= start && c.t < end)
      const lyrics = doc.lyrics.filter((l) => l.t >= start && l.t < end)
      if (chords.length !== lyrics.length) return true
    }
    return false
  }, [doc, bars, ts])

  const syncCounts = (bar: number) => {
    if (!doc || !lockEdits) return
    const start = beatAt(bar, 0, ts)
    const end = beatAt(bar + 1, 0, ts)
    const chordIdxs = doc.chords
      .map((c, i) => ({ c, i }))
      .filter(({ c }) => c.t >= start && c.t < end)
      .map(({ i }) => i)
    const lyricIdxs = doc.lyrics
      .map((l, i) => ({ l, i }))
      .filter(({ l }) => l.t >= start && l.t < end)
      .map(({ i }) => i)
    let cCount = chordIdxs.length
    let lCount = lyricIdxs.length
    if (cCount === lCount) return
    if (cCount < lCount && chordIdxs.length > 0) {
      // split last chord repeatedly until counts match
      while (cCount < lCount) {
        splitChord(chordIdxs[chordIdxs.length - 1])
        cCount += 1
      }
    } else if (lCount < cCount && lyricIdxs.length > 0) {
      while (lCount < cCount) {
        splitLyric(lyricIdxs[lyricIdxs.length - 1])
        lCount += 1
      }
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: 8 }}>
        <label>
          <input
            type="checkbox"
            checked={lockEdits}
            onChange={(e) => setLockEdits(e.target.checked)}
          />
          Lock edits (update both)
        </label>
        {mismatch && (
          <span style={{ color: '#b45309' }}>
            Mismatch detected: chords and lyrics counts differ
          </span>
        )}
      </div>
      <div style={{ display: 'grid', gap: 8, padding: 8 }}>
        {Array.from({ length: bars }).map((_, bar) => (
          <div key={bar} style={{ border: '1px solid #ddd', borderRadius: 6 }}>
            <div style={{ padding: '4px 8px', background: '#f3f4f6', color: '#374151' }}>
              Bar {bar + 1}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: `80px repeat(${bpb}, 1fr)` }}>
              <div style={{ padding: 6, color: '#666' }}>Chords</div>
              {Array.from({ length: bpb }).map((__, i) => {
                const t = beatAt(bar, i, ts)
                const chordIdx = doc?.chords.findIndex((c) => Math.abs(c.t - t) < 1e-6) ?? -1
                return (
                  <div key={i} style={{ padding: 6, borderLeft: '1px solid #eee' }}>
                    {chordIdx >= 0 ? (
                      <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                        <span>{doc!.chords[chordIdx].symbol}</span>
                        {lockEdits && (
                          <>
                            <button
                              onClick={() => {
                                splitChord(chordIdx)
                                syncCounts(bar)
                              }}
                            >
                              Split
                            </button>
                            <button
                              onClick={() => {
                                mergeChordWithNext(chordIdx)
                                syncCounts(bar)
                              }}
                            >
                              Merge →
                            </button>
                          </>
                        )}
                      </div>
                    ) : (
                      <span style={{ color: '#aaa' }}>+</span>
                    )}
                  </div>
                )
              })}
              <div style={{ padding: 6, color: '#666' }}>Lyrics</div>
              {Array.from({ length: bpb }).map((__, i) => {
                const t = beatAt(bar, i, ts)
                const lyricIdx = doc?.lyrics.findIndex((l) => Math.abs(l.t - t) < 1e-6) ?? -1
                return (
                  <div key={i} style={{ padding: 6, borderLeft: '1px solid #eee' }}>
                    {lyricIdx >= 0 ? (
                      <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                        <span>{doc!.lyrics[lyricIdx].text}</span>
                        {lockEdits && (
                          <>
                            <button
                              onClick={() => {
                                splitLyric(lyricIdx)
                                syncCounts(bar)
                              }}
                            >
                              Split
                            </button>
                            <button
                              onClick={() => {
                                mergeLyricWithNext(lyricIdx)
                                syncCounts(bar)
                              }}
                            >
                              Merge →
                            </button>
                          </>
                        )}
                      </div>
                    ) : (
                      <span style={{ color: '#aaa' }}>+</span>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
