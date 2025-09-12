from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, Query
from fastapi.responses import JSONResponse
from typing import Optional
import json

from ..parser import parse_songs
from ..importers import import_json_file, import_midi_file, import_mp3_file, _looks_like_jcrd  # type: ignore[attr-defined]
from ..legacy.ingest.lyrics import parse_lyrics_payload
from ..services.lyrics_providers.lrclib import search_timestamped_lyrics
from ..utils.align import merge_jcrd_with_lyrics, chords_only_text
from ..config import settings


router = APIRouter(prefix="/import", tags=["import"])


def _dedupe_songs(items: list[dict]) -> list[dict]:
	seen: set[tuple[str, str]] = set()
	out: list[dict] = []
	for s in items:
		key = (s.get("title", "").strip().lower(), s.get("artist", "").strip().lower())
		if key in seen:
			continue
		seen.add(key)
		out.append(s)
	return out


@router.post("/multi")
async def import_multi(
	files: list[UploadFile] = File(...),
	include_lyrics: Optional[bool] = Query(default=True),
):
	"""Accept a batch of files (.json, .mid, .midi, .mp3, .txt, .lrc, .vtt, .csv)
	and return a summary + normalized song list.
	"""
	songs: list[dict] = []
	success: list[str] = []
	skipped: list[str] = []
	errors: list[str] = []

	for f in files:
		name = (f.filename or "").lower()
		try:
			data = await f.read()
			if name.endswith((".json",)):
				# Try auto-combine with lyrics for JCRD JSON if enabled
				did_auto = False
				try:
					obj = json.loads(data.decode("utf-8", errors="replace"))
					if isinstance(obj, dict) and _looks_like_jcrd(obj):
						if include_lyrics and settings.LYRICS_PROVIDER_ENABLED:
							meta = obj.get("metadata") or {}
							title = (meta.get("title") or obj.get("title") or (f.filename or name).rsplit(".", 1)[0]).strip()
							artist = (meta.get("artist") or obj.get("artist") or "").strip()
							lines = None
							if title:
								try:
									# Attempt lyrics search even if artist is missing; provider will best-match
									fetched = await search_timestamped_lyrics(title=title, artist=artist, timeout=3.0)
									lines = (fetched or {}).get("lines") if isinstance(fetched, dict) else None
								except Exception:
									lines = None
							if lines:
								merged = merge_jcrd_with_lyrics(obj, lines)
								songs.append({"title": title or "Untitled", "artist": artist, "content": merged.get("content", "")})
								did_auto = True
						if not did_auto and (include_lyrics is False):
							co = chords_only_text(obj)
							meta = obj.get("metadata") or {}
							title = (meta.get("title") or obj.get("title") or (f.filename or name).rsplit(".", 1)[0]).strip()
							artist = (meta.get("artist") or obj.get("artist") or "").strip()
							songs.append({"title": title or "Untitled", "artist": artist, "content": co.get("content", "")})
							did_auto = True
				except Exception:
					did_auto = False

				if not did_auto:
					s, w = import_json_file(f.filename or "", data)
					songs.extend(s)
					errors.extend(w)
				success.append(f.filename or name)
			elif name.endswith((".mid", ".midi")):
				s, w = import_midi_file(f.filename or "", data)
				songs.extend(s)
				success.append(f.filename or name)
				errors.extend(w)
			elif name.endswith((".mp3",)):
				s, w = import_mp3_file(f.filename or "", data)
				songs.extend(s)
				success.append(f.filename or name)
				errors.extend(w)
			elif name.endswith((".txt", ".lrc", ".vtt", ".csv")):
				text = data.decode("utf-8", errors="replace")
				# Convert lyric lines to one pseudo-song content
				lines = parse_lyrics_payload(text, f.filename or name)
				content = "\n".join([l.text for l in lines])
				title = (f.filename or name).rsplit(".", 1)[0]
				songs.append({"title": title, "artist": "", "content": content})
				success.append(f.filename or name)
			else:
				# Fallback: try general text parser
				text = data.decode("utf-8", errors="replace")
				s = parse_songs(text)
				if s:
					songs.extend(s)
					success.append(f.filename or name)
				else:
					skipped.append(f.filename or name)
		except Exception as e:  # noqa: BLE001
			errors.append(f"{f.filename or name}: {e}")

	deduped = _dedupe_songs(songs)

	return JSONResponse(
		{
			"ok": True,
			"counts": {
				"input_files": len(files),
				"songs": len(deduped),
			},
			"success": success,
			"skipped": skipped,
			"errors": errors or None,
			"songs": deduped,
		}
	)
