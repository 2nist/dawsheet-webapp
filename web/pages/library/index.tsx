import useSWR, { mutate } from "swr";
import Link from "next/link";
import { putJSON, del, HttpError } from "@/lib/api";
import { useState } from "react";

const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

type Song = { id: number; title: string; artist: string; content: string };

export default function LibraryPage() {
  const url = `${apiBase}/songs`;
  const { data, error, isLoading } = useSWR<Song[]>(url, async (u) => {
    const res = await fetch(u);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  });
  const songs = data || [];
  return (
    <main style={{ padding: 24 }}>
      <h1>Library</h1>
      <div style={{ marginTop: 8 }}>
        <Link href="/" className="btn" style={{ marginRight: 8 }}>
          Back to Home
        </Link>
        <Link href="/import" className="btn">
          Import More
        </Link>
      </div>
      {isLoading && <div style={{ marginTop: 12 }}>Loading…</div>}
      {error && (
        <div style={{ marginTop: 12, color: "#b91c1c" }}>
          Error: {String(error)}
        </div>
      )}
      <ul
        style={{
          marginTop: 16,
          listStyle: "none",
          padding: 0,
          display: "grid",
          gap: 8,
        }}
      >
        {songs.map((s) => (
          <li
            key={s.id}
            className="card"
            style={{
              background: "#0b1220",
              color: "#e5e7eb",
              border: "1px solid #1f2937",
              borderRadius: 8,
              padding: 12,
            }}
          >
            <LibraryItem
              song={s}
              apiBase={apiBase}
              onChanged={() => mutate(url)}
            />
          </li>
        ))}
      </ul>
    </main>
  );
}

function LibraryItem({
  song,
  apiBase,
  onChanged,
}: {
  song: Song;
  apiBase: string;
  onChanged: () => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [busy, setBusy] = useState(false);
  const [errMsg, setErrMsg] = useState<string | null>(null);

  const [title, setTitle] = useState(song.title);
  const [artist, setArtist] = useState(song.artist);
  const [content, setContent] = useState(song.content);

  const onSave = async () => {
    setBusy(true);
    setErrMsg(null);
    try {
      await putJSON(`${apiBase}/songs/${song.id}`, { title, artist, content });
      setIsEditing(false);
      onChanged();
    } catch (err: any) {
      setErrMsg(
        err instanceof HttpError
          ? String(err.body?.detail || err.message)
          : String(err)
      );
    } finally {
      setBusy(false);
    }
  };

  const onDelete = async () => {
    if (!confirm(`Delete "${song.title}"?`)) return;
    setBusy(true);
    setErrMsg(null);
    try {
      await del(`${apiBase}/songs/${song.id}`);
      onChanged();
    } catch (err: any) {
      setErrMsg(
        err instanceof HttpError
          ? String(err.body?.detail || err.message)
          : String(err)
      );
    } finally {
      setBusy(false);
    }
  };

  if (isEditing) {
    return (
      <div style={{ display: "grid", gap: 8 }}>
        {errMsg && <div style={{ color: "#fca5a5" }}>{errMsg}</div>}
        <input value={title} onChange={(e) => setTitle(e.target.value)} />
        <input value={artist} onChange={(e) => setArtist(e.target.value)} />
        <textarea
          rows={6}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          style={{
            background: "#0f172a",
            color: "#e5e7eb",
            padding: 12,
            borderRadius: 6,
            border: "1px solid #1f2937",
          }}
        />
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={onSave} disabled={busy}>
            {busy ? "Saving…" : "Save"}
          </button>
          <button onClick={() => setIsEditing(false)} disabled={busy}>
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: "grid", gap: 8 }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12,
        }}
      >
        <div>
          <strong>
            <Link href={`/songs/${song.id}`}>{song.title}</Link>
          </strong>{" "}
          — {song.artist}
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <Link href={`/songs/${song.id}`} className="btn">
            View
          </Link>
          <button onClick={() => setIsEditing(true)} disabled={busy}>
            Edit
          </button>
          <button
            onClick={onDelete}
            disabled={busy}
            style={{ color: "#fca5a5" }}
          >
            Delete
          </button>
          <button
            onClick={() => setExpanded((v) => !v)}
            aria-expanded={expanded}
            aria-controls={`lib-${song.id}-content`}
          >
            {expanded ? "Collapse" : "Expand"}
          </button>
        </div>
      </div>
      {expanded && (
        <pre
          id={`lib-${song.id}-content`}
          className="mt-1 text-sm"
          style={{
            whiteSpace: "pre-wrap",
            background: "#0f172a",
            color: "#e5e7eb",
            padding: 12,
            borderRadius: 6,
            border: "1px solid #1f2937",
          }}
        >
          {song.content}
        </pre>
      )}
      {errMsg && <div style={{ color: "#fca5a5" }}>{errMsg}</div>}
    </div>
  );
}
