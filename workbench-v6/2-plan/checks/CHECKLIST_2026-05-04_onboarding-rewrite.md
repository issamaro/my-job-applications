---
feature: onboarding-rewrite
date: 2026-05-04
total_checkboxes: 86
derived_from: FEATURE_SPEC_2026-05-04_onboarding-rewrite.md, UX_DESIGN_2026-05-04_onboarding-rewrite.md, IMPL_PLAN_2026-05-04_onboarding-rewrite.md, .python-version, pyproject.toml, package.json
---

# Verification Checklist — Onboarding Rewrite

---

## Section 0 — Ecosystem

- [ ] Runtime version pinned: `.python-version` = `3.13` (verify: `cat .python-version`)  → source: IMPL_PLAN "Library / runtime research" section; `.python-version` file present at repo root
- [ ] `pyproject.toml` is present and unmodified by this feature (no new deps added)  → source: IMPL_PLAN §"Files NOT touched" — "pyproject.toml … no dependency changes"
- [ ] `package.json` is present and unmodified by this feature (no new deps added)  → source: IMPL_PLAN §"Files NOT touched" — "package.json … no dependency changes"
- [ ] Virtual environment created and activated (verify: `uv sync` exits 0)  → source: IMPL_PLAN §"Test plan" — "`uv run pytest` — full existing suite must pass"

---

## Section 1 — Dependencies

n/a — no new library dependencies introduced. IMPL_PLAN §"Library / runtime research — skipped (with rationale)" documents that `gh`, `uv run uvicorn`, and POSIX builtins require no new entries in any manifest. `pyproject.toml` and `package.json` are explicitly listed as untouched.

---

## Section 2 — Syntax / Implementation Patterns

Derived from IMPL_PLAN §"Watch-item decisions" and §"File 2 — setup.sh".

### setup.sh — shell detection

- [ ] `find_current_shell` uses `ps -p $$ -o comm=` (not `$SHELL`) and pattern-matches `*zsh` / `*bash` via a `case` statement  → source: IMPL_PLAN §"Bonus — ps -p $$ -o comm= portability" and function table
- [ ] `find_current_shell` falls back to `zsh` when the `case` default (`*`) fires  → source: IMPL_PLAN §"Bonus" code snippet: `*) printf 'zsh' ;; # fallback (default macOS)`

### setup.sh — symlink handling (W1)

- [ ] `read_rc_path` calls `readlink` with POSIX-compatible form (no `-f` flag) and falls back to the literal path when the rc is not a symlink  → source: IMPL_PLAN §"W1" pseudocode (`if [[ -L "$rc_path" ]]; then readlink ... else rc_target="$rc_path"`)
- [ ] `read_rc_path` converts a relative `readlink` target to an absolute path via `dirname "$rc_path"` BEFORE returning  → source: IMPL_PLAN §"W1": `if [[ "$rc_target" != /* ]]; then rc_target="$(dirname "$rc_path")/$rc_target"; fi`; relative-target reproduction confirmed under bash 3.2.57
- [ ] Pre-flight summary prints `Writing to: <rc_target>` and, when `rc_target != rc_path`, additionally prints `(resolved from symlink at ~/.zshrc)`  → source: IMPL_PLAN §"W1": "Pre-flight summary prints `Writing to: <rc_target>`"
- [ ] Atomic `mv` in `write_rc_atomic` targets `$rc_target`, not the literal `~/.zshrc` path  → source: IMPL_PLAN §"W1": "All in-memory transform reads from `$rc_target`; the atomic `mv` writes to `$rc_target`"
- [ ] `find_chain_warning` is called once during pre-flight; if `$rc_target` is itself a symlink (chained dotfile setup), it emits a yellow ⚠ note via `warn` and setup proceeds — no refusal  → source: IMPL_PLAN §"W1 — Chained-symlink detection (m4 fix)": "Continue normally — do NOT refuse"

### setup.sh — duplicate collapse (W2)

