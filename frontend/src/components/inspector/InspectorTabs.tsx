import { useEffect, useState } from 'react'

export type TabKey = 'Section' | 'Event' | 'Global'

export function InspectorTabs(props: {
  tabs?: TabKey[]
  initial?: TabKey
  active?: TabKey
  onChange?: (tab: TabKey) => void
}) {
  const tabs = props.tabs ?? ['Section', 'Event', 'Global']
  const [internal, setInternal] = useState<TabKey>(props.initial ?? tabs[0])
  const active = props.active ?? internal

  // Keep internal state in sync if initial changes and component is uncontrolled
  useEffect(() => {
    if (props.active === undefined && props.initial) {
      setInternal(props.initial)
    }
  }, [props.initial, props.active])
  return (
    <div>
      <div style={{ display: 'flex', gap: 6, marginBottom: 8 }}>
        {tabs.map((t) => (
          <button
            key={t}
            onClick={() => {
              if (props.active === undefined) setInternal(t)
              props.onChange?.(t)
            }}
            style={{
              padding: '6px 10px',
              border: '1px solid #ccc',
              borderRadius: 6,
              background: t === active ? '#eef' : 'white',
            }}
          >
            {t}
          </button>
        ))}
      </div>
      <div data-inspector-tab-active={active} />
    </div>
  )
}
