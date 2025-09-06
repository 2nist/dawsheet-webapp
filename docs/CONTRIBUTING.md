# Contributing – UI Styling Rules

This repository enforces strict design-token usage for all UI styling.

Non-negotiable rules for UI code:

- Do not hardcode colors, fonts, radii, spacing, or shadows in components.
- Always source visual props from CSS variables defined in `web/src/styles/tokens.css`.
- Tailwind utilities must map to tokens via `web/tailwind.config.ts` (e.g., colors, radius, spacing, shadows, fonts).
- Any new tokens or components must be previewed in `web/pages/design.tsx` (Design Workbench).
- PRs that bypass tokens or introduce hardcoded values will be rejected.

Styling-only PRs

- Considered safe to merge to main if they only change:
  - `web/tailwind.config.ts`
  - `web/src/styles/tokens.css`
  - `web/src/styles/globals.css`
  - `web/pages/design.tsx` (or design pages)
- They must not alter backend logic or API contracts.

PR checklist (UI)

- [ ] All colors/spacing/radius/shadows/fonts come from tokens.
- [ ] Tailwind classes resolve to mapped tokens (or use CSS vars directly when necessary).
- [ ] New tokens/components have examples in `/design`.
- [ ] No legacy contract drift (SongDoc v1) if backend is touched.
- [ ] Tests & small UI checkpoints are included when functionality changes.

If in doubt, add a token and preview it in `/design` before using it.
