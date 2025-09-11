import { useTimelineStore } from '@/lib/timelineStore'

export function EuclidParams() {
  const selection = useTimelineStore((s) => s.selection)
  const doc = useTimelineStore((s) => s.doc)
  const updateEvent = useTimelineStore((s) => s.updateEvent)
  const vals = (() => {
    if (!doc || selection.eventKind !== 'euclid' || selection.eventIndex == null)
      return { n: 16, k: 4, len: 1 }
    const ev = doc.euclid[selection.eventIndex]
    return { n: ev.n, k: ev.k, len: ev.len }
  })()
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
      <label>
        Steps (n)
        <input
          type="number"
          min={1}
          step={1}
          value={vals.n}
          onChange={(e) => updateEvent('euclid', { n: Number(e.target.value) })}
          style={{ marginLeft: 8, width: 80 }}
        />
      </label>
      <label>
        Pulses (k)
        <input
          type="number"
          min={0}
          step={1}
          value={vals.k}
          onChange={(e) => updateEvent('euclid', { k: Number(e.target.value) })}
          style={{ marginLeft: 8, width: 80 }}
        />
      </label>
      <label>
        Length (beats)
        <input
          type="number"
          min={0}
          step={0.25}
          value={vals.len}
          onChange={(e) => updateEvent('euclid', { len: Number(e.target.value) })}
          style={{ marginLeft: 8, width: 100 }}
        />
      </label>
    </div>
  )
}
