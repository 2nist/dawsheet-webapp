from __future__ import annotations

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from ..parser import parse_songs
from ..importers import import_json_file, import_midi_file, import_mp3_file
from ..legacy.ingest.lyrics import parse_lyrics_payload


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
async def import_multi(files: list[UploadFile] = File(...)):
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
				s, w = import_json_file(f.filename or "", data)
				songs.extend(s)
				success.append(f.filename or name)
				errors.extend(w)
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
