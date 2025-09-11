import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useTimelineStore } from '@/lib/timelineStore'

const presets = ['Timeline', 'Chord', 'Lyric', 'ChordLyric', 'Data'] as const

export function TimelineHeader() {
  const viewPreset = useTimelineStore((s) => s.viewPreset)
  const setViewPreset = useTimelineStore((s) => s.setViewPreset)
  const zoom = useTimelineStore((s) => s.zoom)
  const setZoom = useTimelineStore((s) => s.setZoom)
  const snap = useTimelineStore((s) => s.snap)
  const setSnap = useTimelineStore((s) => s.setSnap)
  const loadFromText = useTimelineStore((s) => s.loadFromText)

  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)
  const menuBtnRef = useRef<HTMLButtonElement>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  // Command palette state
  const [paletteOpen, setPaletteOpen] = useState(false)
  const [filter, setFilter] = useState('')

  // Simple toast impl
  const [toasts, setToasts] = useState<string[]>([])
  const toast = useCallback((msg: string) => {
    setToasts((t) => [...t, msg])
    setTimeout(() => setToasts((t) => t.slice(1)), 2500)
  }, [])

  const doExport = useCallback(() => {
    try {
      const state = useTimelineStore.getState() as any
      const data = state.doc ?? {}
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json',
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'songdoc.jrcd.json'
      a.click()
      URL.revokeObjectURL(url)
      toast('Exported JSON')
    } catch {
      toast('Export failed')
    }
  }, [toast])

  const actions = useMemo(
    () => [
      {
        id: 'import',
        label: 'Import .jrcd.json',
        run: () => fileRef.current?.click(),
      },
      {
        id: 'export',
        label: 'Export current JSON',
        run: () => doExport(),
      },
      {
        id: 'transpose',
        label: 'Transpose (placeholder)',
        run: () => toast('Transpose coming soon'),
      },
      {
        id: 'print',
        label: 'Print / Share (placeholder)',
        run: () => toast('Print/Share coming soon'),
      },
    ],
    [doExport, toast],
  )

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const isMod = navigator.platform.includes('Mac') ? e.metaKey : e.ctrlKey
      if (isMod && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        setPaletteOpen((v) => !v)
      }
      if (e.key === 'Escape') setPaletteOpen(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  const onFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    try {
      const text = await file.text()
      const res = await loadFromText(text)
      toast(res.ok ? 'Import validated' : `Import completed with ${res.issues.length} issues`)
    } catch (err: any) {
      toast('Import failed')
    } finally {
      e.target.value = ''
    }
  }

  // Close menu on outside click / Escape, and focus first item on open
  useEffect(() => {
    if (!menuOpen) return
    const onDown = (e: MouseEvent) => {
      const target = e.target as Node
      if (
        menuRef.current &&
        !menuRef.current.contains(target) &&
        menuBtnRef.current &&
        !menuBtnRef.current.contains(target)
      ) {
        setMenuOpen(false)
      }
    }
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setMenuOpen(false)
    }
    // focus first actionable item
    setTimeout(() => {
      const first = menuRef.current?.querySelector('button') as HTMLButtonElement | null
      first?.focus()
    }, 0)
    document.addEventListener('mousedown', onDown, true)
    window.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onDown, true)
      window.removeEventListener('keydown', onKey)
    }
  }, [menuOpen])

  return (
    <header
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        padding: 12,
        borderBottom: '1px solid #ddd',
        position: 'relative',
      }}
    >
      {/* Play/Stop stub */}
      <button title="Play" onClick={() => toast('Play (stub)')}>
        ▶
      </button>
      <button title="Stop" onClick={() => toast('Stop (stub)')}>
        ■
      </button>

      {/* Zoom */}
      <label style={{ marginLeft: 8 }}>
        Zoom
        <input
          type="range"
          min={0.25}
          max={4}
          step={0.25}
          value={zoom}
          onChange={(e) => setZoom(Number(e.target.value))}
          style={{ verticalAlign: 'middle', marginLeft: 6 }}
        />
      </label>

      {/* Snap/Quantize */}
      <label style={{ marginLeft: 8 }}>
        Snap
        <select
          value={snap}
          onChange={(e) => setSnap(Number(e.target.value))}
          style={{ marginLeft: 6 }}
        >
          <option value={1}>1</option>
          <option value={2}>1/2</option>
          <option value={4}>1/4</option>
          <option value={8}>1/8</option>
        </select>
      </label>

      {/* View Presets dropdown */}
      <label style={{ marginLeft: 8 }}>
        View
        <select
          value={viewPreset}
          onChange={(e) => setViewPreset(e.target.value as any)}
          style={{ marginLeft: 6 }}
        >
          {presets.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
      </label>

      <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8 }}>
        {/* Kebab menu */}
        <div style={{ position: 'relative' }}>
          <button
            ref={menuBtnRef}
            aria-haspopup="menu"
            aria-expanded={menuOpen}
            aria-label="Quick Actions"
            onClick={() => setMenuOpen((v) => !v)}
          >
            ⋮
          </button>
          {menuOpen && (
            <div
              ref={menuRef}
              style={{
                position: 'absolute',
                right: 0,
                top: '100%',
                background: 'white',
                border: '1px solid #ddd',
                borderRadius: 6,
                boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                padding: 6,
                zIndex: 20,
              }}
            >
              <button
                onClick={() => fileRef.current?.click()}
                style={{ display: 'block', width: '100%', textAlign: 'left', padding: '6px 10px' }}
              >
                Import .jrcd.json
              </button>
              <button
                onClick={doExport}
                style={{ display: 'block', width: '100%', textAlign: 'left', padding: '6px 10px' }}
              >
                Export
              </button>
              <button
                onClick={() => toast('Transpose coming soon')}
                style={{ display: 'block', width: '100%', textAlign: 'left', padding: '6px 10px' }}
              >
                Transpose…
              </button>
              <button
                onClick={() => toast('Print/Share coming soon')}
                style={{ display: 'block', width: '100%', textAlign: 'left', padding: '6px 10px' }}
              >
                Print / Share…
              </button>
            </div>
          )}
        </div>
      </div>

      {/* hidden file input */}
      <input
        ref={fileRef}
        type="file"
        accept="application/json,.json"
        onChange={onFile}
        style={{ display: 'none' }}
      />

      {/* Command palette */}
      {paletteOpen && (
        <div
          style={{
            position: 'absolute',
            left: '50%',
            top: 8,
            transform: 'translateX(-50%)',
            width: 480,
            background: 'white',
            border: '1px solid #ddd',
            borderRadius: 8,
            boxShadow: '0 12px 28px rgba(0,0,0,0.15)',
            zIndex: 50,
          }}
        >
          <input
            autoFocus
            placeholder="Type a command…"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            style={{
              width: '100%',
              boxSizing: 'border-box',
              padding: 10,
              border: 0,
              borderBottom: '1px solid #eee',
              outline: 'none',
            }}
          />
          <div style={{ maxHeight: 280, overflow: 'auto', padding: 6 }}>
            {actions
              .filter((a) => a.label.toLowerCase().includes(filter.toLowerCase()))
              .map((a) => (
                <div key={a.id}>
                  <button
                    onClick={() => {
                      a.run()
                      setPaletteOpen(false)
                    }}
                    style={{ width: '100%', textAlign: 'left', padding: '8px 10px' }}
                  >
                    {a.label}
                  </button>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Toasts */}
      <div
        style={{ position: 'fixed', right: 12, bottom: 12, display: 'grid', gap: 8, zIndex: 100 }}
      >
        {toasts.map((t, i) => (
          <div
            key={i}
            style={{
              background: '#333',
              color: 'white',
              padding: '8px 12px',
              borderRadius: 6,
              opacity: 0.95,
            }}
          >
            {t}
          </div>
        ))}
      </div>
    </header>
  )
}
