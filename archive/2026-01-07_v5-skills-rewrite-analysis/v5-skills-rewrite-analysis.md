# v5 Slash Commands Rewrite Analysis

**Date:** 2026-01-07
**Purpose:** Comprehensive analysis of v4→v5 slash command migration

---

## 1. Official Guidelines Summary

From Claude Code documentation (Slash Commands, not Agent Skills):

### Terminology Note
- **Slash Commands**: Single `.md` files in `~/.claude/commands/` - what we use
- **Agent Skills**: Directories with `SKILL.md` + resources in `~/.claude/skills/` - NOT what we use

### Required Format
```yaml
---
description: Brief description + trigger terms ("Use when...")
allowed-tools: [optional] Tools the command can use (e.g., Bash(git:*))
argument-hint: [optional] Show expected arguments
model: [optional] Specific model override
disable-model-invocation: [optional] Prevent auto-invocation (default: false)
---

Direct instructions to Claude here.
```

### Best Practices
1. **Be explicit and direct** - instructions, not explanations
2. **Keep simple** - slash commands are single files, not complex workflows
3. **50-100 lines max** - larger commands should become Agent Skills
4. **Include description** - required for SlashCommand tool auto-invocation
5. **Include trigger terms** - "Use when..." in description

---

## 2. Current v4 Commands Inventory

| Command | Lines | Type | Issues |
|---------|-------|------|--------|
| v4-feature | 122 | Orchestrator | No frontmatter, usage section |
| v4-analyze | 97 | Orchestrator | No frontmatter, usage section |
| v4-plan | 102 | Orchestrator | No frontmatter, usage section |
| v4-build | 121 | Orchestrator | No frontmatter, usage section |
| v4-ship | 121 | Orchestrator | No frontmatter, usage section |
| v4-requirements | 159 | Worker | No frontmatter, embedded template |
| v4-ux | 176 | Worker | No frontmatter, embedded template |
| v4-research | 171 | Worker | "Why" section, embedded template |
| v4-design | 186 | Worker | No frontmatter, embedded template |
| v4-checklist | 235 | Worker | Embedded templates, verbose |
| v4-ecosystem | 189 | Worker | "Why" section, tutorial bash |
| v4-scaffold | 175 | Worker | Tutorial bash blocks |
| v4-implement | 186 | Worker | Tutorial bash blocks |
| v4-test | 231 | Worker | "Why" section, embedded template |
| v4-validate | 194 | Worker | "Why" section, embedded template |
| v4-inspect | 206 | Worker | "Why" section, embedded template |
| v4-close | 248 | Worker | Embedded templates, verbose |
| v4-note | 153 | Worker | Embedded template |
| v4-reflect | 182 | Worker | "Key change" section, embedded template |
| v4-scope | 171 | Standalone | Embedded template |
| v4-initialize | 122 | Orchestrator | "Key change" section |
| v4-init-close | 160 | Worker | Tutorial bash blocks |
| v4-verify-analysis | 212 | Verification | "Why" section, ASCII diagram |
| v4-verify-plan | 180 | Verification | "Why" section |

**Type Legend:** Orchestrator/Worker/Standalone/Verification are logical roles, not technical distinctions. All are single `.md` Slash Commands.

**Total:** 4,099 lines across 24 commands

**Note:** At 50-100 lines max per official docs, these are significantly over target.

---

## 3. Patterns to Remove

### 3.1 "Why" Explanations (remove entirely)
Found in: v4-research, v4-ecosystem, v4-test, v4-validate, v4-inspect, v4-reflect, v4-verify-analysis, v4-verify-plan

Example (v4-test lines 10-20):
```markdown
## Why Consolidated Testing

v2.1 had three separate test skills...
v4 consolidates them because:
1. All represent the same concern...
```
**Action:** Delete these sections

### 3.2 "Usage" Sections (remove entirely)
Found in: ALL 24 skills

Example:
```markdown
## Usage

User: "Run the tests"
/v4-test
```
**Action:** Delete - AI is already invoked

### 3.3 Architecture Metadata (remove)
Found in: ALL 24 skills

Example:
```markdown
**Architecture:** v4.0 - Worker Skill
**Lines:** ~150 (Worker)
```
**Action:** Delete - human documentation

### 3.4 Tutorial-Style Bash Blocks (convert to directives)
Found in: v4-implement, v4-test, v4-research, v4-ecosystem, v4-scaffold, v4-validate, v4-init-close

