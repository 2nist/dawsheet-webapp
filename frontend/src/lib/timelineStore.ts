import { create, type StateCreator } from 'zustand'
import type {
  SongDoc,
  Section as SectionT,
  ChordEvent as ChordT,
  LyricEvent as LyricT,
  EuclidEvent as EuclidT,
} from '@/lib/schema'

export type ViewPreset = 'Timeline' | 'Chord' | 'Lyric' | 'ChordLyric' | 'Data'

export interface TimelineState {
  viewPreset: ViewPreset
  zoom: number
  snap: number
  // validated song doc
  doc: SongDoc | null
  issues: { path: string; message: string }[]
  // selection model: section index and first selected event by kind
  selection: {
    sectionIndex: number | null
    eventKind: 'chords' | 'lyrics' | 'euclid' | null
    eventIndex: number | null
  }
  setViewPreset: (v: ViewPreset) => void
  setZoom: (z: number) => void
  setSnap: (s: number) => void
  loadFromText: (
    text: string,
  ) => Promise<{ ok: boolean; issues: { path: string; message: string }[] }>
  // reducers for inspector
  setSelection: (sel: Partial<TimelineState['selection']>) => void
  updateSection: (patch: Partial<SectionT>) => void
  updateEvent: (
    kind: 'chords' | 'lyrics' | 'euclid',
    patch: Partial<ChordT & LyricT & EuclidT>,
    options?: { applyToSelection?: boolean },
  ) => void
  setGlobal: (patch: Partial<Pick<SongDoc, 'title' | 'artist' | 'bpm'>>) => void
  // view helpers
  upsertChordAt: (beat: number, symbol: string, len?: number) => void
  setChordLen: (index: number, len: number) => void
  renameChord: (index: number, symbol: string) => void
  splitChord: (index: number) => void
  splitLyric: (index: number) => void
  mergeLyricWithNext: (index: number) => void
  mergeChordWithNext: (index: number) => void
  deleteChord: (index: number) => void
  deleteLyric: (index: number) => void
}

const safeGet = (key: string) => {
  try {
    if (typeof window === 'undefined') return null
    return window.localStorage.getItem(key)
  } catch {
    return null
  }
}

