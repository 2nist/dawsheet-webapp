const KEYS = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb']

export function KeyField() {
  // no formal key in schema; reuse markers via title/artist for now? keep as placeholder toast
  return (
    <label style={{ display: 'block', marginBottom: 8 }}>
      Key (placeholder)
      <select disabled style={{ marginLeft: 8 }}>
        {KEYS.map((k) => (
          <option key={k} value={k}>
            {k}
          </option>
        ))}
      </select>
    </label>
  )
}
