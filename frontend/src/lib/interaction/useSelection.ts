import { useState } from 'react'

// Minimal single-index selection hook. Extend later for ranges and multi-select.
export function useSelection(initial: number | null = null) {
  const [selected, setSelected] = useState<number | null>(initial)
  const isSelected = (i: number) => selected === i
  return { selected, setSelected, isSelected }
}