Example (current):
```markdown
```bash
# Sync dependencies (creates .venv if needed)
uv sync

# Run a command in the environment
uv run python main.py
```
```

**Convert to:**
```markdown
Run: `uv sync` to install dependencies
Run: `uv run python main.py` to execute
```

### 3.5 Embedded Output Templates → Minimal Field Lists
Found in: v4-requirements, v4-ux, v4-research, v4-design, v4-checklist, v4-test, v4-validate, v4-inspect, v4-close, v4-note, v4-reflect, v4-scope, v4-verify-analysis, v4-verify-plan

**Action:** Replace 50-80 line templates with 4-8 line field lists.

Example transformation:
```
# Before (77 lines)
## Output Template
```markdown
# Test Results: {Name}
**Date:** {DATE}
... [70+ more lines]
```

# After (6 lines)
## Output
Create `TEST_RESULTS_{DATE}_{NAME}.md` containing:
- Command and result for each test level
- Pass/fail counts
- Coverage percentage
```

---

## 4. YAML Frontmatter Additions

### 4.1 Descriptions with Trigger Terms

| Command | Proposed Description |
|---------|---------------------|
| v5-feature | `Orchestrate complete feature development. Use when user says "implement feature" with a refined backlog item.` |
| v5-analyze | `Complete analysis phase. Use after /v5-scope or when starting feature analysis.` |
| v5-plan | `Complete planning phase. Use after /v5-analyze or when creating implementation plan.` |
| v5-build | `Implement and verify code. Use after /v5-plan or when building a feature.` |
| v5-ship | `Complete delivery with closure. Use after /v5-build passes or when shipping a feature.` |
| v5-requirements | `Define problem statement and BDD scenarios. Use during analysis phase.` |
| v5-ux | `Define UX states and wireframes. Use when feature has UI changes.` |
| v5-research | `Lookup library syntax via context7. Use before implementation planning.` |
| v5-design | `Create technical implementation plan. Use after research, before checklist.` |
| v5-checklist | `Create verification points for implementation. Use after design.` |
| v5-ecosystem | `Determine stack compatibility and runtime versions. Use when initializing project.` |
| v5-scaffold | `Create project structure and hello world. Use after ecosystem decision.` |
| v5-implement | `Write code following the plan. Use during build phase.` |
| v5-test | `Run all automated tests. Use after implementation.` |
| v5-validate | `Verify foundation before committing. Use after scaffold.` |
| v5-inspect | `Manual verification - browser, accessibility, UX. Use after tests pass.` |
| v5-close | `Document changes and create git commit. Use during ship phase.` |
| v5-note | `Capture unexpected findings mid-implementation. Use when encountering issues.` |
| v5-reflect | `Capture lessons learned. Use during ship phase.` |
| v5-scope | `Transform raw ideas into refined features. Use before /v5-feature.` |
| v5-initialize | `Orchestrate new project setup. Use when creating new project.` |
| v5-init-close | `Create initial commit and backlog structure. Use after validation passes.` |
| v5-verify-analysis | `QA checkpoint for analysis phase. Use after requirements/UX complete.` |
| v5-verify-plan | `QA checkpoint for planning phase. Use after design/checklist complete.` |

### 4.2 Allowed Tools

| Command | allowed-tools |
|---------|---------------|
| v5-build | `Bash(pytest:*), Bash(uv:*), Bash(uvicorn:*), Bash(npm:*)` |
| v5-ship | `Bash(git:*), Bash(mv:*), Bash(mkdir:*)` |
| v5-test | `Bash(pytest:*), Bash(npm:*)` |
| v5-implement | `Bash(uv:*), Bash(python:*)` |
| v5-scaffold | `Bash(uv:*), Bash(mkdir:*), Bash(npm:*)` |
| v5-validate | `Bash(pytest:*), Bash(uvicorn:*), Bash(python:*)` |
| v5-init-close | `Bash(git:*), Bash(mkdir:*), Bash(mv:*)` |
| v5-close | `Bash(git:*), Bash(mv:*), Bash(mkdir:*)` |
| v5-research | (none - uses MCP context7) |
| v5-ecosystem | (none - uses MCP context7) |

---

## 5. Structural Changes

### 5.1 Remove Horizontal Rules
Current: `---` separators everywhere
Change: Remove most, keep only for major sections

### 5.2 Remove Footer Signatures
Current: `*Architecture Version: 4.0 (Worker Skill)*`
Change: Delete entirely

### 5.3 Simplify Tables
Current: Full tables with many columns
Change: Inline or minimal tables only where needed

