export default function DesignTokens() {
  return (
    <main style={{ padding: 24 }}>
      <h1>Design Tokens</h1>
      <section
        style={{
          display: "grid",
          gap: 12,
          gridTemplateColumns: "repeat(auto-fill, minmax(180px,1fr))",
          marginTop: 16,
        }}
      >
        {[
          ["bg", "Background", "var(--bg)"],
          ["fg", "Foreground", "var(--fg)"],
          ["primary", "Primary", "var(--primary)"],
          ["secondary", "Secondary", "var(--secondary)"],
          ["muted", "Muted", "var(--muted)"],
          ["border", "Border", "var(--border)"],
          ["cream", "Cream", "var(--cream)"],
        ].map(([key, label, cssVar]) => (
          <div key={key} className="card">
            <div
              style={{
                height: 56,
                borderRadius: "var(--radius)",
                background: String(cssVar),
              }}
            />
            <div style={{ marginTop: 8, color: "var(--muted)" }}>{label}</div>
            <code style={{ fontFamily: "var(--font-mono)", fontSize: 12 }}>
              {String(cssVar)}
            </code>
          </div>
        ))}
      </section>
      <section style={{ marginTop: 24 }}>
        <h2>Typography</h2>
        <p style={{ fontFamily: "var(--font-sans)" }}>
          Body text using --font-sans.
        </p>
        <pre
          className="card"
          style={{ fontFamily: "var(--font-mono)", padding: 12 }}
        >
          Monospace preview using --font-mono.
        </pre>
      </section>
      <section style={{ marginTop: 24 }}>
        <h2>Radius & Shadow</h2>
        <div
          className="card"
          style={{ borderRadius: "var(--radius)", boxShadow: "var(--shadow)" }}
        >
          Card with --radius and --shadow
        </div>
      </section>
    </main>
  );
}
