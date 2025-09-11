import { TimelineHeader } from '@/components/timeline/TimelineHeader'
import { SectionsLane } from '@/components/timeline/SectionsLane'
import { ChordsLane } from '@/components/timeline/ChordsLane'
import { LyricsLane } from '@/components/timeline/LyricsLane'
import { BarRuler } from '@/components/timeline/BarRuler'
import { InspectorPanel } from '@/components/timeline/InspectorPanel'
import { useTimelineStore } from '@/lib/timelineStore'
import { DataPanel } from '@/views/DataView'
import { ChordView } from '@/views/ChordView'
import { LyricView } from '@/views/LyricView'
import { ChordLyricView } from '@/views/ChordLyricView'
import { useEffect } from 'react'
import { attachKeymap } from '@/lib/interaction/keyboard'

export default function App() {
  const preset = useTimelineStore((s) => s.viewPreset)
  const snap = useTimelineStore((s) => s.snap)
  const setSnap = useTimelineStore((s) => s.setSnap)
  const selection = useTimelineStore((s) => s.selection)
  const deleteChord = useTimelineStore((s) => s.deleteChord)
  const deleteLyric = useTimelineStore((s) => s.deleteLyric)

  useEffect(() => {
    const detach = attachKeymap([
      {
        key: 'ArrowLeft',
        run: (e) => {
          e.preventDefault()
          // halve snap down to min 1/16
          const options = [4, 2, 1, 0.5, 0.25]
          const idx = options.findIndex((v) => Math.abs(v - snap) < 1e-6)
          if (idx >= 0 && idx < options.length - 1) setSnap(options[idx + 1])
        },
      },
      {
        key: 'ArrowRight',
        run: (e) => {
          e.preventDefault()
          // increase snap up to whole note
          const options = [0.25, 0.5, 1, 2, 4]
          const idx = options.findIndex((v) => Math.abs(v - snap) < 1e-6)
          if (idx >= 0 && idx < options.length - 1) setSnap(options[idx + 1])
        },
      },
      {
        key: 'Delete',
        run: (e) => {
          e.preventDefault()
          if (selection.eventKind === 'chords' && selection.eventIndex != null) {
            deleteChord(selection.eventIndex)
          } else if (selection.eventKind === 'lyrics' && selection.eventIndex != null) {
            deleteLyric(selection.eventIndex)
          }
        },
      },
    ])
    return detach
  }, [snap, setSnap, selection, deleteChord, deleteLyric])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <TimelineHeader />
      <div style={{ display: 'flex', flex: 1, minHeight: 0 }}>
        <main style={{ flex: 1, minWidth: 0 }}>
          <BarRuler />
          {preset === 'Timeline' && (
            <>
              <SectionsLane />
              <ChordsLane />
              <LyricsLane />
            </>
          )}
          {preset === 'Chord' && <ChordView />}
          {preset === 'Lyric' && <LyricView />}
          {preset === 'ChordLyric' && <ChordLyricView />}
          {preset === 'Data' && <DataPanel />}
        </main>
        <InspectorPanel />
      </div>
    </div>
  )
}
