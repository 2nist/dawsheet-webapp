import { useTimelineStore } from '@/lib/timelineStore'

export function LyricView() {
  const doc = useTimelineStore((s) => s.doc)
  const splitLyric = useTimelineStore((s) => s.splitLyric)
  const mergeLyricWithNext = useTimelineStore((s) => s.mergeLyricWithNext)

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 260px', gap: 12 }}>
      <main style={{ padding: 8 }}>
        {!doc || doc.lyrics.length === 0 ? (
          <div style={{ color: '#666' }}>No lyrics</div>
        ) : (
          <div style={{ display: 'grid', gap: 6 }}>
            {doc.lyrics.map((l, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div style={{ minWidth: 80, color: '#666' }}>
                  t={l.t} len={l.len ?? 1}
                </div>
                <input
                  type="text"
                  value={l.text}
                  onChange={() => {}}
                  readOnly
                  style={{ flex: 1 }}
                />
                <button onClick={() => splitLyric(i)}>Split</button>
                <button onClick={() => mergeLyricWithNext(i)}>Merge →</button>
              </div>
            ))}
          </div>
        )}
      </main>
      <aside style={{ borderLeft: '1px solid #eee', padding: 8 }}>
        <div style={{ fontWeight: 600, marginBottom: 6 }}>Karaoke Preview (stub)</div>
        <div
          style={{
            border: '1px solid #ddd',
            borderRadius: 6,
            padding: 8,
            minHeight: 120,
            background: 'linear-gradient(90deg, #fff 0%, #f3f4f6 100%)',
          }}
        >
          Highlights the current syllable when playhead moves (stub)
        </div>
      </aside>
    </div>
  )
}
