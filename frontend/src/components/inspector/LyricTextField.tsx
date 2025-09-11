import { useTimelineStore } from '@/lib/timelineStore'

export function LyricTextField() {
  const selection = useTimelineStore((s) => s.selection)
  const doc = useTimelineStore((s) => s.doc)
  const updateEvent = useTimelineStore((s) => s.updateEvent)
  const value = (() => {
    if (!doc || selection.eventKind !== 'lyrics' || selection.eventIndex == null) return ''
    const ev = doc.lyrics[selection.eventIndex]
    return ev?.text ?? ''
  })()
  return (
    <label style={{ display: 'block', marginBottom: 8 }}>
      Lyric Text
      <input
        type="text"
        value={value}
        onChange={(e) => updateEvent('lyrics', { text: e.target.value })}
        style={{ marginLeft: 8, width: '100%' }}
      />
    </label>
  )
}
