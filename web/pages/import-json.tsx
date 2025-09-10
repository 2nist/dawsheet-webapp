import { useState } from "react";

const API_URL =
  (globalThis as any).process?.env?.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

export default function ImportJsonPage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [includeLyrics, setIncludeLyrics] = useState(true);
  const combineUrl = `${API_URL}/combine/jcrd-lyrics?save=true`;
  const combinePreviewUrl = `${API_URL}/combine/jcrd-lyrics?save=false`;

  const onSubmit = async (e: any) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    if (!file) {
      setError("Choose a .json file first.");
      return;
    }
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch(
        `${API_URL}/import/json?include_lyrics=${
          includeLyrics ? "true" : "false"
        }`,
        {
          method: "POST",
          body: fd,
        }
      );
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || "Upload failed");
      setResult(data);
    } catch (err: any) {
      setError(err.message || String(err));
    } finally {
      setLoading(false);
    }
  };

  async function onCombineSave() {
    try {
      setError(null);
      if (!result?.preview) throw new Error("Upload and preview JSON first.");
      const auto = result.auto_combined || null;
      const payload = {
        jcrd: result.preview,
        lyrics: { lines: (auto?.lines as any[]) || [] },
        title:
          result.summary?.title ||
          (file?.name || "Untitled").replace(/\.json$/i, ""),
        artist: result.summary?.artist || "",
        include_lyrics: includeLyrics,
      };
      const res = await fetch(combineUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || "Combine failed");
      setResult((r: any) => ({ ...(r || {}), combined_saved: data }));
    } catch (err: any) {
      setError(err.message || String(err));
    }
  }

  async function onCombinePreview() {
    try {
      setError(null);
      if (!result?.preview) throw new Error("Upload and preview JSON first.");
      const auto = result.auto_combined || null;
      const payload = {
        jcrd: result.preview,
        lyrics: { lines: (auto?.lines as any[]) || [] },
        title:
          result.summary?.title ||
          (file?.name || "Untitled").replace(/\.json$/i, ""),
        artist: result.summary?.artist || "",
        include_lyrics: includeLyrics,
      };
      const res = await fetch(combinePreviewUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || "Combine preview failed");
      setResult((r: any) => ({ ...(r || {}), combined_preview: data }));
    } catch (err: any) {
      setError(err.message || String(err));
    }
  }

  return (
    <main className="min-h-screen bg-bg text-fg p-lg">
      <div className="max-w-2xl mx-auto rounded-lg border border-border">
        <div className="p-lg bg-bg">
          <h1 className="text-2xl font-bold">Import JSON</h1>
          <p className="text-sm opacity-80 mt-sm">
            Upload a .json to test the pipeline.
          </p>

          <form onSubmit={onSubmit} className="mt-md space-y-md">
            <input
              type="file"
              accept=".json,application/json"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="block w-full"
            />
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={includeLyrics}
                onChange={(e) => setIncludeLyrics(e.target.checked)}
              />
              Include lyrics when combining (auto-fetch if available)
            </label>
            <button
              type="submit"
              disabled={!file || loading}
              className="px-md py-sm text-black rounded bg-primary disabled:opacity-60"
            >
              {loading ? "Uploading…" : "Upload JSON"}
            </button>
          </form>

          {error && (
            <div
              className="mt-md text-sm"
              style={{ color: "var(--secondary)" }}
            >
              <strong>Error:</strong> {error}
            </div>
          )}

          {result && (
            <div className="mt-lg">
              <h2 className="text-lg font-semibold">Result</h2>
              <div className="mt-sm text-sm">
                <div>
                  File: <code>{result.filename}</code>
                </div>
                <div>
                  Size: <code>{result.size_bytes}</code> bytes
                </div>
                <div className="mt-sm">Summary:</div>
                <pre className="mt-sm p-sm rounded-lg overflow-auto text-xs bg-muted text-fg">
                  {JSON.stringify(result.summary, null, 2)}
                </pre>
                <div className="mt-sm">Preview (truncated client-side):</div>
                <pre
                  className="mt-sm p-sm rounded-lg overflow-auto text-xs bg-muted text-fg"
                  style={{ maxHeight: "32rem" }}
                >
                  {JSON.stringify(result.preview, null, 2)}
                </pre>
                <div className="mt-sm flex gap-2">
                  <button
                    className="px-md py-sm rounded border border-border"
                    onClick={onCombinePreview}
                  >
                    Preview Combined
                  </button>
                  <button
                    className="px-md py-sm rounded bg-primary text-black"
                    onClick={onCombineSave}
                  >
                    Combine & Save
                  </button>
                </div>
                {result.combined_preview && (
                  <div className="mt-sm">
                    <div className="text-sm font-medium">Combined preview</div>
                    <pre className="mt-sm p-sm rounded-lg overflow-auto text-xs bg-muted text-fg">
                      {JSON.stringify(result.combined_preview, null, 2)}
                    </pre>
                  </div>
                )}
                {result.combined_saved && (
                  <div className="mt-sm text-sm">
                    <div className="font-medium">Saved</div>
                    <pre className="mt-sm p-sm rounded-lg overflow-auto text-xs bg-muted text-fg">
                      {JSON.stringify(result.combined_saved, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