- [ ] `create_rc_content` uses `awk` with `next` rules to delete ALL matching `^export LLM_PROVIDER=` lines before appending one canonical line  → source: IMPL_PLAN §"Sketch of create_rc_content": "awk … `$0 ~ "^export " vp "="` { next }"
- [ ] `create_rc_content` uses `awk` with `next` rules to delete ALL matching `^export <chosen_key_var>=` lines before appending one canonical line  → source: IMPL_PLAN §"Sketch of create_rc_content": "`$0 ~ "^export " vk "="` { next }"
- [ ] When user chose "Keep existing", `create_rc_content` re-emits the last matching `^export <VAR>=` line (last-wins), not the first  → source: IMPL_PLAN §"W2 — Duplicate-collapse pick policy": "last-wins … value from the last matching line"
- [ ] The OTHER provider's `*_API_KEY` lines are never mentioned in the `awk` filter and therefore survive untouched  → source: IMPL_PLAN §"Sketch": "The OTHER provider's `*_API_KEY` lines are NEVER mentioned in awk → preserved untouched (Scenario 2b)"

### setup.sh — short-key tail display (W3)

- [ ] `render_key_suffix` branches on key length: empty → `"(empty / suspicious — will replace)"`, length 1–3 → `"(ends in …<all-chars>)"`, length ≥ 4 → `"(ends in …<last-4-chars>)"`  → source: IMPL_PLAN §"W3 — Short-key tail display": three-branch decision table

### setup.sh — atomic write

- [ ] `write_rc_atomic` writes to `<rc_target>.tmp.$$` (pid-suffixed temp file) before `mv`  → source: IMPL_PLAN §"Atomic write" code sketch: `local tmp="${rc_target}.tmp.$$"`
- [ ] `write_rc_atomic` uses `printf '%s'` (no trailing `\n`) so a phantom blank line does not grow on every run  → source: IMPL_PLAN §"Atomic write": "Note: `printf '%s'` (no `\n`) … avoids a phantom blank line"
- [ ] `write_rc_atomic` removes the temp file with `rm -f` on both write-failure and mv-failure paths before returning 1  → source: IMPL_PLAN §"Atomic write" code sketch: `rm -f "$tmp" 2>/dev/null` in both failure branches
- [ ] After a successful `mv`, `write_rc_atomic` does NOT export env vars (exporting is delegated to `write_session_vars`)  → source: IMPL_PLAN §"Atomic-commit phase" step 3: "`write_session_vars` called after `write_rc_atomic` succeeds"
- [ ] `write_rc_atomic` sets `umask 077` before creating the temp file and restores the prior umask before `mv`  → source: IMPL_PLAN §"Atomic write": umask 077 + restore via `prev_umask`
- [ ] `write_rc_atomic` reads the original rc's mode via `stat -f '%Lp'` (BSD) with `stat -c '%a'` (GNU) fallback and `chmod`s the temp to match before `mv`  → source: IMPL_PLAN §"Atomic write": `original_mode` block
- [ ] If the rc file did NOT pre-exist, the new file ends up at mode `0600` (from the umask 077 floor)  → source: IMPL_PLAN §"Mode-preservation contract" table row "absent → 0600"
- [ ] If the rc file pre-existed at mode `0600`, after `setup.sh` it is still `0600` (no permission widening regression)  → source: IMPL_PLAN §"Mode-preservation contract" table row "0600 → 0600"; M3 plan-reviewer finding

### setup.sh — bash 3.2 portability

- [ ] No `${var^^}` uppercase expansion appears anywhere in setup.sh; all upper-casing uses inline `printf '%s' … | tr '[:lower:]' '[:upper:]'`  → source: IMPL_PLAN §"ACTUAL DECISION on upcase": "inline `tr` calls … no new function, no rule violation"
- [ ] No associative arrays (`declare -A`) are used  → source: IMPL_PLAN §"Risks — P3": "plan avoids … `case` for matching, no associative arrays"

