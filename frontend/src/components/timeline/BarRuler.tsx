import { useMemo } from 'react'
import { useTimelineStore } from '@/lib/timelineStore'
import { DEFAULT_TS, beatsPerBar, pxPerBeat } from '@/lib/units'

export function BarRuler() {
  const doc = useTimelineStore((s) => s.doc)
  const zoom = useTimelineStore((s) => s.zoom)
  const totalBeats = useMemo(() => doc?.sections.reduce((a, s) => a + s.len, 0) ?? 32, [doc])
  const ts = DEFAULT_TS
  const bpb = beatsPerBar(ts)
  const bars = Math.max(1, Math.ceil(totalBeats / bpb))
  const beatPx = Math.max(12, Math.round(pxPerBeat(zoom)))

  return (
    <div style={{ overflowX: 'auto', borderBottom: '1px solid #eee' }}>
      <div style={{ display: 'grid', gridTemplateColumns: `80px repeat(${bars}, 1fr)` }}>
        <div style={{ padding: '6px 8px', color: '#666' }}>Bars</div>
        {Array.from({ length: bars }).map((_, bar) => (
          <div key={bar} style={{ borderLeft: '1px solid #eee' }}>
            <div style={{ padding: '6px 8px', color: '#374151', background: '#f9fafb' }}>
              {bar + 1}
            </div>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: `repeat(${bpb}, ${beatPx}px)`,
              }}
            >
              {Array.from({ length: bpb }).map((__, i) => (
                <div key={i} style={{ borderLeft: '1px solid #f0f0f0', height: 6 }} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
