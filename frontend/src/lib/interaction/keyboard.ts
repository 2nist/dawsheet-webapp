export type KeyBinding = {
  key: string // e.g. 'Delete', 'ArrowLeft', 'ArrowRight'
  ctrl?: boolean
  alt?: boolean
  shift?: boolean
  meta?: boolean
  run: (e: KeyboardEvent) => void
}

export function attachKeymap(bindings: KeyBinding[]) {
  const onKey = (e: KeyboardEvent) => {
    // ignore when focused in inputs or editable content
    const el = e.target as HTMLElement | null
    const tag = el?.tagName?.toLowerCase()
    const editable = el && (el as any).isContentEditable
    if (tag === 'input' || tag === 'textarea' || editable) return
    for (const b of bindings) {
      if (
        e.key === b.key &&
        !!b.ctrl === (e.ctrlKey || e.metaKey) &&
        !!b.meta === e.metaKey &&
        !!b.alt === e.altKey &&
        !!b.shift === e.shiftKey
      ) {
        b.run(e)
        break
      }
    }
  }
  window.addEventListener('keydown', onKey)
  return () => window.removeEventListener('keydown', onKey)
}
