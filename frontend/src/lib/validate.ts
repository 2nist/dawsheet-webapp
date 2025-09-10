import { SongDoc as SongDocSchema } from './schema'

export type Issue = {
  path: string
  message: string
}

export function validateSong(input: unknown): { ok: boolean; doc?: any; issues: Issue[] } {
  const issues: Issue[] = []

  // Capture unknown fields by deep traversal against schema shape keys
  const shapeKeys = new Set([
    'title',
    'artist',
    'bpm',
    'sections',
    'chords',
    'lyrics',
    'euclid',
    'markers',
  ])

  if (input && typeof input === 'object') {
    for (const key of Object.keys(input as Record<string, unknown>)) {
      if (!shapeKeys.has(key)) {
        issues.push({ path: key, message: `Unknown top-level field: ${key}` })
      }
    }
  }

  const parsed = SongDocSchema.safeParse(input)
  if (!parsed.success) {
    for (const e of parsed.error.issues) {
      issues.push({ path: e.path.join('.') || '(root)', message: e.message })
    }
    return { ok: false, issues }
  }

  const doc = parsed.data

  // Lints: negative length already guarded by schema, but double-check
  const checkNegLen = (arr: Array<{ len?: number }>, path: string) => {
    arr.forEach((e, i) => {
      if (e.len != null && e.len < 0) {
        issues.push({ path: `${path}[${i}].len`, message: 'Negative length' })
      }
    })
  }
  checkNegLen(doc.sections, 'sections')
  checkNegLen(doc.chords, 'chords')
  checkNegLen(doc.lyrics, 'lyrics')
  checkNegLen(doc.euclid, 'euclid')

  // Overlaps within same kind (based on t and len)
  const hasOverlap = (arr: Array<{ t: number; len?: number }>) => {
    const sorted = [...arr].sort((a, b) => a.t - b.t)
    for (let i = 0; i < sorted.length - 1; i++) {
      const a = sorted[i]
      const b = sorted[i + 1]
      const aEnd = a.t + (a.len ?? 0)
      if (a.len != null && aEnd > b.t) return true
    }
    return false
  }

  if (hasOverlap(doc.chords)) issues.push({ path: 'chords', message: 'Chord overlaps detected' })
  if (hasOverlap(doc.lyrics)) issues.push({ path: 'lyrics', message: 'Lyric overlaps detected' })
  if (hasOverlap(doc.euclid)) issues.push({ path: 'euclid', message: 'Euclid overlaps detected' })
  if (hasOverlap(doc.sections)) issues.push({ path: 'sections', message: 'Section overlaps detected' })

  // Non-contiguous sections (gaps) – check if next.t === prev.t + prev.len
  const secs = [...doc.sections].sort((a, b) => a.t - b.t)
  for (let i = 0; i < secs.length - 1; i++) {
    const a = secs[i]
    const b = secs[i + 1]
    const aEnd = a.t + a.len
    if (aEnd !== b.t) {
      issues.push({ path: `sections[${i+1}].t`, message: `Non-contiguous sections: prev ends at ${aEnd}, next starts at ${b.t}` })
    }
  }

  return { ok: issues.length === 0, doc, issues }
}