---

## 6. Estimated Line Counts

**Target:** 50-100 lines max per official docs (complex commands at upper end)

| Command | v4 Lines | v5 Target | Reduction |
|---------|----------|-----------|-----------|
| v5-feature | 122 | ~50 | -59% |
| v5-analyze | 97 | ~40 | -59% |
| v5-plan | 102 | ~45 | -56% |
| v5-build | 121 | ~50 | -59% |
| v5-ship | 121 | ~45 | -63% |
| v5-requirements | 159 | ~60 | -62% |
| v5-ux | 176 | ~70 | -60% |
| v5-research | 171 | ~60 | -65% |
| v5-design | 186 | ~70 | -62% |
| v5-checklist | 235 | ~80 | -66% |
| v5-ecosystem | 189 | ~60 | -68% |
| v5-scaffold | 175 | ~60 | -66% |
| v5-implement | 186 | ~70 | -62% |
| v5-test | 231 | ~70 | -70% |
| v5-validate | 194 | ~60 | -69% |
| v5-inspect | 206 | ~70 | -66% |
| v5-close | 248 | ~80 | -68% |
| v5-note | 153 | ~50 | -67% |
| v5-reflect | 182 | ~60 | -67% |
| v5-scope | 171 | ~70 | -59% |
| v5-initialize | 122 | ~45 | -63% |
| v5-init-close | 160 | ~55 | -66% |
| v5-verify-analysis | 212 | ~70 | -67% |
| v5-verify-plan | 180 | ~60 | -67% |

**Total:** 4,099 → ~1,450 lines (65% reduction)

**Compliance:** All v5 targets fall within 50-100 line recommendation.

---

## 7. Example Rewrite: v5-test

### 7.1 What Gets Removed (with line references to v4-test)

| v4 Section | Lines | Principle Violated | Action |
|------------|-------|-------------------|--------|
| `**Architecture:** v4.0...` | 6-7 | §3.3 Architecture metadata | DELETE |
| `**Lines:** ~150 (Worker)` | 7 | §3.3 Architecture metadata | DELETE |
| `## Why Consolidated Testing` | 10-20 | §3.1 "Why" explanations | DELETE |
| `## Usage` block | 219-227 | §3.2 Usage sections | DELETE |
| `*Architecture Version...*` | 231 | §5.2 Footer signatures | DELETE |
| `---` horizontal rules | throughout | §5.1 Horizontal rules | REDUCE |
| `## Output Template` (77 lines) | 109-188 | §3.5 Embedded templates | SIMPLIFY |
| Tutorial bash blocks | 76-105 | §3.4 Tutorial bash | CONVERT |

### 7.2 What Gets Added

| Addition | Principle | Example |
|----------|-----------|---------|
| YAML frontmatter | §1 Required Format | `description:`, `allowed-tools:` |
| Trigger terms | §4.1 Descriptions | "Use after /v5-implement" |
| Tool permissions | §4.2 Allowed Tools | `Bash(pytest:*)` |
| Direct commands | §3.4 Convert bash | "Run: `pytest...`" |
| `disable-model-invocation` | Official docs | Optional, default false |

### 7.3 Side-by-Side Transformation

#### Header Block

**v4 (7 lines):**
```
# Test

**Purpose:** Run all automated tests (unit + integration + e2e).
**Output:** `workbench/3-build/test/TEST_RESULTS_{DATE}_{NAME}.md`
**Architecture:** v4.0 - Worker Skill (QA CHECKPOINT 3a)
**Lines:** ~150 (Worker)

---
```

**v5 (6 lines):**
```
---
description: Run all automated tests (unit, integration, e2e). Use after /v5-implement.
allowed-tools: Bash(pytest:*), Bash(npm:*)
---

# Test
```

**Changes:** YAML frontmatter replaces Purpose/Architecture/Lines. Output moved to body.

#### Bash Blocks

**v4 (tutorial style):**
```
### 1. Unit Tests

Run unit tests (fast, isolated):

```bash
pytest tests/ -v --ignore=tests/e2e --ignore=tests/integration
```

**Expectations:**
- All new tests pass
- Existing tests still pass
- No import errors
```

**v5 (directive style):**
```
### 1. Unit Tests
Run: `pytest tests/ -v --ignore=tests/e2e --ignore=tests/integration`

Expect: all pass, no import errors.
```

**Changes:** Removed explanation, converted to imperative directive.

#### Output Template

