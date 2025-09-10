# Timeline Musician Workflow

## What Changed

Adds multi-row lyric wrapping with dynamic lane height, guided chord editing (root/quality/slash + shapes), Euclid rhythm lane (steps/pulses/rotation with drag & toggle), and Save Draft button posting current timeline state. Styling updated to favor design tokens and Tailwind utilities.

## How to Test

1. Start stack (API + web) then open /songs/{id}/timeline (replace {id}).
2. Zoom slider: adjust; lyrics reflow into multiple rows with no overlaps.
3. Click a lyric: selection ring shows; double-click to edit text inline via prompt.
4. Click a chord: guided edit panel + Shapes button appears. Change root/quality or add /bass. Press Escape to cancel edits (close popover), Enter inside input applies.
5. Add Euclid: use any add control (if exposed) or preset; verify dots = steps; drag Rotate button horizontally to rotate; click dots (when implemented) to toggle active state.
6. Save Draft: click Save Draft; toast shows timestamped confirmation; while saving button is disabled. Retry after success.
7. Inspect /design for any new tokens (if added this iteration) and confirm no raw hex codes in modified components.

## Feature Flags / Toggles

Currently none required; new lanes/components auto-render when data present.

## Styling Guardrails

Use Tailwind spacing/size utilities and shared CSS variables from tokens.css. Avoid raw hex colors or inline pixel values except when computing dynamic geometry (positions, widths). Colors use semantic classes or var(--token) references. Heights derived from row constants rather than hard-coded magic numbers.
