import { useMemo, useState } from "react";
import { postJSON, request, errorMessage } from "../lib/api";
import useSWRMutation from "swr/mutation";

export default function ImportPage() {
  const [text, setText] = useState("");
  const [status, setStatus] = useState("");
  const [files, setFiles] = useState<FileList | null>(null);
  const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
  const parseUrl = useMemo(() => `${apiBase}/legacy/lyrics/parse`, [apiBase]);
  const importLyricsUrl = useMemo(() => `${apiBase}/import/lyrics`, [apiBase]);
  const importMultiUrl = useMemo(() => `${apiBase}/import/multi`, [apiBase]);
  const { trigger: previewParse, isMutating: previewing } = useSWRMutation(
    importLyricsUrl,
    async (
      url: string,
      { arg }: { arg: { text: string; filename?: string } }
    ) => {
      const blob = new Blob([arg.text || ""], { type: "text/plain" });
      const fname = arg.filename || "preview.txt";
      const file = new File([blob], fname, { type: blob.type });
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch(url, { method: "POST", body: fd });
      return res.json();
    }
  );
  const [preview, setPreview] = useState<{
    count: number;
    sample: string[];
    sampleTs: (number | null)[];
  } | null>(null);

  const onParse = async () => {
    try {
      setStatus("Parsing...");
      const r = await request<any>(apiBase + "/parse", {
        method: "POST",
        headers: { "Content-Type": "text/plain" },
        body: text,
      });
      const songs = r?.songs || [];
      setStatus(`Parsed ${songs.length} songs. Saving...`);
      for (const s of songs) {
        await postJSON(apiBase + "/songs", s);
      }
      setStatus("Saved.");
    } catch (e: any) {
      setStatus("Error: " + errorMessage(e));
    }
  };

  const onImportFile = async () => {
    if (!files || files.length === 0) return;
    try {
      setStatus("Uploading & parsing files...");
      const fd = new FormData();
      Array.from(files).forEach((f: File) => fd.append("files", f));
      const r = await request<any>(importMultiUrl, {
        method: "POST",
        body: fd,
      });
      const songs = r?.songs || [];
      setStatus(`Imported ${songs.length} songs. Saving...`);
      for (const s of songs) {
        await postJSON(apiBase + "/songs", s);
      }
      setStatus("Saved.");
    } catch (e: any) {
      setStatus("Error: " + errorMessage(e));
    }
  };

  const onPreview = async () => {
    try {
      let payload = text;
      let fname: string | undefined = undefined;
      // If no pasted text, try to preview from the first selected text-lyrics file
      if (
        (!payload || payload.trim().length === 0) &&
        files &&
        files.length > 0
      ) {
        const first = (files[0] as File) || (Array.from(files) as File[])[0];
        const name = first.name.toLowerCase();
        const isTextLyrics = [".lrc", ".vtt", ".txt", ".csv"].some((ext) =>
          name.endsWith(ext)
        );
        if (isTextLyrics) {
          payload = await first.text();
          fname = first.name;
        } else if (name.endsWith(".json") || name.endsWith(".jcrd.json")) {
          payload = await first.text();
          fname = first.name;
        }
      }
      const r = await previewParse({ text: payload || "", filename: fname });
      const lines = Array.isArray(r?.lines) ? r.lines : [];
      setPreview({
        count: lines.length,
        sample: lines.slice(0, 10).map((l: any) => l?.text ?? ""),
        sampleTs: lines
          .slice(0, 10)
          .map((l: any) => (typeof l?.ts === "number" ? l.ts : null)),
      });
    } catch (e) {
      setPreview({ count: 0, sample: [], sampleTs: [] });
    }
  };

  return (
    <main className="min-h-screen" style={{ padding: "var(--spacing-lg)" }}>
      <div className="max-w-4xl mx-auto">
        <div
          className="card"
          style={{
            background: "var(--cream)",
            color: "#111",
            borderRadius: "var(--radius-lg)",
          }}
        >
          <h2
            className="text-2xl font-semibold"
            style={{ fontFamily: "Poppins, var(--font-sans)" }}
          >
            Import
          </h2>
          <p className="mt-1" style={{ color: "#4b5563" }}>
            Upload lyrics, MIDI/JSON, or paste text. We’ll parse and save songs.
          </p>

          <section className="mt-4">
            <h3 className="text-lg font-medium">Upload Files</h3>
            <input
              className="mt-2"
              type="file"
              multiple
              accept=".json,.mid,.midi,.mp3,.txt,.pro,.chordpro,.md,.lrc,.vtt,.csv"
              onChange={(e) => setFiles(e.target.files)}
            />
            <div className="text-sm mt-1" style={{ color: "#6b7280" }}>
              Supports .json, .mid/.midi, .mp3, .txt, .lrc, .vtt, .csv
            </div>
            <div className="mt-2">
              <button
                className="btn"
                disabled={!files || files.length === 0}
                onClick={onImportFile}
              >
                Import Files
              </button>
            </div>
          </section>

          <section className="mt-6">
            <h3 className="text-lg font-medium">Paste Text</h3>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="w-full mt-2"
              style={{
                height: 200,
                color: "#111",
                background: "#fff",
                borderRadius: "var(--radius)",
              }}
              placeholder="Paste songs here..."
            />
            <div className="mt-2 flex items-center gap-2">
              <button className="btn" onClick={onPreview} disabled={previewing}>
                {previewing ? "Previewing…" : "Preview"}
              </button>
              <button className="btn" onClick={onParse}>
                Parse & Save
              </button>
              <span className="text-sm" style={{ color: "#6b7280" }}>
                {status}
              </span>
            </div>
          </section>

          {preview && (
            <div
              className="card mt-4"
              style={{ background: "#fff", color: "#111" }}
            >
              {preview.count > 0 ? (
                <>
                  <div className="mb-2">Lines parsed: {preview.count}</div>
                  <ul className="list-none p-0 m-0">
                    {preview.sample.map((t, i) => (
                      <li
                        key={i}
                        className="text-sm"
                        style={{ color: "#4b5563" }}
                      >
                        {i + 1}.{" "}
                        {preview.sampleTs[i] !== null
                          ? `[${preview.sampleTs[i]}] `
                          : ""}
                        {t}
                      </li>
                    ))}
                  </ul>
                </>
              ) : (
                <div className="text-sm" style={{ color: "#6b7280" }}>
                  No previewable lines for this input.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