### setup.sh — Lean Code compliance

- [ ] Every new bash function name starts with one of the nine permitted verbs (read, write, create, delete, update, find, check, parse, render)  → source: CLAUDE.md Lean Code verb table; IMPL_PLAN §"New functions to add" (revised) function table
- [ ] No function name exceeds verb + three words  → source: CLAUDE.md "Function naming — Maximum three words after the verb"
- [ ] No abbreviations in any function or variable name added by this feature  → source: CLAUDE.md "No abbreviations anywhere in names"
- [ ] No inline comments appear in setup.sh below the two-line file header  → source: CLAUDE.md "After the header: ZERO comments"
- [ ] `setup.sh` file header is exactly: shebang line, `# MyCV — Setup`, `# Scope: Install dependencies and write LLM provider + API key into the user's shell-rc atomically.`  → source: IMPL_PLAN §"File header": three-line header spec
- [ ] `update_provider_and_key` is the only function that orchestrates phase 1 → phase 2; all other functions do exactly one job  → source: IMPL_PLAN §"New functions to add" (revised): "`update_provider_and_key` — Top-level orchestration"

### dev.sh — uvicorn invocation

- [ ] `dev.sh` line 71 reads `uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000 &` (not bare `uvicorn`)  → source: IMPL_PLAN §"File 3 — dev.sh": "L71 — change `uvicorn …` → `uv run uvicorn …`"
- [ ] `dev.sh` no longer contains the `if [ -d ".venv" ]; then source .venv/bin/activate; fi` block (current L37–L41)  → source: IMPL_PLAN §"File 3 — Remove activate block (m8 fix)": "delete current L37–L41"
- [ ] After `dev.sh` runs, `env | grep VIRTUAL_ENV` from a separate shell does NOT show a stale path pointing at the project's pre-`mv` location (regression check for m8)  → source: IMPL_PLAN §"File 3 — m8 fix": "stale-path footgun at its source"

### dev.sh — provider banner

- [ ] A line `echo -e "${GREEN}Using LLM provider: ${YELLOW}${LLM_PROVIDER:-claude (default)}${NC}"` appears in dev.sh BEFORE the `# Start Rollup/Svelte watcher...` comment (so the comment stays attached to its echo) and BEFORE the uvicorn invocation  → source: IMPL_PLAN §"File 3": "Insert before L47 (after the uv sync block ends, before the Svelte-watcher comment)"
- [ ] `services/llm/factory.py` line 43 is NOT modified (intentional duplication per R6)  → source: IMPL_PLAN §"File 3 — Risk R6": "explicitly do NOT touch `services/llm/factory.py` line 43"

---

## Section 3 — UX States

Derived from UX_DESIGN §"Surface A — README.md", §"Surface B — setup.sh", §"Surface C — dev.sh".

### README.md (Surface A)

