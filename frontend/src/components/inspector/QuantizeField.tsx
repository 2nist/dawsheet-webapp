import { useTimelineStore } from '@/lib/timelineStore'

export function QuantizeField() {
  const snap = useTimelineStore((s) => s.snap)
  const setSnap = useTimelineStore((s) => s.setSnap)
  return (
    <label style={{ display: 'block', marginBottom: 8 }}>
      Quantize
      <select
        value={snap}
        onChange={(e) => setSnap(Number(e.target.value))}
        style={{ marginLeft: 8 }}
      >
        <option value={1}>1</option>
        <option value={2}>1/2</option>
        <option value={4}>1/4</option>
        <option value={8}>1/8</option>
      </select>
    </label>
  )
}
