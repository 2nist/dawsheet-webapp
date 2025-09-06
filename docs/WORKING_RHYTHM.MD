# Working Rhythm (DAWSheet)

## Roles
- Matthew (owner): tweaks styling, runs UI checkpoints, approves next step.
- Agent(s): ship small PRs, keep to milestones, update integration log.
- AI advocate: reviews “Project Health” + UI checkpoint notes and issues next steps.

## Cycle (each PR)
1) Agent opens a small PR with tests + a tiny UI surface.
2) Matthew runs it locally and performs the UI Checkpoint (below, 60–180s).
3) Matthew posts a short status in the PR or a comment here.
4) AI advocate replies with accept/fix + the exact next PR scope.

## Local run (dev)
- Backend: `uvicorn backend.app.main:app --reload --port 8000`
- Frontend: `npm run dev` (3000)
- WebSocket (stub): served by backend at `/ws/bridge`

## UI Checkpoints (what Matthew does)

### M1: Lyrics Parse
- Go to **Import** page.
- Drag `.lrc` and `.txt` samples.
- Expect: line count + first 10 lines; timestamps for `.lrc`, none for `.txt`.

### M2: Import Pipeline
- Upload 5 mixed files (`.lrc`, `.lab`, `.json`).
- Expect: per-file progress → OK/ERR table; “Preview” links open.

### M3: Analysis + Song Page
- Click **Analyze** on a preview → open **Song** page.
- Expect: section chips, mini timeline stripe, chord lane.

### M4: Export + Preview (WS)
- Click **Export Pack** → unzip → import `song.mid` into DAW → markers visible.
- Click **Preview (Local)** → UI logs an **ACK**.

## What to Post (copy/paste template)
