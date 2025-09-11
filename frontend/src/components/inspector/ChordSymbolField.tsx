import { parseChordSymbol } from '@/lib/harmony'
import { useTimelineStore } from '@/lib/timelineStore'

export function ChordSymbolField() {
  const selection = useTimelineStore((s) => s.selection)
  const doc = useTimelineStore((s) => s.doc)
  const updateEvent = useTimelineStore((s) => s.updateEvent)
  const value = (() => {
    if (!doc || selection.eventKind !== 'chords' || selection.eventIndex == null) return ''
    const ev = doc.chords[selection.eventIndex]
    return ev?.symbol ?? ''
  })()
  return (
    <label style={{ display: 'block', marginBottom: 8 }}>
      Chord Symbol
      <input
        type="text"
        value={value}
        onChange={(e) => updateEvent('chords', { symbol: e.target.value })}
        style={{ marginLeft: 8, width: '100%' }}
      />
      <small style={{ display: 'block', color: '#666' }}>
        Parsed: {value ? JSON.stringify(parseChordSymbol(value)) : '(n/a)'}
      </small>
      <label style={{ display: 'block', marginTop: 6 }}>
        <input
          type="checkbox"
          onChange={() => {
            /* placeholder */
          }}
        />{' '}
        Roman numerals
      </label>
    </label>
  )
}
