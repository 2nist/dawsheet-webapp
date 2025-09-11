import { useTimelineStore } from '@/lib/timelineStore'

export function LyricsLane() {
  const doc = useTimelineStore((s) => s.doc)
  const splitLyric = useTimelineStore((s) => s.splitLyric)
  const mergeLyricWithNext = useTimelineStore((s) => s.mergeLyricWithNext)
  return (
    <div style={{ borderBottom: '1px solid #eee' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '80px 1fr' }}>
        <div style={{ padding: '6px 8px', color: '#666' }}>Lyrics</div>
        <div style={{ padding: '6px 8px', display: 'grid', gap: 6 }}>
          {!doc || doc.lyrics.length === 0 ? (
            <div style={{ color: '#666' }}>No lyrics</div>
          ) : (
            doc.lyrics.map((l, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ color: '#666', minWidth: 80 }}>
                  t={l.t} len={l.len ?? 1}
                </span>
                <input type="text" value={l.text} readOnly style={{ flex: 1 }} />
                <button onClick={() => splitLyric(i)}>Split</button>
                <button onClick={() => mergeLyricWithNext(i)}>Merge →</button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
