import { useMemo, useRef, useState } from 'react'
import { useTimelineStore } from '@/lib/timelineStore'
import { barsForLength, beatAt, romanizeChord } from '@/lib/timelineUtils'
import { DEFAULT_TS, beatsPerBar } from '@/lib/units'

const QUALITIES = ['maj7', 'min7', '7', 'sus', 'dim', 'aug']
const CADENCES = [
  { name: 'ii–V–I', seq: ['Dm7', 'G7', 'Cmaj7'] },
  { name: 'I–vi–ii–V', seq: ['C', 'Am', 'Dm', 'G7'] },
]

export function ChordView() {
  const doc = useTimelineStore((s) => s.doc)
  const snap = useTimelineStore((s) => s.snap)
  const upsertChordAt = useTimelineStore((s) => s.upsertChordAt)
  const renameChord = useTimelineStore((s) => s.renameChord)
  const setChordLen = useTimelineStore((s) => s.setChordLen)
  const [roman, setRoman] = useState(false)

  const totalBeats = useMemo(() => doc?.sections.reduce((a, s) => a + s.len, 0) ?? 32, [doc])
  const ts = DEFAULT_TS
  const bars = barsForLength(totalBeats, ts)
  const bpb = beatsPerBar(ts)

  const placeChord = (bar: number, beatIdx: number, sym: string) => {
    const t = beatAt(bar, beatIdx, ts)
    upsertChordAt(t, sym, snap)
  }

  const [editingIdx, setEditingIdx] = useState<number | null>(null)
  const [editValue, setEditValue] = useState('')
  const dragRef = useRef<{ idx: number; startX: number; startLen: number } | null>(null)
  const beatCellPx = 64
  const onDragStart = (e: React.MouseEvent<HTMLDivElement>, idx: number, startLen: number) => {
    e.preventDefault()
    dragRef.current = { idx, startX: e.clientX, startLen }
    const onMove = (ev: MouseEvent) => {
      const dx = ev.clientX - (dragRef.current?.startX || 0)
      const beats = dx / beatCellPx
      const snapped = Math.round(beats / 0.25) * 0.25
      const nextLen = Math.max(0.25, (dragRef.current?.startLen || 0.25) + snapped)
      setChordLen(idx, nextLen)
    }
    const onUp = () => {
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
      dragRef.current = null
    }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr', gap: 12 }}>
      <aside style={{ borderRight: '1px solid #eee', padding: 8 }}>
        <div style={{ fontWeight: 600, marginBottom: 6 }}>Palette</div>
        <div style={{ display: 'grid', gap: 6 }}>
          <div>Qualities</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {['C', 'D', 'E', 'F', 'G', 'A', 'B'].flatMap((r) =>
              QUALITIES.map((q) => (
                <button key={r + q} onClick={() => placeChord(0, 0, r + q)}>
                  {r}
                  {q}
                </button>
              )),
            )}
          </div>
          <div>Cadences</div>
          <div style={{ display: 'grid', gap: 6 }}>
            {CADENCES.map((c) => (
              <button
                key={c.name}
                onClick={() => {
                  // drop cadence at bar 0 sequentially
                  c.seq.forEach((s, i) => placeChord(i, 0, s))
                }}
              >
                {c.name}
              </button>
            ))}
          </div>
          <label style={{ marginTop: 8 }}>
            <input type="checkbox" checked={roman} onChange={(e) => setRoman(e.target.checked)} />
            Roman numerals
          </label>
        </div>
      </aside>
      <main style={{ overflow: 'auto' }}>
        <div style={{ display: 'grid', gap: 2 }}>
          {Array.from({ length: bars }).map((_, bar) => (
            <div
              key={bar}
              style={{ display: 'grid', gridTemplateColumns: `60px repeat(${bpb}, 1fr)` }}
            >
              <div style={{ padding: '6px 8px', color: '#666' }}>Bar {bar + 1}</div>
              {Array.from({ length: bpb }).map((__, bi) => {
                const t = beatAt(bar, bi, ts)
                const chord = doc?.chords.find((c) => Math.abs(c.t - t) < 1e-6)
                const label = chord ? (roman ? romanizeChord(chord.symbol) : chord.symbol) : ''
                return (
                  <button
                    key={bi}
                    onClick={() => placeChord(bar, bi, chord?.symbol || 'C')}
                    title={`Beat ${bi + 1}`}
                    style={{
                      border: '1px solid #ddd',
                      background: chord ? '#eef' : 'white',
                      padding: 8,
                      textAlign: 'center',
                      minWidth: 64,
                      position: 'relative',
                    }}
                    onDoubleClick={(e) => {
                      if (doc && chord) {
                        const idx = doc.chords.findIndex((c) => Math.abs(c.t - t) < 1e-6)
                        if (idx >= 0) {
                          setEditingIdx(idx)
                          setEditValue(chord.symbol)
                          e.preventDefault()
                          e.stopPropagation()
                        }
                      }
                    }}
                  >
                    {editingIdx != null && doc && chord && doc.chords[editingIdx] === chord ? (
                      <input
                        autoFocus
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        onBlur={() => {
                          if (editingIdx != null) renameChord(editingIdx, editValue.trim() || 'C')
                          setEditingIdx(null)
                        }}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            if (editingIdx != null) {
                              renameChord(editingIdx, editValue.trim() || 'C')
                            }
                            setEditingIdx(null)
                          } else if (e.key === 'Escape') {
                            setEditingIdx(null)
                          }
                        }}
                        style={{
                          position: 'absolute',
                          left: 2,
                          right: 2,
                          top: 6,
                          height: 24,
                          fontSize: 12,
                        }}
                      />
                    ) : (
                      <>
                        {label || '+'}
                        {chord && (
                          <div
                            onMouseDown={(e) => {
                              const idx =
                                doc?.chords.findIndex((c) => Math.abs(c.t - t) < 1e-6) ?? -1
                              if (idx >= 0) {
                                onDragStart(e, idx, doc!.chords[idx].len || 1)
                              }
                            }}
                            title="Drag to resize"
                            style={{
                              position: 'absolute',
                              right: 0,
                              top: 0,
                              bottom: 0,
                              width: 6,
                              cursor: 'ew-resize',
                            }}
                          />
                        )}
                      </>
                    )}
                  </button>
                )
              })}
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}
