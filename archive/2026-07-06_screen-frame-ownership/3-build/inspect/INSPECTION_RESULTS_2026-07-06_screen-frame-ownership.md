feature: screen-frame-ownership
date: 2026-07-06
status: READY
playwright: skipped

## Playwright

No `playwright.config.*` at project root (this repo drives Playwright
through `pytest-playwright`/`uv run python -m playwright`, not the JS test
runner), so step 2's `npx playwright test` path does not apply.

Attempted an ad hoc Python Playwright smoke instead (static server via
`python3 -m http.server --directory public`, viewport 1512x860,
`uv run python -m playwright`, version 1.58.0 confirmed installed). The
browser binary itself is missing:

```
playwright._impl._errors.Error: BrowserType.launch: Executable doesn't exist
at .../ms-playwright/chromium_headless_shell-1208/chrome-headless-shell-mac-arm64/chrome-headless-shell
```

Fixing this requires `playwright install`, which is a browser-binary
download — out of scope for a read-only inspector (no install actions).
Automated smoke is therefore skipped; all geometry bullets below are
manual. This does not block — the checklist's own
`tests/test_generator_frame.py` and `tests/test_editorial_page_frame`
already cover the computed-style assertions under `pytest`; this
inspection's job is the human-eyeball layer pytest cannot do (visual
"comfortable margins," "nothing edge-flush," and the real-data resume
preview).

## Manual checklist

- Serve the app (`python3 -m http.server <port> --directory public`),
  open it at 1512x860, land on the Tailor CV tab (`[data-slot-id="tailor"]`)
  before generating anything. Eyeball the input view: confirm the
  job-description form sits in a centered column with comfortable margins
  on both sides, nothing touches the viewport edge, and the saved-jobs
  list renders inside that same column rather than spanning full-width.
- With the Tailor CV input view still open, paste 100+ characters into the
  job-description field and click Generate. The call will fail (no backend
  running) — that's expected. Confirm the loading state you see for that
  moment (or, if it flashes past, judge the input view's framing) is still
  inside the same centered ~800px frame — no shift to edge-flush layout.
- Open a resume preview from your own local app with real generated data
  (not the static bundle used above — this needs an actual generated
  resume, so it cannot be automated against the static server). Confirm
  the geometry is unchanged from before this change: full-bleed workspace,
  `--d-pad` breathing room around content, no new outer gutter or
  container has appeared. You are the inspector of record for this bullet.
- Open the Profile screen and confirm it still renders unchanged: the
  `.editor-column` content caps at roughly 940px, centered, with no new
  outer frame or gutter introduced by the shell change.

## Decisions

none — parent collects user verdict