**v4 (77 lines):**
```
## Output Template

```markdown
# Test Results: {Name}

**Date:** {DATE}
**Status:** PASS / FAIL

---

## 1. Unit Tests

**Command:** `pytest tests/ -v --ignore=tests/e2e --ignore=tests/integration`

**Result:** [X passed, Y failed]

### Passed
- test_[name]

### Failed (if any)
- test_[name]
  - Error: [message]
  - Location: [file:line]

---

## 2. Integration Tests
... [continues 50+ more lines]
```
```

**v5 (6 lines):**
```
## Output

Create `TEST_RESULTS_{DATE}_{NAME}.md` containing:
- Command and result for each test level
- Pass/fail counts
- Coverage percentage
- Notes captured (if /v5-note invoked)
```

**Changes:** Field list replaces full template. AI generates structure.

### 7.4 Complete v5-test Example

This is what the actual file would look like:

```
---
description: Run all automated tests (unit, integration, e2e). Use after /v5-implement.
allowed-tools: Bash(pytest:*), Bash(npm:*)
---

# Test

**Output:** `workbench/3-build/test/TEST_RESULTS_{DATE}_{NAME}.md`

## Prerequisite

Verify dependencies match manifest before running.

Run: `uv tree --package [package]` (Python) or `npm list [package]` (Node)

If mismatch: STOP, report blocking failure, return to /v5-implement.

## Steps

### 1. Unit Tests
Run: `pytest tests/ -v --ignore=tests/e2e --ignore=tests/integration`

### 2. Integration Tests
Run: `pytest tests/integration/ -v`

### 3. E2E Tests (if applicable)
Run: `pytest tests/e2e/ -v`

### 4. Coverage
Run: `pytest --cov=app --cov-report=term`

## Output

Create `TEST_RESULTS_{DATE}_{NAME}.md` containing:
- Command and result for each test level
- Pass/fail counts
- Coverage percentage
- Notes captured (if /v5-note invoked)

## Status

| Status | Next |
|--------|------|
| PASS | /v5-inspect |
| FAIL | Fix code, re-run |

## Note Trigger

If environment issue or flaky test encountered: invoke /v5-note → fix → re-run.
```

### 7.5 Line Count Comparison

| Metric | v4-test | v5-test | Change |
|--------|---------|---------|--------|
| Total lines | 231 | 52 | -77% |
| YAML frontmatter | 0 | 4 | +4 |
| "Why" section | 11 | 0 | -11 |
| Output template | 77 | 6 | -71 |
| Usage section | 8 | 0 | -8 |
| Metadata lines | 4 | 0 | -4 |

---

## 8. Decisions

### Q1: Template Handling ✓ DECIDED
**Choice: B) Minimal inline**

- No separate template files
- Skills specify only essential field names
- AI generates appropriate structure

Example:
```
## Output

Create `TEST_RESULTS_{DATE}_{NAME}.md` containing:
- Command and result for each test level
- Pass/fail counts
- Coverage percentage
```

### Q2: Output Format in Skills ✓ DECIDED
**Choice: B) Field list only**

Follows from Q1. No full templates, just field lists.

### Q3: Command Location ✓ DECIDED
**Choice: A) New v5-*.md files**

- Create alongside v4 in `~/.claude/commands/`
- Safe migration path
- Can compare/test before removing v4
- These are Slash Commands (single .md files), NOT Agent Skills

---

## 9. Next Steps

1. [x] Review this analysis
2. [x] Decide on Q1, Q2, Q3 above
3. [x] Approve v5-test example as reference
4. [x] Verify compliance with official Slash Commands docs (NOT Skills docs)
5. [ ] Rewrite all 24 commands following pattern
6. [ ] Test with actual feature workflow

## 10. Implementation Order

Rewrite in dependency order (all are Slash Commands in `~/.claude/commands/`):

**Batch 1: Standalone/Entry Points**
- v5-scope (entry for feature refinement)
- v5-initialize (entry for new projects)

**Batch 2: Orchestrators**
- v5-feature, v5-analyze, v5-plan, v5-build, v5-ship
- v5-init-close

**Batch 3: Analysis Workers**
- v5-requirements, v5-ux, v5-verify-analysis

**Batch 4: Planning Workers**
- v5-research, v5-ecosystem, v5-design, v5-checklist, v5-verify-plan

**Batch 5: Build Workers**
- v5-scaffold, v5-implement, v5-test, v5-validate, v5-inspect

**Batch 6: Ship Workers**
- v5-close, v5-reflect, v5-note
