export function TimeSigField() {
  // Not in schema yet; placeholder only
  return (
    <label style={{ display: 'block', marginBottom: 8 }}>
      Time Signature (placeholder)
      <select disabled style={{ marginLeft: 8 }}>
        <option value="4/4">4/4</option>
        <option value="3/4">3/4</option>
        <option value="6/8">6/8</option>
      </select>
    </label>
  )
}
