export function SwingField() {
  // Not in schema; placeholder
  return (
    <label style={{ display: 'block', marginBottom: 8 }}>
      Swing % (placeholder)
      <input
        type="number"
        min={0}
        max={100}
        step={1}
        defaultValue={0}
        disabled
        style={{ marginLeft: 8, width: 80 }}
      />
    </label>
  )
}