- [ ] README contains no `localhost:5173` mentions (verify: `grep "localhost:" README.md` shows only `:8000` matches)  → source: UX_DESIGN §"Copy guidelines": "The phrase `http://localhost:8000` appears verbatim in section 5 and nowhere else [re: 5173]"
- [ ] README contains no `MyCV-2` mentions (verify: `grep -ri "MyCV-2" README.md` returns zero hits)  → source: UX_DESIGN §"Copy guidelines": "No 'MyCV-2' anywhere"
- [ ] §2 "Authenticate to GitHub" section exists and appears BEFORE §3 "Clone the project"  → source: UX_DESIGN §"Section list" items 3 and 4
- [ ] §2 includes the `gh auth login` command in a fenced bash code block  → source: UX_DESIGN §"State coverage per section — 2 — Auth": "run `gh auth login`, choose GitHub.com → HTTPS → Login with a web browser"
- [ ] §2 shows the success state: terminal prints `✓ Logged in as <username>`  → source: UX_DESIGN §"State coverage — 2 — Auth — Success state"
- [ ] §2 documents error recovery: if `gh` not on PATH, README points back to Section 1  → source: UX_DESIGN §"State coverage — 2 — Auth — Error state"
- [ ] §3 "Clone the project" uses `gh repo clone issamaro/my-job-applications` and the subsequent `cd` line reads `cd my-job-applications`  → source: UX_DESIGN §"Section list" item 4; FEATURE_SPEC Scenario 5
- [ ] §3 documents the "directory already exists" error state  → source: UX_DESIGN §"State coverage — 3 — Clone — Error state"
- [ ] §4 "Run setup" mentions that cancelling at any prompt is safe (no shell-rc changes)  → source: UX_DESIGN §"State coverage — 4 — Setup": "User cancels at any prompt → setup.sh exits 0 with no shell-rc changes"
- [ ] §5 "Start the app" references `http://localhost:8000` verbatim  → source: UX_DESIGN §"State coverage — 5 — Run — Success state": "dev.sh banner shows `App running at: http://localhost:8000`"
- [ ] §5 documents the error state for stale terminal env (provider/key mismatch ValueError)  → source: UX_DESIGN §"State coverage — 5 — Run — Error — provider/key mismatch"
- [ ] §6 "If something goes wrong" exists with exactly four troubleshooting items  → source: UX_DESIGN §"Troubleshooting copy" items 1–4
- [ ] §6 item 1 covers: "App says ANTHROPIC_API_KEY not set but I chose Gemini" with `source ~/.zshrc` / new terminal recovery  → source: UX_DESIGN §"Troubleshooting copy" item 1
- [ ] §6 item 2 covers: "`uvicorn: command not found` after mv" with `uv sync` + note that rewrite should prevent this  → source: UX_DESIGN §"Troubleshooting copy" item 2
- [ ] §6 item 3 covers: "Port 8000 already in use" with `lsof -ti:8000` manual recovery  → source: UX_DESIGN §"Troubleshooting copy" item 3
- [ ] §6 item 4 covers: "I had LLM_PROVIDER manually exported from before" with self-healing re-run instruction  → source: UX_DESIGN §"Troubleshooting copy" item 4
- [ ] Each fenced code block in README contains ONE command (no multi-command blocks that could cause copy-paste mistakes)  → source: UX_DESIGN §"Copy guidelines": "Code blocks contain ONE command per block"
- [ ] All fenced code blocks carry ` ```bash ` language hint  → source: UX_DESIGN §"Accessibility / readability": "Code blocks have language hint (` ```bash `)"

### setup.sh (Surface B)

