import useSWR, { mutate } from "swr";
import { swrFetcher, postJSON, putJSON, del, HttpError } from "../lib/api";
import { useState } from "react";
import Link from "next/link";

const apiBase = process.env.NEXT_PUBLIC_API_BASE;
const fetcher = swrFetcher;

export default function SongsPage() {
  const url = `${apiBase}/songs`;
  const { data, error, isLoading } = useSWR(url, fetcher);
  const [title, setTitle] = useState("");
  const [artist, setArtist] = useState("");
  const [content, setContent] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [errMsg, setErrMsg] = useState<string | null>(null);

  const onCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setErrMsg(null);
    try {
      await postJSON(url, { title, artist, content });
      setTitle("");
      setArtist("");
      setContent("");
      mutate(url);
    } catch (err: any) {
      setErrMsg(
        err instanceof HttpError
          ? String(err.body?.detail || err.message)
          : String(err)
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main style={{ padding: 24, maxWidth: 800, margin: "0 auto" }}>
      <h2>Songs</h2>
      {isLoading && <div>Loading…</div>}
      {error && <div style={{ color: "crimson" }}>Error: {String(error)}</div>}

      <section
        style={{
          margin: "16px 0",
          padding: 12,
          border: "1px solid #ddd",
          borderRadius: 8,
        }}
      >
        <h3 style={{ marginTop: 0 }}>Add Song</h3>
        {errMsg && (
          <div style={{ color: "crimson", marginBottom: 8 }}>{errMsg}</div>
        )}
        <form onSubmit={onCreate} style={{ display: "grid", gap: 8 }}>
          <input
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
          <input
            placeholder="Artist"
            value={artist}
            onChange={(e) => setArtist(e.target.value)}
          />
          <textarea
            placeholder="Content (lyrics/chords)"
            rows={6}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
          />
          <button type="submit" disabled={submitting}>
            {submitting ? "Saving…" : "Create"}
          </button>
        </form>
      </section>

      <ul style={{ listStyle: "none", padding: 0, display: "grid", gap: 8 }}>
        {Array.isArray(data) &&
          data.map((s: any) => (
            <li
              key={s.id}
              style={{ border: "1px solid #eee", borderRadius: 8, padding: 12 }}
            >
              <SongItem
                song={s}
                apiBase={apiBase!}
                onChanged={() => mutate(url)}
              />
            </li>
          ))}
      </ul>
    </main>
  );
}

function SongItem({
  song,
  apiBase,
  onChanged,
}: {
  song: any;
  apiBase: string;
  onChanged: () => void;
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState(song.title);
  const [artist, setArtist] = useState(song.artist);
  const [content, setContent] = useState(song.content);
  const [busy, setBusy] = useState(false);
  const [errMsg, setErrMsg] = useState<string | null>(null);

  const onSave = async () => {
    setBusy(true);
    setErrMsg(null);
    try {
      await putJSON(`${apiBase}/songs/${song.id}`, {
        title,
        artist,
        content,
      });
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
        {errMsg && <div style={{ color: "crimson" }}>{errMsg}</div>}
        <input value={title} onChange={(e) => setTitle(e.target.value)} />
        <input value={artist} onChange={(e) => setArtist(e.target.value)} />
        <textarea
          rows={4}
          value={content}
          onChange={(e) => setContent(e.target.value)}
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
      <div>
        <strong>
          <Link href={`/songs/${song.id}`}>{song.title}</Link>
        </strong>{" "}
        — {song.artist}
      </div>
      <pre
        style={{
          whiteSpace: "pre-wrap",
          background: "#fafafa",
          padding: 8,
          borderRadius: 6,
        }}
      >
        {song.content}
      </pre>
      {errMsg && <div style={{ color: "crimson" }}>{errMsg}</div>}
      <div style={{ display: "flex", gap: 8 }}>
        <Link href={`/songs/${song.id}`}>View</Link>
        <button onClick={() => setIsEditing(true)} disabled={busy}>
          Edit
        </button>
        <button onClick={onDelete} disabled={busy} style={{ color: "crimson" }}>
          Delete
        </button>
      </div>
    </div>
  );
}
