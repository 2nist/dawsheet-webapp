import { useTimelineStore } from '@/lib/timelineStore'

const presets = ['Timeline', 'Chord', 'Lyric', 'ChordLyric', 'Data'] as const

export function TimelineHeader() {
  const viewPreset = useTimelineStore((s) => s.viewPreset)
  const setViewPreset = useTimelineStore((s) => s.setViewPreset)
  return (
    <header style={{ display: 'flex', gap: 8, padding: 12, borderBottom: '1px solid #ddd' }}>
      {presets.map((p) => (
        <button
          key={p}
          onClick={() => setViewPreset(p)}
          style={{
            padding: '6px 10px',
            borderRadius: 6,
            border: '1px solid #ccc',
            background: p === viewPreset ? '#eef' : 'white',
            cursor: 'pointer',
          }}
        >
          {p}
        </button>
      ))}
    </header>
  )
}
