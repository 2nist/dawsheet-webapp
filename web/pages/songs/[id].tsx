import React, { useEffect, useState, useMemo, useCallback, useRef } from "react";
import { useRouter } from "next/router";
import useSWR from "swr";
import { swrFetcher } from "@/lib/api";
import { SectionRail } from "@/components/SectionRail";
import { ChordLane } from "@/components/ChordLane";
import { BarRuler } from "@/components/BarRuler";
import { LyricLane } from "@/components/LyricLane";

const SongPage: React.FC = () => {
  const router = useRouter();
  const { id } = router.query;
  const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

  const [zoom, setZoom] = useState(8); // px per beat
  const [playhead, setPlayhead] = useState(0); // Current playhead position in beats
  const [isDragging, setIsDragging] = useState(false);
  const [lastInteractionX, setLastInteractionX] = useState(0);

  const url = useMemo(() => {
    if (!id) return null;
    const sid = Array.isArray(id) ? id[0] : id;
    return `${apiBase}/v1/songs/${sid}/doc`;
  }, [id, apiBase]);

  const { data, error, isLoading, mutate } = useSWR(url, swrFetcher);

  const doc = data as any;
  const sections = useMemo(() => doc?.sections || [], [doc]);
  const chords = useMemo(() => (doc?.chords || []) as { symbol: string; startBeat: number }[], [doc]);
  const lyrics = useMemo(() => (doc?.lyrics || []) as { text: string; beat?: number | null }[], [doc]);
  const timeSig: string = doc?.timeSignature || "4/4";
  const beatsPerBar = Number(timeSig?.split("/")[0] || "4") || 4;

  const totalBeats = useMemo(() => {
    if (!chords.length && !sections.length) return beatsPerBar * 16; // Default length
    const lastChordBeat = chords[chords.length - 1]?.startBeat ?? 0;
    const lastSectionBeat = sections[sections.length - 1]?.startBeat ?? 0;
    const lastBeat = Math.max(lastChordBeat, lastSectionBeat) + beatsPerBar;
    return Math.max(beatsPerBar, lastBeat);
  }, [chords, sections, beatsPerBar]);

  const normalizeBeat = useCallback((b: number) => {
    const tb = Math.max(1, totalBeats || 1);
    return ((b % tb) + tb) % tb;
  }, [totalBeats]);

  // Cylindrical rotation boundaries
  const ROTATION_BARS = 10;
  const rotationBeats = ROTATION_BARS * beatsPerBar;
  const cycles = Math.max(3, Math.ceil(rotationBeats / Math.max(1, totalBeats)));
  const sideBeats = cycles * totalBeats;
  const extendedTotalBeats = totalBeats + 2 * sideBeats;

  const rotatingContent = useMemo(() => {
    if (!doc) return { sections: [], chords: [], lyrics: [] };

    const rotatedSections: any[] = [];
    const rotatedChords: any[] = [];
    const rotatedLyrics: any[] = [];

    for (let i = -cycles; i <= cycles; i++) {
      const offset = i * totalBeats;
      sections.forEach(section => rotatedSections.push({ ...section, startBeat: offset + section.startBeat }));
      chords.forEach(chord => rotatedChords.push({ ...chord, startBeat: offset + chord.startBeat }));
      lyrics.forEach(lyric => rotatedLyrics.push({ ...lyric, beat: offset + (lyric.beat || 0) }));
    }

    const shift = sideBeats;
    return {
      sections: rotatedSections.map(s => ({ ...s, startBeat: (s.startBeat || 0) + shift })),
      chords: rotatedChords.map(c => ({ ...c, startBeat: (c.startBeat || 0) + shift })),
      lyrics: rotatedLyrics.map(l => ({ ...l, beat: (l.beat || 0) + shift })),
    };
  }, [doc, sections, chords, lyrics, totalBeats, cycles, sideBeats]);

  const contentRef = useRef<HTMLDivElement | null>(null);
  const viewBeat = useMemo(() => normalizeBeat(playhead), [normalizeBeat, playhead]);

  useEffect(() => {
    const el = contentRef.current;
    if (!el) return;
    const center = window.innerWidth / 2;
    el.style.transform = `translateX(${center - (viewBeat + sideBeats) * zoom}px)`;
  }, [viewBeat, sideBeats, zoom]);

  // --- Consolidated Event Handlers ---
  useEffect(() => {
    const handleInteractionStart = (clientX: number) => {
      setIsDragging(true);
      setLastInteractionX(clientX);
    };

    const handleInteractionMove = (clientX: number) => {
      setLastInteractionX(prevX => {
        if (prevX === 0) return clientX; // Initial move after start
        const deltaX = prevX - clientX; // Reversed for natural feel
        const deltaBeats = deltaX / zoom;
        setPlayhead(p => normalizeBeat(p + deltaBeats));
        return clientX;
      });
    };

    const handleInteractionEnd = () => {
      setIsDragging(false);
      setLastInteractionX(0);
    };

    const handleMouseDown = (e: MouseEvent) => {
      e.preventDefault();
      handleInteractionStart(e.clientX);
    };

    const handleMouseMove = (e: MouseEvent) => {
      if (isDragging) {
        e.preventDefault();
        handleInteractionMove(e.clientX);
      }
    };

    const handleMouseUp = (e: MouseEvent) => {
      if (isDragging) {
        e.preventDefault();
        handleInteractionEnd();
      }
    };

    const handleWheel = (e: WheelEvent) => {
      e.preventDefault();
      const deltaBeats = (e.deltaX / zoom) * 0.5 + (e.deltaY / zoom) * 0.1;
      setPlayhead(prev => normalizeBeat(prev + deltaBeats));
    };

    const handleTouchStart = (e: TouchEvent) => {
      if (e.touches.length === 1) {
        e.preventDefault();
        handleInteractionStart(e.touches[0].clientX);
      }
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (e.touches.length === 1 && isDragging) {
        e.preventDefault();
        handleInteractionMove(e.touches[0].clientX);
      }
    };

    const handleTouchEnd = (e: TouchEvent) => {
      if (isDragging) {
        e.preventDefault();
        handleInteractionEnd();
      }
    };

    const eventOptions = { passive: false };
    window.addEventListener('mousedown', handleMouseDown, eventOptions);
    window.addEventListener('mousemove', handleMouseMove, eventOptions);
    window.addEventListener('mouseup', handleMouseUp, eventOptions);
    window.addEventListener('wheel', handleWheel, eventOptions);
    window.addEventListener('touchstart', handleTouchStart, eventOptions);
    window.addEventListener('touchmove', handleTouchMove, eventOptions);
    window.addEventListener('touchend', handleTouchEnd, eventOptions);

    return () => {
      window.removeEventListener('mousedown', handleMouseDown);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('wheel', handleWheel);
      window.removeEventListener('touchstart', handleTouchStart);
      window.removeEventListener('touchmove', handleTouchMove);
      window.removeEventListener('touchend', handleTouchEnd);
    };
  }, [isDragging, zoom, normalizeBeat]);


  // --- Lyrics Search and Attach Logic ---
  const [searching, setSearching] = useState(false);
  const [searchErr, setSearchErr] = useState<string | null>(null);
  const [foundLyrics, setFoundLyrics] = useState<any>(null);

  const searchLyrics = useCallback(async () => {
    if (!doc) return;
    setSearching(true);
    setSearchErr(null);
    setFoundLyrics(null);
    try {
      const cleanTitle = (doc?.title || "")
        .replace(/^\d+\s*-\s*/, '')
        .replace(/_/g, ' ');

      console.log(`Searching for lyrics with cleaned title: "${cleanTitle}"`);
      const title = encodeURIComponent(cleanTitle);
      const artist = encodeURIComponent(doc?.artist || "");
      const res = await fetch(`${apiBase}/v1/lyrics/search?title=${title}&artist=${artist}`);

      if (!res.ok) {
        const errorText = await res.text();
        console.error("Lyric search failed:", res.status, errorText);
        throw new Error(`[${res.status}] ${errorText}`);
      }
      const data = await res.json();
      console.log("--- Lyrics Search Result ---", data);
      if (data.matched && data.lines?.length > 0) {
        setFoundLyrics(data);
      } else {
        setSearchErr("No matching lyrics found.");
      }
    } catch (e: any) {
      console.error("An error occurred during lyric search:", e);
      setSearchErr(e.message || String(e));
    } finally {
      setSearching(false);
    }
  }, [doc, apiBase]);

  const attachLyrics = useCallback(async (lyricsToAttach: any) => {
    if (!id || !lyricsToAttach) return;
    const sid = Array.isArray(id) ? id[0] : id;
    console.log("--- Attaching lyrics... ---");
    try {
      const res = await fetch(`${apiBase}/v1/songs/${sid}/attach-lyrics`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ lines: lyricsToAttach.lines, mode: "append" }),
      });
      if (!res.ok) throw new Error(await res.text());
      await mutate(); // Refresh the song doc
      setFoundLyrics(null);
      console.log("--- Lyrics attached successfully ---");
    } catch (e: any) {
      alert(`Attach failed: ${String(e)}`);
      console.error("Attach failed:", e);
    }
  }, [id, apiBase, mutate]);

  useEffect(() => {
    if (doc && !lyrics.length && !foundLyrics && !searching && !searchErr) {
      searchLyrics();
    }
  }, [doc, lyrics.length, foundLyrics, searching, searchErr, searchLyrics]);

  useEffect(() => {
    if (foundLyrics) {
      attachLyrics(foundLyrics);
    }
  }, [foundLyrics, attachLyrics]);


  if (isLoading) return <div className="p-4 text-center">Loading song...</div>;
  if (error) return <div className="p-4 text-center text-red-500">Error loading song: {error.message}</div>;
  if (!doc) return <div className="p-4 text-center">Song not found.</div>;

  return (
    <div className="fixed inset-0 bg-slate-900/50 overflow-hidden select-none touch-none">
      <div className="absolute inset-0">
        <div ref={contentRef} className="relative timeline-content z-20 h-full">
          <div className="flex flex-col justify-center h-full space-y-1">
            {!!rotatingContent.sections?.length && (
              <div>
                <SectionRail sections={rotatingContent.sections} zoom={zoom} totalBeats={extendedTotalBeats} />
              </div>
            )}
            <div>
              <BarRuler beatsPerBar={beatsPerBar} totalBeats={extendedTotalBeats} zoom={zoom} />
            </div>
            <div>
              <ChordLane chords={rotatingContent.chords} zoom={zoom} beatsPerBar={beatsPerBar} totalBeats={extendedTotalBeats} />
            </div>
            {!!rotatingContent.lyrics?.length && (
              <div>
                <LyricLane lyrics={rotatingContent.lyrics} zoom={zoom} beatsPerBar={beatsPerBar} totalBeats={extendedTotalBeats} />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default SongPage;
