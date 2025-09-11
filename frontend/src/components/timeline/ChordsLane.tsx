import { useTimelineStore } from '@/lib/timelineStore'
import { useMemo, useRef, useState } from 'react'
import { DEFAULT_TS, beatsPerBar, pxPerBeat } from '@/lib/units'
import { useResize } from '@/lib/interaction/useResize'

function ResizeHandle({
  zoom,
  startLen,
  onChange,
}: {
  zoom: number
  startLen: number
  onChange: (len: number) => void
}) {
  const dragProps = useResize({ zoom, startLen, onChange, snap: 0.25 })
  return (
    <div
      title="Drag to resize"
      style={{ position: 'absolute', right: 0, top: 0, bottom: 0, width: 6, cursor: 'ew-resize' }}
      {...dragProps}
    />
  )
}

export function ChordsLane() {
  const doc = useTimelineStore((s) => s.doc)
  const upsertChordAt = useTimelineStore((s) => s.upsertChordAt)
  const setChordLen = useTimelineStore((s) => s.setChordLen)
  const renameChord = useTimelineStore((s) => s.renameChord)
  const selection = useTimelineStore((s) => s.selection)
  const setSelection = useTimelineStore((s) => s.setSelection)
  const zoom = useTimelineStore((s) => s.zoom)
  const beatPx = Math.max(12, Math.round(pxPerBeat(zoom)))
  const ts = DEFAULT_TS
  const bpb = beatsPerBar(ts)
  const totalBeats = useMemo(() => doc?.sections.reduce((a, s) => a + s.len, 0) ?? 32, [doc])
  const bars = Math.ceil(totalBeats / bpb)

  const containerRef = useRef<HTMLDivElement | null>(null)
  const [editingIdx, setEditingIdx] = useState<number | null>(null)
  const [editValue, setEditValue] = useState('')

  const dragIdx = useRef<number | null>(null)

  return (
    <div style={{ borderBottom: '1px solid #eee' }}>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: `80px repeat(${bars * bpb}, ${beatPx}px)`,
        }}
        ref={containerRef}
      >
        <div style={{ padding: '6px 8px', color: '#666' }}>Chords</div>
        {Array.from({ length: bars * bpb }).map((_, i) => {
          const t = i
          const chord = doc?.chords.find((c) => Math.abs(c.t - t) < 1e-6)
          const idx = doc && chord ? doc.chords.findIndex((c) => c === chord) : -1
          const isSelected = selection.eventKind === 'chords' && selection.eventIndex === idx
          return (
            <button
              key={i}
              onClick={() => {
                upsertChordAt(t, chord?.symbol || 'C', chord?.len || 1)
                if (idx >= 0) setSelection({ eventKind: 'chords', eventIndex: idx })
              }}
              style={{
                borderLeft: '1px solid #f0f0f0',
                borderRight: i % bpb === bpb - 1 ? '1px solid #eee' : 'none',
                height: 28,
                background: chord ? (isSelected ? '#c7d2fe' : '#eef') : 'white',
                fontSize: 12,
                position: 'relative',
              }}
              title={`Beat ${i + 1}`}
              onDoubleClick={(e) => {
                if (idx >= 0 && chord) {
                  setEditingIdx(idx)
                  setEditValue(chord.symbol)
                  setSelection({ eventKind: 'chords', eventIndex: idx })
                  e.preventDefault()
                  e.stopPropagation()
                }
              }}
            >
              {editingIdx === idx ? (
                <input
                  autoFocus
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  onBlur={() => {
                    if (idx >= 0) renameChord(idx, editValue.trim() || 'C')
                    setEditingIdx(null)
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      if (idx >= 0) renameChord(idx, editValue.trim() || 'C')
                      setEditingIdx(null)
                    } else if (e.key === 'Escape') {
                      setEditingIdx(null)
                    }
                  }}
                  style={{
                    position: 'absolute',
                    left: 2,
                    right: 2,
                    top: 4,
                    height: 20,
                    fontSize: 12,
                  }}
                />
              ) : (
                <>
                  {chord ? `${chord.symbol}` : ''}
                  {chord && (
                    <ResizeHandle
                      zoom={zoom}
                      startLen={chord.len || 1}
                      onChange={(len) => {
                        dragIdx.current = idx
                        setChordLen(idx, len)
                      }}
                    />
                  )}
                </>
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}
