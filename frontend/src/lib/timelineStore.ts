import { create, type StateCreator } from 'zustand'

export type ViewPreset = 'Timeline' | 'Chord' | 'Lyric' | 'ChordLyric' | 'Data'

export interface TimelineState {
  viewPreset: ViewPreset
  zoom: number
  snap: number
  // placeholder timeline doc; structure TBD
  doc: unknown
  issues: { path: string; message: string }[]
  setViewPreset: (v: ViewPreset) => void
  setZoom: (z: number) => void
  setSnap: (s: number) => void
  loadFromText: (
    text: string,
  ) => Promise<{ ok: boolean; issues: { path: string; message: string }[] }>
}

const creator: StateCreator<TimelineState> = (set) => ({
  viewPreset: 'Timeline',
  zoom: 1,
  snap: 1,
  doc: null,
  issues: [],
  setViewPreset: (v: ViewPreset) => set({ viewPreset: v }),
  setZoom: (zoom: number) => set({ zoom }),
  setSnap: (snap: number) => set({ snap }),
  loadFromText: async (text: string) => {
    try {
      const data = JSON.parse(text)
      // dynamic import to avoid circular
      const mod = await import('@/lib/validate')
      const res = mod.validateSong(data)
      set({ doc: res.doc ?? data, issues: res.issues })
      return { ok: res.ok, issues: res.issues }
    } catch (e: any) {
      const msg = e?.message ?? String(e)
      const issues = [{ path: '(root)', message: `JSON parse error: ${msg}` }]
      set({ doc: null, issues })
      return { ok: false, issues }
    }
  },
})

export const useTimelineStore = create<TimelineState>()(creator)
