import { useDrag } from './useDrag'
import { pxPerBeat } from '@/lib/units'

// Resize in beats along X axis, snapping to quarter-beat by default.
export function useResize(options: {
  zoom: number
  startLen: number
  onChange: (len: number) => void
  snap?: number // in beats, default 0.25
}) {
  const snap = options.snap ?? 0.25
  const ppb = pxPerBeat(options.zoom)
  return useDrag({
    onDrag: (dx) => {
      const dBeats = dx / ppb
      const snapped = Math.round(dBeats / snap) * snap
      const next = Math.max(snap, options.startLen + snapped)
      options.onChange(next)
    },
  })
}