- [ ] `read_provider_choice` shows the detected current value next to the matching number (e.g. `[2] Gemini  (currently selected)`) when one is detected; absent when none is detected  → source: UX_DESIGN §"Provider prompt": "Detected current value shown in brackets next to the matching number if any (e.g., `[2] Gemini  (currently selected)`)"
- [ ] Pre-flight "empty" state (no vars set): summary shows `LLM_PROVIDER: not set`, `ANTHROPIC_API_KEY: not set`, `GEMINI_API_KEY: not set`  → source: UX_DESIGN §"State coverage — Empty (no LLM_PROVIDER)"
- [ ] Pre-flight "mismatch" state: yellow ⚠ line reads `Mismatch: LLM_PROVIDER says <X> but no <X>_API_KEY found. Setup will fix this.`  → source: UX_DESIGN §"Pre-flight" anomaly lines
- [ ] Pre-flight "duplicates" state: yellow ⚠ line reads `Found N duplicate <VAR> lines — will collapse to one on save.`  → source: UX_DESIGN §"Pre-flight" anomaly lines
- [ ] Case A "Keep existing" path: prints `✓ Kept existing <VAR>.` then proceeds to done banner  → source: UX_DESIGN §"State coverage — Case A: Keep existing"
- [ ] Case A "Cancel" path: prints `Setup cancelled. No changes made.` and exits 0  → source: UX_DESIGN §"State coverage — Case A: Cancel"
- [ ] Case B empty-input loop: re-prompts with `No key entered. Paste a key, or type 'cancel' to abort.`  → source: UX_DESIGN §"Key prompt — Case B": "Empty input (just Enter) → re-prompt with: `No key entered. …`"
- [ ] `read_new_key` quote-injection guard uses pattern `[[ "$answer" == *'"'* || "$answer" == *\\* ]]` (second branch UNQUOTED so bash de-escapes `\\` to a single-backslash glob); a one-backslash paste like `hello\bye` MUST trigger the re-prompt  → source: IMPL_PLAN §"Quote-injection guard in read_new_key (m2 fix)"; verified under bash 3.2.57
- [ ] Atomic write failure state: prints red `✗ Failed to write ~/.zshrc (disk full? permissions?). Original is unchanged.` and exits 1  → source: UX_DESIGN §"State coverage — Atomic write fails"
- [ ] Done banner matches UX_DESIGN spec exactly: includes `✓ Setup complete.`, `./dev.sh`, and new-terminal / `source ~/.zshrc` caveat  → source: UX_DESIGN §"Done banner (Phase 2 success)"
- [ ] The legacy "Done" footer block at setup.sh L177–L194 is DELETED — `render_done_banner` is the only source of the success banner; cancel paths (Ctrl-C, `cancel` literal, `[3] Cancel`) cannot fall through to a trailing banner block  → source: IMPL_PLAN §"Approach — Delete the existing Done footer at L177–L194 (M-1 fix)"
- [ ] `render_done_banner` takes `need_restart` as an argument and branches: `true` → "Open a new terminal window" (PATH refresh after bun install); `false` → "Run the app with: ./dev.sh" + the `source ~/.zshrc` / different-terminal hint  → source: IMPL_PLAN §"Done banner — render_done_banner body sketch"
- [ ] After running `setup.sh` and cancelling at any prompt (Ctrl-C / `cancel` / `[3] Cancel`), stdout does NOT contain the string `Setup complete` — only `Setup cancelled. No changes made.`  → source: UX_DESIGN L188 + Scenario 2d; M-1 regression check
- [ ] `find_chain_warning` is invoked with two args `("$rc_path" "$rc_target")` and uses `${rc_path/#$HOME/~}` to render the user-facing path — for a real `/Users/x/.zshrc` symlink the warning shows `~/.zshrc`, NOT `~/..zshrc` (no double-dot)  → source: IMPL_PLAN §"Sketch of find_chain_warning (W1 chained-symlink detection, M-2 user-facing-string fix)"

### dev.sh (Surface C)

- [ ] dev.sh banner includes `Using LLM provider: <provider>` line (using `${LLM_PROVIDER:-claude (default)}`)  → source: UX_DESIGN §"Surface C — dev.sh — Banner"
- [ ] dev.sh banner includes `App running at: http://localhost:8000` as the canonical URL line  → source: UX_DESIGN §"Surface C — Banner" and §"URL is the single source of truth"
- [ ] dev.sh "error — uvicorn not on PATH" should NOT occur after the `uv run` rewrite; if it does, it is logged as a regression  → source: UX_DESIGN §"State coverage — Error — uvicorn not on PATH"

---

## Section 4 — Tests

Derived from FEATURE_SPEC §"BDD scenarios" and IMPL_PLAN §"Test plan".

