import { useState } from 'react'

export default function LegacyPage() {
  const [ping, setPing] = useState<string>('')
  const [text, setText] = useState<string>('Hello\nWorld')
  const [parsed, setParsed] = useState<number | null>(null)
  const [sample, setSample] = useState<string[]>([])

  const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

  const doPing = async () => {
    const res = await fetch(`${apiBase}/legacy/ping`)
    const j = await res.json()
    setPing(JSON.stringify(j))
  }

  const doParse = async () => {
    const res = await fetch(`${apiBase}/legacy/lyrics/parse`, {
      method: 'POST',
      headers: { 'content-type': 'text/plain' },
      body: text,
    })
  const j = await res.json()
  const lines = Array.isArray(j?.lines) ? j.lines : []
  setParsed(lines.length)
  setSample(lines.slice(0, 10).map((l: any) => l?.text ?? ''))
  }

  return (
    <div style={{ padding: 16 }}>
      <h1>Legacy</h1>
      <div style={{ marginBottom: 12 }}>
        <button onClick={doPing}>Ping legacy</button>
        <div><small>{ping}</small></div>
      </div>
      <div>
        <textarea value={text} onChange={e => setText(e.target.value)} rows={6} cols={60} />
        <div>
          <button onClick={doParse}>Parse</button>
          {parsed !== null && <div>Lines parsed: {parsed}</div>}
          {parsed !== null && parsed > 0 && (
            <ul>
              {sample.map((t, i) => (
                <li key={i}>{i + 1}. {t}</li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}
