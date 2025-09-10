import { create, type StateCreator } from 'zustand'

export type ViewPreset = 'Timeline' | 'Chord' | 'Lyric' | 'ChordLyric' | 'Data'

export interface TimelineState {
  viewPreset: ViewPreset
  zoom: number
  snap: number
  // placeholder timeline doc; structure TBD
  doc: unknown
  setViewPreset: (v: ViewPreset) => void
  setZoom: (z: number) => void
  setSnap: (s: number) => void
}

const creator: StateCreator<TimelineState> = (set) => ({
  viewPreset: 'Timeline',
  zoom: 1,
  snap: 1,
  doc: null,
  setViewPreset: (v: ViewPreset) => set({ viewPreset: v }),
  setZoom: (zoom: number) => set({ zoom }),
  setSnap: (snap: number) => set({ snap }),
})

export const useTimelineStore = create<TimelineState>()(creator)
