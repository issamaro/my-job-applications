# CODEMAP — where things live

Path-discovery aid for subagents. Read before searching the tree. Hand-curated;
update when shape changes. Everything not listed here is recoverable from `ls`.

`{slug}` = domain noun, snake on filesystem (`jobs`, `users`, `education`,
`languages`, `photos`, `projects`, `resumes`, `skills`, `work_experiences`,
`profile_import`).

## Entry points

- `main.py` — FastAPI app: mounts `routes/*`, serves `public/build/`.
- `dev.sh` — develop (watch): `bun run dev` (Rollup watcher) + `uv run uvicorn main:app --reload` on :8000.
- `run.sh` — run (serve): `bun run build` once if missing + `uv run uvicorn main:app` on 127.0.0.1:8000.
- `setup.sh` — Install deps, build bundle, write LLM provider + API key to `.env`.
- `rollup.config.js` — Bundles `src/main.js` → `public/build/bundle.{js,css}`.

## Pairing conventions

```
routes/{slug}.py              ⇄  tests/test_{slug}.py             (always paired)
routes/{slug}.py              →  services/{slug}.py               (most, not all)
src/components/{Name}.svelte  ↔  tests/test_{name_snake}.py       (selective)
templates/resume_{variant}.html  →  consumed by services/pdf_generator.py
```

## Cross-cutting modules

- `settings.py` — Single config reader: process-env → `.env` → defaults (`LLM_PROVIDER`, API keys, models, `DATABASE`). Written by `setup.sh`.
- `schemas.py` — Pydantic shapes shared by every route.
- `database.py` — SQLite engine + session shared by every service.
- `services/llm/{provider}.py` — LLM provider implementations (`claude`, `gemini`); selection via `services/llm/factory.py`.
- `services/translations.py` — i18n strings consumed by routes + `resume_generator.py`.
- `src/lib/profileStore.svelte.js` — Shared profile state (load, save, initials).
- `src/lib/api.js` — Frontend fetch wrapper.
- `templates/resume_base.css` — Shared CSS for all `resume_*.html` templates.
- `translations/{en,fr,nl}.json` — i18n source files.
