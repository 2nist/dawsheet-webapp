import { useState } from "react";

const API_URL =
  (globalThis as any).process?.env?.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

export default function ImportJsonPage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

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
      const res = await fetch(`${API_URL}/import/json`, {
        method: "POST",
        body: fd,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || "Upload failed");
      setResult(data);
    } catch (err: any) {
      setError(err.message || String(err));
    } finally {
      setLoading(false);
    }
  };

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
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
