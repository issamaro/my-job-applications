feature: setup-detects-existing-api-key
date: 2026-05-05
status: READY
playwright: skipped

---

## Playwright

skipped — surface is terminal CLI (`./setup.sh`); no web UI, no playwright.config present in scope.

---

## Manual checklist

Steps map to CHECKLIST Section "Manual verification record" (lines 140-146) plus the UX states in UX_DESIGN Screens A, C, D.

- Run `grep -l ANTHROPIC_API_KEY ~/.zshenv ~/.zprofile ~/.zshrc ~/.profile 2>/dev/null` and note which file is printed — this is the reproduction file; record it before continuing.
- Run `printenv ANTHROPIC_API_KEY` and confirm a non-empty value is returned (key is live in the environment).
- Run `./setup.sh` WITHOUT the fix applied (baseline): confirm the preflight block does NOT show `(from <reproduction file>)` next to `ANTHROPIC_API_KEY` — this records the failing case.
- Apply the fix, then run `./setup.sh` again: confirm the preflight heading reads `Detected configuration:` (not `Current configuration in …:`).
- In the same run, confirm the `ANTHROPIC_API_KEY` row reads `set ...XXXX         (from <tilde-path to reproduction file>)` where the last four chars of the key are visible.
- Confirm the `Write target: ~/.zshrc` line appears below the three variable rows.
- When the keep/replace/cancel menu appears, confirm the header reads `You already have a ANTHROPIC_API_KEY (from <tilde-path>, ends in …XXXX).` — source and suffix are on one combined label, not two separate parenthesized clauses.
- Pick `[1] Keep` — confirm setup completes without adding a duplicate `export ANTHROPIC_API_KEY` line to `~/.zshrc` (run `grep -c ANTHROPIC_API_KEY ~/.zshrc` before and after; count must not increase).
- Run `./setup.sh` a second time — confirm the preflight output is identical to the previous run (idempotent).
- If you want to verify Screen D: in a scratch run, pick `[2] Replace` when the source file is different from `~/.zshrc` — confirm both warn lines appear: `! Existing key is exported from <source>.` and `!   You may end up with two export ANTHROPIC_API_KEY lines across files.`
- Record the reproduction file name (from step 1) in the change log entry for this feature.

---

## Decisions

none — parent collects user verdict.
