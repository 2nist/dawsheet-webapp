import { TimelineHeader } from '@/components/timeline/TimelineHeader'
import { SectionsLane } from '@/components/timeline/SectionsLane'
import { ChordsLane } from '@/components/timeline/ChordsLane'
import { LyricsLane } from '@/components/timeline/LyricsLane'
import { SectionChordLyricChart } from '@/components/timeline/SectionChordLyricChart'
import { BarRuler } from '@/components/timeline/BarRuler'
import { InspectorPanel } from '@/components/timeline/InspectorPanel'
import { useTimelineStore } from '@/lib/timelineStore'

export default function App() {
  const preset = useTimelineStore((s) => s.viewPreset)

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
          {preset === 'Chord' && <ChordsLane />}
          {preset === 'Lyric' && <LyricsLane />}
          {preset === 'ChordLyric' && <SectionChordLyricChart />}
          {preset === 'Data' && (
            <div style={{ padding: 12 }}>Data view (placeholder)</div>
          )}
        </main>
        <InspectorPanel />
      </div>
    </div>
  )
}
