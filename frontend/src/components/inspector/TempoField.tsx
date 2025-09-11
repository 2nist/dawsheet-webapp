import { useTimelineStore } from '@/lib/timelineStore'

export function TempoField() {
  const bpm = useTimelineStore((s) => s.doc?.bpm ?? 120)
  const setGlobal = useTimelineStore((s) => s.setGlobal)
  return (
    <label style={{ display: 'block', marginBottom: 8 }}>
      Tempo (BPM)
      <input
        type="number"
        min={1}
        step={1}
        value={bpm}
        onChange={(e) => setGlobal({ bpm: Number(e.target.value) || undefined })}
        style={{ marginLeft: 8, width: 100 }}
      />
    </label>
  )
}
