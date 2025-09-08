import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import Link from "next/link";
import { ZSongDraft, type SongDraft } from "../../../lib/schemas/songDraft";

const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function DraftReview() {
  const router = useRouter();
  const { id } = router.query;
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const [validation, setValidation] = useState<string | null>(null);
  const [draft, setDraft] = useState<SongDraft | null>(null);

  useEffect(() => {
    if (!id) return;
    (async () => {
      try {
        const res = await fetch(`${apiBase}/drafts/${id}/songdoc`);
        if (!res.ok) throw new Error(await res.text());
        const data = await res.json();
        const parsed = ZSongDraft.safeParse(data);
        if (!parsed.success) {
          setValidation(parsed.error.errors.map((e) => e.message).join("; "));
        } else {
          setValidation(null);
          setDraft(parsed.data);
        }
      } catch (e: any) {
        setErr(String(e));
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  async function createSong() {
    if (!id) return;
    const res = await fetch(`${apiBase}/songs/from-draft`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ draftId: Number(id) }),
    });
    if (!res.ok) {
      alert(await res.text());
      return;
    }
    const song = await res.json();
    router.push(`/songs/${song.id}`);
  }

  if (loading) return <main style={{ padding: 24 }}>Loading draft…</main>;
  if (err)
    return <main style={{ padding: 24, color: "#ef4444" }}>Error: {err}</main>;

  const meta = draft?.meta || {};
  const sections = draft?.sections || [];
  const lyricsList = draft?.lyrics || [];

  return (
    <main
      style={{
        padding: 24,
        display: "grid",
        gap: 16,
        gridTemplateColumns: "1fr 1fr",
      }}
    >
      <section>
        <h2>Waveform</h2>
        <div
          style={{
            height: 240,
            border: "1px solid #1f2937",
            background: "#0f172a",
            borderRadius: 6,
          }}
        />
        <p style={{ color: "#9aa3af" }}>Beat grid coming soon.</p>
      </section>
      <section style={{ display: "grid", gap: 12 }}>
        <div>
          <h3>Meta</h3>
          <div style={{ color: "#e5e7eb" }}>
            <div>Title: {meta.title || "(none)"}</div>
            <div>Artist: {meta.artist || "(none)"}</div>
            {meta.timeSig && <div>Time Sig: {meta.timeSig}</div>}
            {meta.bpm?.value && <div>BPM: {meta.bpm.value}</div>}
          </div>
        </div>
        <div>
          <h3>Sections</h3>
          <pre
            style={{
              whiteSpace: "pre-wrap",
              background: "#0f172a",
              color: "#e5e7eb",
              padding: 12,
              borderRadius: 6,
              border: "1px solid #1f2937",
            }}
          >
            {JSON.stringify(sections, null, 2)}
          </pre>
        </div>
        <div>
          <h3>Lyrics</h3>
          <div
            style={{
              width: "100%",
              minHeight: 160,
              background: "#0f172a",
              color: "#e5e7eb",
              padding: 12,
              borderRadius: 6,
              border: "1px solid #1f2937",
            }}
          >
            {lyricsList.length > 0
              ? lyricsList.map((l, i) => <div key={i}>{l.text}</div>)
              : "(none)"}
          </div>
        </div>
        {validation && (
          <div style={{ color: "#f59e0b" }}>Schema warnings: {validation}</div>
        )}
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={createSong}>Create Song</button>
          <Link href="/library">Back to Library</Link>
        </div>
      </section>
    </main>
  );
}