- [ ] **Scenario 1 — GitHub auth:** `gh auth status` reports an authenticated session and `gh repo clone issamaro/my-job-applications` succeeds without a password prompt  → source: FEATURE_SPEC §"Scenario 1 — GitHub auth before clone"
- [ ] **Scenario 2a — Fresh shell-rc, Gemini:** after setup.sh run, `~/.zshrc` contains exactly one `export LLM_PROVIDER="gemini"` line and exactly one `export GEMINI_API_KEY="AIzaTEST123"` line; current shell has both exported  → source: FEATURE_SPEC §"Scenario 2a"
- [ ] **Scenario 2b — Provider switch preserves orphan key:** after switching from claude to gemini, `~/.zshrc` has `export LLM_PROVIDER="gemini"`, new `export GEMINI_API_KEY=`, AND the original `export ANTHROPIC_API_KEY="sk-ant-OLD"` still present untouched  → source: FEATURE_SPEC §"Scenario 2b"
- [ ] **Scenario 2c — Keep existing key:** after "Keep" at Case A, `~/.zshrc` has updated `LLM_PROVIDER` and unchanged `GEMINI_API_KEY="AIzaEXISTING"`; current shell exports both  → source: FEATURE_SPEC §"Scenario 2c"
- [ ] **Scenario 2d — Cancel at any prompt → zero writes:** `~/.zshrc` is byte-identical to pre-run state after Ctrl-C at provider prompt, `cancel` at key prompt, or `[3] Cancel` at key menu; setup exits 0; current shell env unchanged  → source: FEATURE_SPEC §"Scenario 2d"
- [ ] **Scenario 2e — Pre-flight mismatch warning:** when `LLM_PROVIDER="gemini"` but no `GEMINI_API_KEY` in rc, setup.sh prints the ⚠ mismatch line before any prompt, then continues normally  → source: FEATURE_SPEC §"Scenario 2e"
- [ ] **Scenario 2f — Pre-flight duplicate collapse:** setup.sh prints ⚠ duplicate warning for two `ANTHROPIC_API_KEY` lines; after "Keep existing" commit, exactly one `export ANTHROPIC_API_KEY=` line remains  → source: FEATURE_SPEC §"Scenario 2f"
- [ ] **Scenario 2g — Backend boots with chosen provider (parameterized for claude and gemini):** `dev.sh` stdout contains `Using LLM provider: <P>`; stderr does NOT contain `<P_OTHER>_API_KEY environment variable is not set`; backend returns HTTP 200 at `http://localhost:8000/`  → source: FEATURE_SPEC §"Scenario 2g"
- [ ] **Scenario 3 — Portable launch after mv:** after `mv ~/projects/my-job-applications ~/code/my-job-applications && ./dev.sh`, banner shows `App running at: http://localhost:8000`, no "command not found" in stdout/stderr, backend returns HTTP 200  → source: FEATURE_SPEC §"Scenario 3 — Portable launch after mv"
- [ ] **Scenario 4 — URL agreement:** `grep "localhost:" README.md` returns zero matches outside `:8000`; `http://localhost:8000` in dev.sh banner equals the URL cited in README §5  → source: FEATURE_SPEC §"Scenario 4 — URL agreement"
- [ ] **Scenario 5 — Repo name consistency:** `grep -ri "MyCV-2" README.md setup.sh` returns zero hits; clone command in README reads `gh repo clone issamaro/my-job-applications`; `cd` line reads `cd my-job-applications`  → source: FEATURE_SPEC §"Scenario 5 — Repo name consistency"
- [ ] **Regression:** `uv run pytest` exits 0 on the full existing test suite (no app-feature test changes expected)  → source: IMPL_PLAN §"Test plan": "`uv run pytest` — full existing suite must pass"

---

## Section 5 — Accessibility

Derived from UX_DESIGN §"Surface A — Accessibility / readability" and §"Surface B — Keyboard navigation".

