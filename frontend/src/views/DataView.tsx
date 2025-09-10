import { useState } from 'react'
import { useTimelineStore } from '@/lib/timelineStore'

export function DataPanel() {
  const [text, setText] = useState('')
  const issues = useTimelineStore((s) => s.issues)
  const loadFromText = useTimelineStore((s) => s.loadFromText)

  const onValidate = async () => {
    await loadFromText(text)
  }

  return (
    <div style={{ padding: 12, display: 'grid', gridTemplateColumns: '1fr 320px', gap: 12 }}>
      <div>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste .jrcd.json here"
          style={{
            width: '100%',
            minHeight: 260,
            fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
          }}
        />
        <div style={{ marginTop: 8 }}>
          <button onClick={onValidate} style={{ padding: '6px 10px' }}>
            Validate
          </button>
          <button style={{ padding: '6px 10px', marginLeft: 8 }} disabled>
            Fix overlaps (coming soon)
          </button>
        </div>
      </div>
      <aside style={{ borderLeft: '1px solid #eee', paddingLeft: 12 }}>
        <h3 style={{ marginTop: 0 }}>Issues</h3>
        {issues.length === 0 ? (
          <div style={{ color: '#666' }}>Paste JSON and click Validate to see results.</div>
        ) : (
          <ul>
            {issues.map((i, idx) => (
              <li key={idx}>
                <code>{i.path}</code>: {i.message}
              </li>
            ))}
          </ul>
        )}
      </aside>
    </div>
  )
}
