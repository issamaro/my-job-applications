# UX_DESIGN — setup-detects-existing-api-key

- **Date:** 2026-05-05
- **Slug:** setup-detects-existing-api-key
- **Surface:** terminal CLI (`./setup.sh`)
- **UX direction:** preserve current patterns. Only the source-of-key labels and one warning line are new.

The script is interactive but non-graphical. Keyboard navigation is just `read -r`. There is no a11y concern beyond ANSI colors already in use; we keep them and the existing `step` / `ok` / `warn` / `fail` glyph helpers (`▸ ✓ ! ✗`).

## Screens

### Screen A — preflight summary (renamed heading + source labels)

State: **success** (the only state — the script always renders preflight after install)

Existing copy (today, `setup.sh:200-204`):

```
Current configuration in ~/.zshrc:
  LLM_PROVIDER:        not set
  ANTHROPIC_API_KEY:   not set
  GEMINI_API_KEY:      not set
```

New copy (after fix):

```
Detected configuration:
  LLM_PROVIDER:        claude              (from ~/.zshrc)
  ANTHROPIC_API_KEY:   set ...AB12         (from ~/.zshenv)
  GEMINI_API_KEY:      not set

  Write target: ~/.zshrc
```

State variations:

- **Empty** (fresh install): each row shows `not set`; no `(from …)` annotation. `Write target: ~/.zshrc` still shown.
- **Loading**: not applicable — preflight is synchronous and prints in <50ms.
- **Success** (key in env only): row reads `set ...AB12         (live env only)`.
- **Error**: covered by existing `find_chain_warning` (symlink chain → orange warn line). No new error states.

### Screen B — provider menu

Unchanged. (`setup.sh:222-253`.) Mentioned only because it follows the preflight on the same scroll.

### Screen C — keep / replace / cancel menu (message text updated)

Existing copy (today, `setup.sh:259`):

```
You already have a ANTHROPIC_API_KEY in ~/.zshrc (ends in …AB12).
  [1] Keep the existing key
  [2] Replace it with a new key
  [3] Cancel setup
Choice [1/2/3]:
```

New copy:

```
You already have a ANTHROPIC_API_KEY (from ~/.zshenv, ends in …AB12).
  [1] Keep the existing key
  [2] Replace it with a new key
  [3] Cancel setup
Choice [1/2/3]:
```

State variations:

- **Source = rc target** (e.g. `~/.zshrc`): label reads `(from ~/.zshrc, ends in …AB12)`.
- **Source = different login file**: label reads `(from ~/.zshenv, ends in …AB12)`.
- **Source = live env only**: label reads `(from live env only, ends in …AB12)`.
- **Error**: invalid choice falls to default `keep` (existing behavior; unchanged).

### Screen D — replace warning (new, conditional)

Triggered only when the user picks `[2] Replace` AND the source file ≠ rc_target.

```
! Existing key is exported from ~/.zshenv. New key will be written to ~/.zshrc.
!   You may end up with two `export ANTHROPIC_API_KEY` lines across files.
```

(`!` is the existing yellow `warn` glyph.)

State variations:

- **Skipped** when source = rc_target (no warning needed).
- **Skipped** when source = `live env only` (no source file exists; the warning would be misleading). Instead the existing flow simply writes to rc_target.

### Screen E — paste prompt

Unchanged (`setup.sh:283`). Reached only when no key is detected anywhere — i.e. **after** the new detection has confirmed the key is genuinely absent.

## Keyboard map

Unchanged across all screens — single-character `read -r` answers, Enter to submit, Ctrl-C cancels via the existing `INT` trap (`setup.sh:413`).

## Copy specifics (no new strings beyond these)

- Heading change: `Current configuration in <path>:` → `Detected configuration:`
- New per-row suffix: `(from <path>)` or `(live env only)` — appended after the existing right-padded value.
- New write-target line: `  Write target: <rc_target>` printed once below the three rows.
- New warn line(s) on cross-file replace, copy as in Screen D.
- Updated keep/replace/cancel header line, copy as in Screen C.

No emojis are introduced. ANSI palette stays as-is (`BOLD`, `BLUE`, `GREEN`, `YELLOW`, `RED`, `NC`).

## Out of scope

- New menu layouts.
- Splash screens, progress bars, multi-column layout.
- Internationalization.
