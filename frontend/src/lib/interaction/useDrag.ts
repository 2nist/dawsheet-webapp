import { useRef } from 'react'

type DragHandlers = {
  onDrag: (dx: number, dy: number, ev: MouseEvent) => void
  onEnd?: (ev: MouseEvent) => void
  button?: number // default 0 (left)
}

// Generic mouse drag hook. Attach returned props to a handle element.
export function useDrag(handlers: DragHandlers) {
  const start = useRef<{ x: number; y: number } | null>(null)

  const onMouseDown: React.MouseEventHandler<HTMLElement> = (e) => {
    if (handlers.button != null && e.button !== handlers.button) return
    e.preventDefault()
    start.current = { x: e.clientX, y: e.clientY }
    const onMove = (ev: MouseEvent) => {
      if (!start.current) return
      const dx = ev.clientX - start.current.x
      const dy = ev.clientY - start.current.y
      handlers.onDrag(dx, dy, ev)
    }
    const onUp = (ev: MouseEvent) => {
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
      handlers.onEnd?.(ev)
      start.current = null
    }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
  }

  return { onMouseDown }
}
