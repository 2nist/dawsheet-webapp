export default function DesignPage() {
  return <main style={{ padding: 24 }}>Design</main>;
}

type TokenMap = Record<TokenName, string>;

const hex = (v: string) => {
  const s = v.trim();
  // If it's already hex or named color, return as-is
  if (s.startsWith("#") || /^[a-zA-Z]+$/.test(s)) return s;
  return s; // Keep raw (e.g., rgba/oklab supported by browser)
};

function parsePx(value: string): number {
  const n = parseFloat(String(value).replace("px", "").trim());
  return Number.isFinite(n) ? n : 0;
}

function toPx(n: number): string {
  return `${Math.max(0, Math.round(n))}px`;
}

// WCAG contrast helpers
function srgbToLinear(c: number) {
  const cs = c / 255;
  return cs <= 0.03928 ? cs / 12.92 : Math.pow((cs + 0.055) / 1.055, 2.4);
}
function hexToRgb(h: string): [number, number, number] | null {
  const s = h.trim();
  if (!s.startsWith("#")) return null;
  const p = s.slice(1);
  const isShort = p.length === 3 || p.length === 4;
  const r = isShort ? parseInt(p[0] + p[0], 16) : parseInt(p.slice(0, 2), 16);
  const g = isShort ? parseInt(p[1] + p[1], 16) : parseInt(p.slice(2, 4), 16);
  const b = isShort ? parseInt(p[2] + p[2], 16) : parseInt(p.slice(4, 6), 16);
  if ([r, g, b].some((x) => Number.isNaN(x))) return null;
  return [r, g, b];
}
function luminanceFromHex(h: string): number | null {
  const rgb = hexToRgb(h);
  if (!rgb) return null;
  const [r, g, b] = rgb.map((v) => srgbToLinear(v)) as unknown as [
    number,
    number,
    number
  ];
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
function contrastRatio(hexA: string, hexB: string): number | null {
  const La = luminanceFromHex(hexA);
  const Lb = luminanceFromHex(hexB);
  if (La == null || Lb == null) return null;
  const L1 = Math.max(La, Lb) + 0.05;
  const L2 = Math.min(La, Lb) + 0.05;
  return +(L1 / L2).toFixed(2);
}

export default function DesignPage() {
  const [tokens, setTokens] = useState<TokenMap>({} as TokenMap);
  const [loaded, setLoaded] = useState(false);
  const [bgChoice, setBgChoice] = useState<TokenName>("--bg");
  const [fgChoice, setFgChoice] = useState<TokenName>("--fg");
  const [modalOpen, setModalOpen] = useState(false);
  const [modalToken, setModalToken] = useState<TokenName | null>(null);
  const [hsl, setHsl] = useState<{ h: number; s: number; l: number }>({
    h: 160,
    s: 50,
    l: 50,
  });

  function rgbToHsl(r: number, g: number, b: number) {
    r /= 255;
    g /= 255;
    b /= 255;
    const max = Math.max(r, g, b),
      min = Math.min(r, g, b);
    let h = 0,
      s = 0,
      l = (max + min) / 2;
    if (max !== min) {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      switch (max) {
        case r:
          h = (g - b) / d + (g < b ? 6 : 0);
          break;
        case g:
          h = (b - r) / d + 2;
          break;
        case b:
          h = (r - g) / d + 4;
          break;
      }
      h /= 6;
    }
    return {
      h: Math.round(h * 360),
      s: Math.round(s * 100),
      l: Math.round(l * 100),
    };
  }

  function hexToHsl(hex: string) {
    const rgb = hexToRgb(hex);
    if (!rgb) return { h: 0, s: 0, l: 0 };
    const { h, s, l } = rgbToHsl(rgb[0], rgb[1], rgb[2]);
    return { h, s, l };
  }

  function hslToCss({ h, s, l }: { h: number; s: number; l: number }) {
    return `hsl(${Math.round(h)}, ${Math.round(s)}%, ${Math.round(l)}%)`;
  }

  function openHslModal(token: TokenName) {
    setModalToken(token);
    const currentHex = resolveVarToHex(token);
    setHsl(hexToHsl(currentHex));
    setModalOpen(true);
  }

  function applyHsl() {
    if (!modalToken) return;
    updateToken(modalToken, hslToCss(hsl));
    setModalOpen(false);
  }

  // Load from computed styles + localStorage overrides
  useEffect(() => {
    const root = document.documentElement;
    const initial: Partial<TokenMap> = {};
    const all = [
      ...COLOR_TOKENS,
      ...RADIUS_TOKENS,
      ...SPACING_TOKENS,
      ...FONT_TOKENS,
      ...SHADOW_TOKENS,
    ];
    all.forEach((k) => {
      initial[k] = getComputedStyle(root).getPropertyValue(k).trim();
    });
    try {
      const stored = window.localStorage.getItem("tokens");
      if (stored) {
        const parsed = JSON.parse(stored) as Partial<TokenMap>;
        Object.entries(parsed).forEach(([k, v]) => {
          if (v != null) {
            root.style.setProperty(k, v as string);
            (initial as any)[k] = v as string;
          }
        });
      }
    } catch {}
    setTokens(initial as TokenMap);
    setLoaded(true);
  }, []);

  const updateToken = (key: TokenName, value: string) => {
    const root = document.documentElement;
    root.style.setProperty(key, value);
    const next = { ...tokens, [key]: value } as TokenMap;
    setTokens(next);
    window.localStorage.setItem("tokens", JSON.stringify(next));
  };

  // Convert any CSS color (e.g., rgb(), oklab(), named) into #rrggbb for <input type="color">
  function cssColorToHex(input: string): string | null {
    const s = (input || "").trim();
    if (!s) return null;
    if (s.startsWith("#")) {
      // Normalize to #rrggbb if short
      const hex = s.replace(/[^#0-9a-fA-F]/g, "");
      if (hex.length === 4) {
        const r = hex[1];
        const g = hex[2];
        const b = hex[3];
        return `#${r}${r}${g}${g}${b}${b}`.toLowerCase();
      }
      return hex.length >= 7 ? hex.slice(0, 7).toLowerCase() : null;
    }
    // Use a temporary element to let the browser parse the color
    if (typeof window === "undefined") return null;
    const el = document.createElement("div");
    el.style.color = s;
    document.body.appendChild(el);
    const computed = getComputedStyle(el).color; // rgb(a)
    document.body.removeChild(el);
    const m = computed.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/i);
    if (!m) return null;
    const r = Math.max(0, Math.min(255, parseInt(m[1], 10)));
    const g = Math.max(0, Math.min(255, parseInt(m[2], 10)));
    const b = Math.max(0, Math.min(255, parseInt(m[3], 10)));
    const toHex = (n: number) => n.toString(16).padStart(2, "0");
    return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
  }

  // Resolve var(--token) to a hex suitable for the color input
  function resolveVarToHex(varName: TokenName): string {
    if (typeof window === "undefined") return "#000000";
    const el = document.createElement("div");
    el.style.color = `var(${varName})`;
    document.body.appendChild(el);
    const computed = getComputedStyle(el).color; // rgb(a)
    document.body.removeChild(el);
    return (
      cssColorToHex(computed) || cssColorToHex(tokens[varName]) || "#000000"
    );
  }

  const resetAll = () => {
    window.localStorage.removeItem("tokens");
    // Reload to recompute from CSS
    location.reload();
  };

  const exportOverrides = () => {
    const blob = new Blob([JSON.stringify(tokens, null, 2)], {
      type: "application/json",
    });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "design-tokens-overrides.json";
    a.click();
  };

  const contrast = useMemo(() => {
    const bg = tokens[bgChoice];
    const fg = tokens[fgChoice];
    if (!bg || !fg) return null;
    return contrastRatio(hex(bg), hex(fg));
  }, [tokens, bgChoice, fgChoice]);

  const ColorSwatch = ({
    name,
    varName,
  }: {
    name: string;
    varName: TokenName;
  }) => (
    <div className="flex items-center gap-3 p-md rounded-lg border border-border">
      <div
        className="h-8 w-8 rounded"
        style={{ background: `var(${varName})` }}
        aria-label={`${name} swatch`}
      />
      <div className="text-sm">
        <div className="font-medium">{name}</div>
        <div className="opacity-80">
          <code>{varName}</code>
        </div>
      </div>
    </div>
  );

  return (
    <>
      <main className="min-h-screen p-lg bg-bg text-fg">
        <div className="mx-auto max-w-5xl space-y-lg">
          <header className="flex items-end justify-between">
            <div>
              <h1 className="text-2xl font-bold">Design Tokens</h1>
              <p className="text-sm opacity-80">
                All colors, fonts, radii, spacing, and shadows come from
                <code className="ml-1">src/styles/tokens.css</code> and are
                mapped via Tailwind.
              </p>
            </div>
            <div className="space-x-sm">
              <button className="btn" onClick={exportOverrides}>
                Export JSON
              </button>
              <button className="btn" onClick={resetAll}>
                Reset All
              </button>
            </div>
          </header>

          {/* Color helper with live editors */}
          <section className="space-y-md">
            <h2 className="text-lg font-semibold">Colors</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-md">
              {COLOR_TOKENS.map((t) => {
                const hex = resolveVarToHex(t);
                return (
                  <div key={t} className="rounded-lg border border-border p-md">
                    <div className="flex items-center justify-between mb-sm">
                      <div className="font-medium">{t}</div>
                      <div
                        className="h-6 w-6 rounded border border-border"
                        style={{ background: `var(${t})` }}
                      />
                    </div>
                    <div className="flex items-center gap-sm">
                      <input
                        type="color"
                        aria-label={`${t} color`}
                        value={hex}
                        onChange={(e) => updateToken(t, e.target.value)}
                        className="h-9 w-14 bg-transparent cursor-pointer"
                      />
                      <input
                        value={tokens[t] || ""}
                        onChange={(e) => updateToken(t, e.target.value)}
                        className="flex-1 rounded border border-border bg-bg p-sm"
                        placeholder="#rrggbb or color()"
                      />
                      <button
                        className="btn"
                        type="button"
                        onClick={() => openHslModal(t)}
                      >
                        HSL
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Contrast checker */}
            <div className="rounded-lg border border-border p-md">
              <div className="flex items-center gap-md mb-sm">
                <div>
                  <label className="block text-sm opacity-80 mb-xs">
                    BG token
                  </label>
                  <select
                    className="rounded border border-border bg-bg p-sm"
                    value={bgChoice}
                    onChange={(e) => setBgChoice(e.target.value as TokenName)}
                  >
                    {COLOR_TOKENS.map((t) => (
                      <option key={t} value={t}>
                        {t}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm opacity-80 mb-xs">
                    FG token
                  </label>
                  <select
                    className="rounded border border-border bg-bg p-sm"
                    value={fgChoice}
                    onChange={(e) => setFgChoice(e.target.value as TokenName)}
                  >
                    {COLOR_TOKENS.map((t) => (
                      <option key={t} value={t}>
                        {t}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="ml-auto text-sm opacity-80">
                  Contrast: {contrast ?? "n/a"}
                  {typeof contrast === "number" && (
                    <span className="ml-sm">
                      {contrast >= 7
                        ? "(AAA)"
                        : contrast >= 4.5
                        ? "(AA)"
                        : "(Fail)"}
                    </span>
                  )}
                </div>
              </div>
              <div
                className="rounded p-md"
                style={{
                  background: `var(${bgChoice})`,
                  color: `var(${fgChoice})`,
                }}
              >
                <div className="text-lg font-semibold">Sample text</div>
                <div className="opacity-80 text-sm">The quick brown fox…</div>
                <button className="btn mt-sm">Button sample</button>
              </div>
            </div>
          </section>

          {/* Fonts */}
          <section className="space-y-sm">
            <h2 className="text-lg font-semibold">Fonts</h2>
            <div className="grid sm:grid-cols-2 gap-md">
              {FONT_TOKENS.map((t) => (
                <div key={t} className="rounded-lg border border-border p-md">
                  <div className="text-sm opacity-80 mb-sm">{t}</div>
                  <input
                    className="w-full rounded border border-border bg-bg p-sm mb-sm"
                    value={tokens[t] || ""}
                    onChange={(e) => updateToken(t, e.target.value)}
                    placeholder="Font stack"
                  />
                  <p style={{ fontFamily: `var(${t})` }}>
                    The quick brown fox jumps over the lazy dog.
                  </p>
                </div>
              ))}
            </div>
          </section>

          {/* Radii */}
          <section className="space-y-sm">
            <h2 className="text-lg font-semibold">Radii</h2>
            <div className="grid sm:grid-cols-3 gap-md">
              {RADIUS_TOKENS.map((t) => (
                <div key={t} className="rounded-lg border border-border p-md">
                  <div className="text-sm opacity-80 mb-sm">{t}</div>
                  <div className="flex items-center gap-sm">
                    <input
                      type="number"
                      className="w-24 rounded border border-border bg-bg p-sm"
                      value={parsePx(tokens[t] || "0")}
                      onChange={(e) =>
                        updateToken(t, toPx(Number(e.target.value)))
                      }
                    />
                    <div className="flex-1">
                      <div
                        className="h-10 border border-border"
                        style={{ borderRadius: `var(${t})` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Spacing */}
          <section className="space-y-sm">
            <h2 className="text-lg font-semibold">Spacing</h2>
            <div className="grid sm:grid-cols-4 gap-md items-end">
              {SPACING_TOKENS.map((t) => (
                <div key={t} className="rounded-lg border border-border p-md">
                  <div className="text-sm opacity-80 mb-sm">{t}</div>
                  <input
                    type="number"
                    className="w-full rounded border border-border bg-bg p-sm"
                    value={parsePx(tokens[t] || "0")}
                    onChange={(e) =>
                      updateToken(t, toPx(Number(e.target.value)))
                    }
                  />
                  <div
                    className="mt-sm text-center bg-secondary/30"
                    style={{ padding: `var(${t})` }}
                  >
                    sample
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Shadows */}
          <section className="space-y-sm">
            <h2 className="text-lg font-semibold">Shadows</h2>
            <div className="grid sm:grid-cols-3 gap-md">
              {SHADOW_TOKENS.map((t) => (
                <div key={t} className="rounded-lg border border-border p-md">
                  <div className="text-sm opacity-80 mb-sm">{t}</div>
                  <input
                    className="w-full rounded border border-border bg-bg p-sm mb-sm"
                    value={tokens[t] || ""}
                    onChange={(e) => updateToken(t, e.target.value)}
                    placeholder="shadow CSS"
                  />
                  <div
                    className="h-16 bg-bg rounded"
                    style={{ boxShadow: `var(${t})` }}
                  />
                </div>
              ))}
            </div>
          </section>

          {/* Example components */}
          <section className="space-y-sm">
            <h2 className="text-lg font-semibold">Example components</h2>
            <div className="grid md:grid-cols-2 gap-md">
              <div className="card">
                <div className="text-sm opacity-80 mb-sm">Card</div>
                <div className="font-medium">
                  This card uses tokens for radius, shadow and border.
                </div>
              </div>
              <div className="space-x-sm">
                <button className="btn">Primary Button</button>
                <button
                  className="btn"
                  style={{ background: "var(--secondary)" }}
                >
                  Secondary
                </button>
              </div>
            </div>
          </section>
        </div>
      </main>
      /* HSL Modal */
      {modalOpen && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center"
          style={{ background: "rgba(0,0,0,0.5)" }}
        >
          <div
            className="rounded-lg border border-border p-md"
            style={{ background: "var(--bg)" }}
          >
            <div className="text-lg font-semibold mb-sm">
              Adjust HSL {modalToken}
            </div>
            <div className="grid gap-sm" style={{ minWidth: 280 }}>
              <label className="grid gap-xs">
                <span className="text-sm opacity-80">Hue: {hsl.h}</span>
                <input
                  type="range"
                  min={0}
                  max={360}
                  value={hsl.h}
                  onChange={(e) =>
                    setHsl({ ...hsl, h: Number(e.target.value) })
                  }
                />
              </label>
              <label className="grid gap-xs">
                <span className="text-sm opacity-80">Saturation: {hsl.s}%</span>
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={hsl.s}
                  onChange={(e) =>
                    setHsl({ ...hsl, s: Number(e.target.value) })
                  }
                />
              </label>
              <label className="grid gap-xs">
                <span className="text-sm opacity-80">Lightness: {hsl.l}%</span>
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={hsl.l}
                  onChange={(e) =>
                    setHsl({ ...hsl, l: Number(e.target.value) })
                  }
                />
              </label>
              <div
                className="h-12 rounded"
                style={{
                  background: hslToCss(hsl),
                  border: "1px solid var(--border)",
                }}
              />
              <div className="flex justify-end gap-sm mt-sm">
                <button
                  className="btn"
                  type="button"
                  onClick={() => setModalOpen(false)}
                >
                  Cancel
                </button>
                <button className="btn" type="button" onClick={applyHsl}>
                  Apply
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
