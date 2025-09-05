import { useState } from "react";
import axios from "axios";

export default function ImportPage() {
  const [text, setText] = useState("");
  const [status, setStatus] = useState("");
  const [files, setFiles] = useState<FileList | null>(null);

  const onParse = async () => {
    try {
      setStatus("Parsing...");
      const r = await axios.post(
        process.env.NEXT_PUBLIC_API_BASE + "/parse",
        text,
        {
          headers: { "Content-Type": "text/plain" },
        }
      );
      const songs = r.data.songs || [];
      setStatus(`Parsed ${songs.length} songs. Saving...`);
      for (const s of songs) {
        await axios.post(process.env.NEXT_PUBLIC_API_BASE + "/songs", s);
      }
      setStatus("Saved.");
    } catch (e: any) {
      setStatus("Error: " + (e.response?.data?.detail || e.message));
    }
  };

  const onImportFile = async () => {
    if (!files || files.length === 0) return;
    try {
      setStatus("Uploading & parsing file...");
      const fd = new FormData();
      Array.from(files).forEach((f) => fd.append("files", f));
      const r = await axios.post(
        process.env.NEXT_PUBLIC_API_BASE + "/import/files",
        fd,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      const songs = r.data.songs || [];
      setStatus(`Parsed ${songs.length} songs. Saving...`);
      for (const s of songs) {
        await axios.post(process.env.NEXT_PUBLIC_API_BASE + "/songs", s);
      }
      setStatus("Saved.");
    } catch (e: any) {
      setStatus("Error: " + (e.response?.data?.detail || e.message));
    }
  };

  return (
    <main style={{ padding: 24 }}>
      <h2>Batch Import</h2>
      <section style={{ marginBottom: 16 }}>
        <h3>Upload Files</h3>
        <input
          type="file"
          multiple
          accept=".json,.mid,.midi,.mp3,.txt,.pro,.chordpro,.md"
          onChange={(e) => setFiles(e.target.files)}
        />
        <div style={{ marginTop: 8 }}>
          <button
            disabled={!files || files.length === 0}
            onClick={onImportFile}
          >
            Import Files
          </button>
        </div>
      </section>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        style={{ width: "100%", height: 200 }}
        placeholder="Paste songs here..."
      />
      <div style={{ marginTop: 8 }}>
        <button onClick={onParse}>Parse & Save</button>
        <span style={{ marginLeft: 8, color: "#666" }}>{status}</span>
      </div>
    </main>
  );
}
