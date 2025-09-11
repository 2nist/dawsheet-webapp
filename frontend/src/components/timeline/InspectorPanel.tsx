import { useEffect, useMemo, useState } from 'react'
import { useTimelineStore } from '@/lib/timelineStore'
import { InspectorTabs, type TabKey } from '@/components/inspector/InspectorTabs'
import { TempoField } from '@/components/inspector/TempoField'
import { KeyField } from '@/components/inspector/KeyField'
import { TimeSigField } from '@/components/inspector/TimeSigField'
import { SwingField } from '@/components/inspector/SwingField'
import { QuantizeField } from '@/components/inspector/QuantizeField'
import { ChordSymbolField } from '@/components/inspector/ChordSymbolField'
import { LyricTextField } from '@/components/inspector/LyricTextField'
import { SyllableTools } from '@/components/inspector/SyllableTools'
import { EuclidParams } from '@/components/inspector/EuclidParams'

export function InspectorPanel() {
  const doc = useTimelineStore((s) => s.doc)
  const selection = useTimelineStore((s) => s.selection)
  const updateSection = useTimelineStore((s) => s.updateSection)
  const setGlobal = useTimelineStore((s) => s.setGlobal)
  const updateEvent = useTimelineStore((s) => s.updateEvent)

  const [tab, setTab] = useState<TabKey>('Section')

  // Auto-switch tab based on selection
  useEffect(() => {
    if (selection.eventKind != null && selection.eventIndex != null) {
      setTab('Event')
    } else if (selection.sectionIndex != null) {
      setTab('Section')
    } else {
      setTab('Global')
    }
  }, [selection.eventKind, selection.eventIndex, selection.sectionIndex])

  const section = useMemo(() => {
    if (!doc || selection.sectionIndex == null) return null
    return doc.sections[selection.sectionIndex] ?? null
  }, [doc, selection.sectionIndex])

  const eventSummary = useMemo(() => {
    if (!doc || selection.eventKind == null || selection.eventIndex == null) return null
    const list = (doc as any)[selection.eventKind] as any[]
    const item = list?.[selection.eventIndex]
    return { kind: selection.eventKind, item }
  }, [doc, selection.eventKind, selection.eventIndex])

  return (
    <aside style={{ padding: 12, borderLeft: '1px solid #ddd', minWidth: 320 }}>
      <InspectorTabs initial={tab} active={tab} onChange={setTab} />

      {tab === 'Section' && (
        <div>
          <h4 style={{ marginTop: 8, marginBottom: 8 }}>Section</h4>
          {!section ? (
            <div style={{ color: '#666' }}>No section selected</div>
          ) : (
            <div style={{ display: 'grid', gap: 8 }}>
              <label>
                Name
                <input
                  type="text"
                  value={section.name}
                  onChange={(e) => updateSection({ name: e.target.value })}
                  style={{ marginLeft: 8, width: '100%' }}
                />
              </label>
              <label>
                Start (t)
                <input
                  type="number"
                  step={0.25}
                  value={section.t}
                  onChange={(e) => updateSection({ t: Number(e.target.value) })}
                  style={{ marginLeft: 8, width: 100 }}
                />
              </label>
              <label>
                Length (beats)
                <input
                  type="number"
                  step={0.25}
                  min={0}
                  value={section.len}
                  onChange={(e) => updateSection({ len: Number(e.target.value) })}
                  style={{ marginLeft: 8, width: 120 }}
                />
              </label>
            </div>
          )}
        </div>
      )}

      {tab === 'Event' && (
        <div>
          <h4 style={{ marginTop: 8, marginBottom: 8 }}>Event</h4>
          {!eventSummary ? (
            <div style={{ color: '#666' }}>No event selected</div>
          ) : (
            <div style={{ display: 'grid', gap: 8 }}>
              <label>
                Start (t)
                <input
                  type="number"
                  step={0.25}
                  value={eventSummary.item.t}
                  onChange={(e) => updateEvent(eventSummary.kind, { t: Number(e.target.value) })}
                  style={{ marginLeft: 8, width: 120 }}
                />
              </label>
              {'len' in eventSummary.item && (
                <label>
                  Length (beats)
                  <input
                    type="number"
                    step={0.25}
                    min={0}
                    value={eventSummary.item.len}
                    onChange={(e) =>
                      updateEvent(eventSummary.kind, { len: Number(e.target.value) })
                    }
                    style={{ marginLeft: 8, width: 120 }}
                  />
                </label>
              )}

              {eventSummary.kind === 'chords' && <ChordSymbolField />}
              {eventSummary.kind === 'lyrics' && (
                <>
                  <LyricTextField />
                  <SyllableTools />
                </>
              )}
              {eventSummary.kind === 'euclid' && <EuclidParams />}

              <div>
                <button
                  onClick={() =>
                    updateEvent(eventSummary.kind, eventSummary.item, { applyToSelection: true })
                  }
                >
                  Apply to selection
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {tab === 'Global' && (
        <div>
          <h4 style={{ marginTop: 8, marginBottom: 8 }}>Global</h4>
          <div style={{ display: 'grid', gap: 8 }}>
            <label>
              Title
              <input
                type="text"
                value={doc?.title ?? ''}
                onChange={(e) => setGlobal({ title: e.target.value })}
                style={{ marginLeft: 8, width: '100%' }}
              />
            </label>
            <label>
              Artist
              <input
                type="text"
                value={doc?.artist ?? ''}
                onChange={(e) => setGlobal({ artist: e.target.value })}
                style={{ marginLeft: 8, width: '100%' }}
              />
            </label>
            <TempoField />
            <KeyField />
            <TimeSigField />
            <SwingField />
            <QuantizeField />
            <button
              style={{ marginTop: 8 }}
              onClick={() => {
                const state = useTimelineStore.getState() as any
                const data = state.doc ?? {}
                const blob = new Blob([JSON.stringify(data, null, 2)], {
                  type: 'application/json',
                })
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = 'songdoc.jrcd.json'
                a.click()
                URL.revokeObjectURL(url)
              }}
            >
              Export
            </button>
          </div>
        </div>
      )}
    </aside>
  )
}
