import { z } from 'zod'

export const MarkerEvent = z.object({
  t: z.number(), // beat
  label: z.string().optional(),
})

export const ChordEvent = z.object({
  t: z.number(), // start beat
  len: z.number().nonnegative(),
  symbol: z.string(),
})

export const LyricEvent = z.object({
  t: z.number(),
  len: z.number().nonnegative().optional(),
  text: z.string(),
})

export const EuclidEvent = z.object({
  t: z.number(),
  len: z.number().nonnegative(),
  k: z.number().int().nonnegative(),
  n: z.number().int().positive(),
})

export const Section = z.object({
  t: z.number(),
  len: z.number().nonnegative(),
  name: z.string(),
})

export const SongDoc = z.object({
  title: z.string().default('Untitled'),
  artist: z.string().default(''),
  bpm: z.number().positive().optional(),
  sections: z.array(Section).default([]),
  chords: z.array(ChordEvent).default([]),
  lyrics: z.array(LyricEvent).default([]),
  euclid: z.array(EuclidEvent).default([]),
  markers: z.array(MarkerEvent).default([]),
})

export type SongDoc = z.infer<typeof SongDoc>
export type Section = z.infer<typeof Section>
export type ChordEvent = z.infer<typeof ChordEvent>
export type LyricEvent = z.infer<typeof LyricEvent>
export type EuclidEvent = z.infer<typeof EuclidEvent>
export type MarkerEvent = z.infer<typeof MarkerEvent>