- [ ] README headings start at H2 inside the document body (H1 is the title only)  → source: UX_DESIGN §"Accessibility / readability": "Headings start at H2 inside README (H1 is title)"
- [ ] No emoji appear inside fenced command blocks in README (decorative emoji only in section dividers, if any)  → source: UX_DESIGN §"Accessibility / readability": "No emoji in commands"
- [ ] All hyperlinks in README use full descriptive text, not "click here"  → source: UX_DESIGN §"Accessibility / readability": "Hyperlinks use full text, not 'click here'"
- [ ] setup.sh key prompt uses `read -rs` (silent/hidden input) for API key entry  → source: UX_DESIGN §"Keyboard navigation": "Hidden input for API keys via `read -rs`"
- [ ] Empty-Enter at the key prompt loops with a re-prompt; it does NOT trigger "keep existing" semantics  → source: UX_DESIGN §"Keyboard navigation": "Pressing Enter with no input on the key prompt loops; never has overloaded 'keep existing' semantics"
- [ ] Ctrl-C exits cleanly at any prompt with no shell-rc changes (guaranteed by atomic-commit-only-at-end pattern)  → source: UX_DESIGN §"Keyboard navigation": "Ctrl-C exits cleanly at any prompt with no shell-rc changes"
- [ ] `update_provider_and_key` calls `trap - INT` IMMEDIATELY BEFORE `create_rc_content` so the commit phase is uninterruptible — Ctrl-C during `write_rc_atomic` cannot falsely return 0 from the helper while the orchestrator believes commit succeeded  → source: IMPL_PLAN §"Notes — Commit phase is uninterruptible (M2 trap-leak fix)"
- [ ] `update_provider_and_key` installs an `EXIT` trap that runs `rm -f "${rc_target}.tmp.$$"` (literal pid suffix, not glob) on every exit path (success, failure, SIGINT) so this run's temp file cannot linger in `$HOME` AND a concurrent setup.sh cannot delete a sibling run's in-flight temp  → source: IMPL_PLAN §"Notes — EXIT-trap temp cleanup"
- [ ] After `setup.sh` runs (any path: success, mid-prompt cancel, mid-commit Ctrl-C), `ls "$HOME/.zshrc.tmp."* 2>/dev/null | wc -l` returns 0  → source: IMPL_PLAN §"EXIT-trap temp cleanup"; M2 leak regression check

---

## Section 6 — Project-specific

n/a — no project-checks.md found at repo root.

---

## Inspector Checklist (FEATURE_SPEC §Verification — 10 items)

These 10 items are the build gate. All must pass before the feature is declared done.

- [ ] **I-1** `grep -ri "MyCV-2" README.md setup.sh` returns zero hits  → source: FEATURE_SPEC §"Verification" item 1
- [ ] **I-2** `grep "localhost:" README.md` shows only `:8000` matches  → source: FEATURE_SPEC §"Verification" item 2
- [ ] **I-3** README has a §"Authenticate to GitHub" section before "Clone the project" with `gh auth login` walkthrough  → source: FEATURE_SPEC §"Verification" item 3
- [ ] **I-4** Run `./setup.sh`, exercise Case A all three menu paths (Keep / Replace / Cancel)  → source: FEATURE_SPEC §"Verification" item 4
- [ ] **I-5** Run `./setup.sh`, exercise Case B paste path (non-empty key input)  → source: FEATURE_SPEC §"Verification" item 5
- [ ] **I-6** Run `./setup.sh` with a manually-injected duplicate key line; confirm pre-flight prints the duplicate warning AND post-run rc has exactly one line for that var  → source: FEATURE_SPEC §"Verification" item 6
- [ ] **I-7** Run `./setup.sh` with a manually-induced mismatch (e.g., `LLM_PROVIDER=gemini` but no `GEMINI_API_KEY`); confirm pre-flight prints the mismatch warning  → source: FEATURE_SPEC §"Verification" item 7
- [ ] **I-8** Run `./dev.sh`; observe the `Using LLM provider:` line; visit `http://localhost:8000/`; confirm HTTP 200  → source: FEATURE_SPEC §"Verification" item 8
- [ ] **I-9** `mv` the project folder to a new path, re-run `./dev.sh`, confirm app loads at `http://localhost:8000`  → source: FEATURE_SPEC §"Verification" item 9
- [ ] **I-10** Open README §6 troubleshooting; confirm copy reads correctly for all four documented failure scenarios  → source: FEATURE_SPEC §"Verification" item 10
