import { useTimelineStore } from '@/lib/timelineStore'

export function SectionsLane() {
  const doc = useTimelineStore((s) => s.doc)
  const updateSection = useTimelineStore((s) => s.updateSection)
  return (
    <div style={{ borderBottom: '1px solid #eee' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '80px 1fr' }}>
        <div style={{ padding: '6px 8px', color: '#666' }}>Sections</div>
        <div style={{ padding: '6px 8px', display: 'grid', gap: 6 }}>
          {!doc || doc.sections.length === 0 ? (
            <div style={{ color: '#666' }}>No sections</div>
          ) : (
            doc.sections.map((s, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <input
                  value={s.name}
                  onChange={(e) => updateSection({ name: e.target.value })}
                  style={{ flex: 1 }}
                />
                <span style={{ color: '#666' }}>
                  t={s.t} len={s.len}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
