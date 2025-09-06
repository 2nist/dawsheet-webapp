## Summary

Describe what changed and why.

## UI Styling Compliance (required)

- [ ] No hardcoded colors/fonts/radius/spacing/shadows in components.
- [ ] All styling uses tokens from `web/src/styles/tokens.css` (via Tailwind mapping or CSS vars).
- [ ] New tokens/components are previewed in `web/pages/design.tsx`.

## Scope

- [ ] Styling-only PR (safe to merge to main)
  - Files touched are limited to Tailwind config, tokens, globals, or design pages.
- [ ] Functional changes (include tests and tiny UI checkpoint)

## Testing

- [ ] Ran `docker compose build web && docker compose up -d web`
- [ ] Verified `/design` renders and previews tokens

## Screenshots (optional)