const creator: StateCreator<TimelineState> = (set) => ({
  viewPreset: (safeGet('viewPreset') as ViewPreset) || 'Timeline',
  zoom: 1,
  snap: 1,
  doc: null,
  issues: [],
  selection: { sectionIndex: null, eventKind: null, eventIndex: null },
  setViewPreset: (v: ViewPreset) => {
    try {
      if (typeof window !== 'undefined') window.localStorage.setItem('viewPreset', v)
    } catch {}
    set({ viewPreset: v })
  },
  setZoom: (zoom: number) => set({ zoom }),
  setSnap: (snap: number) => set({ snap }),
  loadFromText: async (text: string) => {
    try {
      const data = JSON.parse(text)
      // dynamic import to avoid circular
      const mod = await import('@/lib/validate')
      const res = mod.validateSong(data)
      const doc = (res.doc ?? (data as SongDoc)) as SongDoc
      // initialize selection to first section if present
      const sectionIndex = doc.sections.length ? 0 : null
      set({
        doc,
        issues: res.issues,
        selection: { sectionIndex, eventKind: null, eventIndex: null },
      })
      return { ok: res.ok, issues: res.issues }
    } catch (e: any) {
      const msg = e?.message ?? String(e)
      const issues = [{ path: '(root)', message: `JSON parse error: ${msg}` }]
      set({
        doc: null,
        issues,
        selection: { sectionIndex: null, eventKind: null, eventIndex: null },
      })
      return { ok: false, issues }
    }
  },
  setSelection: (sel) => set((s) => ({ selection: { ...s.selection, ...sel } })),
  updateSection: (patch) =>
    set((s) => {
      if (!s.doc || s.selection.sectionIndex == null) return s
      const i = s.selection.sectionIndex
      if (i < 0 || i >= s.doc.sections.length) return s
      const nextSections = s.doc.sections.slice()
      nextSections[i] = { ...nextSections[i], ...patch }
      return { ...s, doc: { ...s.doc, sections: nextSections } }
    }),
  updateEvent: (kind, patch, options) =>
    set((s) => {
      if (!s.doc) return s
      const applyToSelection = options?.applyToSelection ?? false
      const kinds = ['chords', 'lyrics', 'euclid'] as const
      if (!kinds.includes(kind as any)) return s
      const list = (s.doc as any)[kind] as Array<any>
      if (!Array.isArray(list) || !list.length) return s
      let indices: number[] = []
      if (applyToSelection && s.selection.eventKind === kind && s.selection.eventIndex != null) {
        indices = [s.selection.eventIndex]
      } else if (s.selection.eventKind === kind && s.selection.eventIndex != null) {
        indices = [s.selection.eventIndex]
      } else {
        indices = [0]
      }
      const nextList = list.slice()
      for (const idx of indices) {
        if (idx < 0 || idx >= nextList.length) continue
        nextList[idx] = { ...nextList[idx], ...patch }
      }
      return { ...s, doc: { ...(s.doc as SongDoc), [kind]: nextList } as SongDoc }
    }),
  setGlobal: (patch) => set((s) => ({ doc: s.doc ? { ...s.doc, ...patch } : s.doc })),
  upsertChordAt: (beat, symbol, len = 1) =>
    set((s) => {
      if (!s.doc) return s
      const list = s.doc.chords.slice()
      const idx = list.findIndex((c) => c.t === beat)
      if (idx >= 0) list[idx] = { ...list[idx], symbol, len: list[idx].len || len }
      else list.push({ t: beat, len, symbol })
      list.sort((a, b) => a.t - b.t)
      return { ...s, doc: { ...(s.doc as SongDoc), chords: list } as SongDoc }
    }),
  setChordLen: (index, len) =>
    set((s) => {
      if (!s.doc) return s
      const list = s.doc.chords.slice()
      if (index < 0 || index >= list.length) return s
      const clamped = Math.max(0.25, Number.isFinite(len) ? len : 0.25)
      list[index] = { ...list[index], len: clamped }
      return { ...s, doc: { ...(s.doc as SongDoc), chords: list } as SongDoc }
    }),
  renameChord: (index, symbol) =>
    set((s) => {
      if (!s.doc) return s
      const list = s.doc.chords.slice()
      if (index < 0 || index >= list.length) return s
      list[index] = { ...list[index], symbol }
      return { ...s, doc: { ...(s.doc as SongDoc), chords: list } as SongDoc }
    }),
  splitChord: (index) =>
    set((s) => {
      if (!s.doc) return s
      const list = s.doc.chords.slice()
      if (index < 0 || index >= list.length) return s
      const it = list[index]
      const len = Math.max(0.25, (it.len ?? 1) / 2)
      const a = { ...it, len }
      const b = { t: it.t + len, len, symbol: it.symbol }
      list.splice(index, 1, a, b)
      return { ...s, doc: { ...(s.doc as SongDoc), chords: list } as SongDoc }
    }),
  splitLyric: (index) =>
    set((s) => {
      if (!s.doc) return s
      const list = s.doc.lyrics.slice()
      if (index < 0 || index >= list.length) return s
      const it = list[index]
      const text = it.text
      const parts = text.split(/\s+/).filter(Boolean)
      if (parts.length <= 1) return s
      const len = Math.max(0.25, (it.len ?? 1) / parts.length)
      // build syllables
      const news: typeof list = []
      let cursor = it.t
      for (const p of parts) {
        news.push({ t: cursor, len, text: p })
        cursor += len
      }
      // replace in list
      list.splice(index, 1, ...news)
      return { ...s, doc: { ...(s.doc as SongDoc), lyrics: list } as SongDoc }
    }),
  mergeLyricWithNext: (index) =>
    set((s) => {
      if (!s.doc) return s
      const list = s.doc.lyrics.slice()
      if (index < 0 || index + 1 >= list.length) return s
      const a = list[index]
      const b = list[index + 1]
      const text = `${a.text} ${b.text}`.replace(/\s+/g, ' ').trim()
      const len = (a.len ?? 1) + (b.len ?? 1)
      list.splice(index, 2, { t: a.t, len, text })
      return { ...s, doc: { ...(s.doc as SongDoc), lyrics: list } as SongDoc }
    }),
  mergeChordWithNext: (index) =>
    set((s) => {
      if (!s.doc) return s
      const list = s.doc.chords.slice()
      if (index < 0 || index + 1 >= list.length) return s
      const a = list[index]
      const b = list[index + 1]
      const len = (a.len ?? 1) + (b.len ?? 1)
      // keep first symbol
      list.splice(index, 2, { t: a.t, len, symbol: a.symbol })
      return { ...s, doc: { ...(s.doc as SongDoc), chords: list } as SongDoc }
    }),
  deleteChord: (index) =>
    set((s) => {
      if (!s.doc) return s
      const list = s.doc.chords.slice()
      if (index < 0 || index >= list.length) return s
      list.splice(index, 1)
      return {
        ...s,
        doc: { ...(s.doc as SongDoc), chords: list } as SongDoc,
        selection: { ...s.selection, eventIndex: null },
      }
    }),
  deleteLyric: (index) =>
    set((s) => {
      if (!s.doc) return s
      const list = s.doc.lyrics.slice()
      if (index < 0 || index >= list.length) return s
      list.splice(index, 1)
      return {
        ...s,
        doc: { ...(s.doc as SongDoc), lyrics: list } as SongDoc,
        selection: { ...s.selection, eventIndex: null },
      }
    }),
})

export const useTimelineStore = create<TimelineState>()(creator)
