# Methodology Improvement: Solution Proposal v4 (Refined)

**Date:** 2026-01-04
**Status:** Refined based on user feedback
**Changes from v3:**
- /v4-initialize: validate BEFORE commit, add /v4-close
- /v4-note: skills should be aware and prompt for it
- verify-analysis: no percentages, just recall /v4-scope
- backlog: `0-backlog/{raw,refined}` structure (simplified)
- Checklist gaps: confirmed approach (global vs project-specific)
- **NEW: /v4-scope as standalone refiner (outside /v4-feature)**
- **NEW: All commands prefixed with /v4-... (clean slate)**
- **NEW: Skill size constraint (100-200 lines max)**

---

## CRITICAL: Design Principles

### 1. Context-Size Efficiency (Primary Rationale)

The v3 methodology exists because **large monolithic commands exhaust context**. Every skill must:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SKILL SIZE CONSTRAINTS                            │
└─────────────────────────────────────────────────────────────────────┘

    WORKER SKILLS:        100-200 lines MAXIMUM
    ORCHESTRATOR SKILLS:  50-100 lines MAXIMUM (just coordinate)

    If a skill exceeds this → BREAK IT DOWN into sub-skills

    Rationale:
    • Large prompts tire the agent
    • Context is precious, don't waste it on instructions
    • Small focused skills = better execution
    • Orchestrators should just route, not contain logic
```

### 2. Clean Versioning (v4 Prefix for ALL)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COMMAND NAMING CONVENTION                         │
└─────────────────────────────────────────────────────────────────────┘

    BEFORE (messy):
    ├── /v2-analyze-feature.md      ← Old version
    ├── /v3-analyze.md              ← Current version
    ├── /analyze-feature.md         ← No prefix (which version?)
    └── /plan-implementation.md     ← No prefix

    AFTER (clean):
    └── /v4-*.md                    ← ALL commands have v4 prefix

    MIGRATION:
    1. Create all /v4-* commands
    2. DELETE all /v2-* commands
    3. DELETE all unprefixed commands
    4. Only /v4-* remains
```

---

## Refinement 1: /v4-initialize Flow (Validate Before Commit)

### Previous (v3)
```
/v4-ecosystem → /v4-scaffold (creates + commits) → /v4-validate
                                    ↑
                            Commits BEFORE validation!
```

### Refined (v4)
```
                              ┌─────────────────────┐
                              │    USER INTENT      │
                              └──────────┬──────────┘
                                         │
                                         ▼
    ┌────────────────────────────────────────────────────────────────┐
    │ Phase 1: /v4-ecosystem                                         │
    ├────────────────────────────────────────────────────────────────┤
    │ • Query context7 for stack compatibility                       │
    │ • Decide runtime version                                       │
    │ • Document rationale                                           │
    │ OUTPUT: workbench/0-init/ECOSYSTEM_DECISION_*.md              │
    └────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
    ┌────────────────────────────────────────────────────────────────┐
    │ Phase 2: /v4-scaffold                                          │
    ├────────────────────────────────────────────────────────────────┤
    │ • Create project structure                                     │
    │ • Create dependency manifests                                  │
    │ • Setup dev tooling + hello world                              │
    │ OUTPUT: Working code (NOT COMMITTED YET)                       │
    │ ⚠️ NO GIT COMMIT - validation must pass first                 │
    └────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
    ┌────────────────────────────────────────────────────────────────┐
    │ Phase 3: /v4-validate                                          │
    ├────────────────────────────────────────────────────────────────┤
    │ CHECKS: Build & Run, Dev Workflow, Error Handling              │
    │ IF FAIL → Fix issues, re-run                                   │
    │ IF PASS → OUTPUT: workbench/0-init/FOUNDATION_VERIFIED_*.md   │
    └────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
    ┌────────────────────────────────────────────────────────────────┐
    │ Phase 4: /v4-init-close                                        │
    ├────────────────────────────────────────────────────────────────┤
    │ REQUIRES: FOUNDATION_VERIFIED with PASS                        │
    │ 1. Create initial git commit                                   │
    │ 2. Archive: workbench/0-init/ → archive/[DATE]_INIT/          │
    │ 3. Create 0-backlog/{raw,refined}/ structure                   │
    └────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │    PROJECT READY    │
                              │  Use /v4-scope      │
                              └─────────────────────┘
```

---

## Refinement 2: /v4-note Awareness

Skills that should PROMPT for /v4-note when issues arise:

| Skill | Trigger | Action |
|-------|---------|--------|
| /v4-implement | Unexpected behavior, workaround, assumption wrong | Fix → /v4-note → Continue |
| /v4-test | Environment issue, flaky test, framework quirk | /v4-note → Fix → Re-run |
| /v4-inspect | Browser quirk, rendering difference, a11y tool issue | /v4-note → Continue |

User can ask: "Did anything happen that needs /v4-note?"
Agent reviews recent actions and invokes /v4-note if needed.

---

## Refinement 3: /v4-verify-analysis Scope Check

### Previous (v3) - Percentages
```
• < 20% expansion → ✅ Proceed
• 20-50% → ⚠️ User decision
• > 50% → ❌ STOP
```

### Refined (v4) - Just Recall /v4-scope

```
/v4-verify-analysis
       │
       ▼
┌─────────────────┐
│ Checks 1-4      │
│ (existing)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Check 5:        │
│ Scope grew?     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
  NO        YES → Recall /v4-scope with updated context
    │              │
    │         ┌────┴────┐
    │         │         │
    │         ▼         ▼
    │     Single    EPIC → Ask user:
    │     feature   A) Scope all now (refined/)
    │         │     B) Capture raw (raw/)
    ▼         │         │
┌─────────────┴─────────┘
│ Continue to /v4-plan
└─────────────────────────
```

---

## Refinement 4: 0-backlog/ Structure (SIMPLIFIED)

### Previous (v3) - Complex subdirectories
```
0-backlog/
├── epics/              ← Ambiguous: raw or refined?
├── features/           ← Ambiguous: raw or refined?
├── from-retrospectives/
└── user-intents/
```

### Refined (v4) - Binary: raw OR refined

```
┌─────────────────────────────────────────────────────────────────────┐
│                    0-backlog/ STRUCTURE (FINAL)                      │
└─────────────────────────────────────────────────────────────────────┘

    0-backlog/
    ├── raw/                    ← FREEFORM. Anything goes. No template.
    │   ├── dark-mode.md           "User wants dark mode"
    │   ├── e2e-tests.md           "Need e2e tests - retro finding"
    │   └── user-mgmt-roles.md     "Sub-feature from epic breakdown"
    │
    └── refined/                ← STRUCTURED. Ready for /v4-feature.
        ├── dark-mode.md           SCOPED_FEATURE format
        └── export-pdf.md          SCOPED_FEATURE format

    LIFECYCLE:

    raw/item.md  ──▶  /v4-scope  ──▶  refined/item.md  ──▶  /v4-feature
         │                                    │
         │                                    │
    Freeform text              SCOPED_FEATURE structure
    No requirements            Ready to implement
```

### Raw Item Format (FREEFORM)

```
# Dark Mode

User wants dark mode for the app.
Mentioned on 2026-01-04 during SAVED-JOB-DESCRIPTIONS feature.

That's it. No structure required. Just capture the thought.
```

### Refined Item Format (SCOPED_FEATURE)

```
# Dark Mode - SCOPED_FEATURE

**Size:** M (Medium)
**Files affected:** ~8-12
**Dependencies:** None new
**Ready for:** /v4-feature

## Description
[Structured description]

## Scope
[Clear boundaries]

## Out of Scope
[Explicit exclusions]
```

---

## Refinement 5: /v4-scope as Standalone Refiner

### Key Change: /v4-scope is OUTSIDE /v4-feature

```
┌─────────────────────────────────────────────────────────────────────┐
│                    /v4-scope (STANDALONE SKILL)                      │
└─────────────────────────────────────────────────────────────────────┘

    NOT inside /v4-feature. Runs BEFORE /v4-feature.

    ROLE: Transform raw → refined

    INPUT:
    ├── Direct user request: "I want dark mode"
    └── Raw backlog item: "Scope the e2e-tests item"

    PROCESS:
    1. Analyze scope
    2. Determine size (XS/S/M/L/XL or EPIC)

    OUTPUT:

    IF size ≤ XL (single feature):
    → Create: 0-backlog/refined/{feature-name}.md

    IF size = EPIC:
    → ASK USER:
      "This is epic-sized. I identified N sub-features:
       1. User authentication
       2. Role management
       3. Permission system

       How should I capture them?

       A) Scope all now (refined/) - higher effort, all ready
       B) Capture as raw (raw/) - refine one at a time later"

    IF A → Create N files in refined/
    IF B → Create N files in raw/ (freeform)
```

### /v4-feature: Strict Contract

```
┌─────────────────────────────────────────────────────────────────────┐
│                    /v4-feature ENTRY VALIDATION                      │
└─────────────────────────────────────────────────────────────────────┘

    User: "/v4-feature dark-mode"

    /v4-feature checks:

    Does 0-backlog/refined/dark-mode.md exist?
    │
    ├─ YES → Load SCOPED_FEATURE, proceed to /v4-analyze
    │
    └─ NO → "No refined feature 'dark-mode' found.

             Options:
             • Run /v4-scope dark-mode to create it
             • Point me to an existing refined feature

             Available in refined/:
             - export-pdf
             - bulk-delete"
```

### /v4-reflect: Always Raw

```
┌─────────────────────────────────────────────────────────────────────┐
│                    /v4-reflect → raw/ ONLY                           │
└─────────────────────────────────────────────────────────────────────┘

    Findings from retrospective:

    "We discovered manual testing is slow"
    → Creates: 0-backlog/raw/e2e-test-framework.md

    Content (freeform):
    ┌─────────────────────────────────────────────────────────────────┐
    │ # E2E Test Framework                                            │
    │                                                                 │
    │ Source: SAVED-JOB-DESCRIPTIONS retrospective                   │
    │ Date: 2026-01-04                                                │
    │                                                                 │
    │ Manual testing took too long. Consider Playwright.              │
    └─────────────────────────────────────────────────────────────────┘

    NO structure imposed. Just capture the thought.
    Later: user runs /v4-scope e2e-test-framework to refine it.
```

---

## Refinement 6: Checklist (Global vs Project-Specific)

```
~/.claude/commands/v4-checklist.md
│
│   Contains GLOBAL sections (0-5):
│   • Ecosystem, Dependencies, Syntax, UX, Test, Accessibility
│
│   Section 6 reads from project-specific file:
│   → project-root/project-checks.md
│
└───────────────────────────────────────────────────────────────────

project-root/project-checks.md
│
│   Contains PROJECT-SPECIFIC checks from retrospectives:
│   • SCSS token locations
│   • Environment variables
│   • HTML nesting rules learned
│   • Integration patterns
│
└───────────────────────────────────────────────────────────────────
```

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         COMPLETE v4 FLOW                             │
└─────────────────────────────────────────────────────────────────────┘

                              INPUTS
    ┌──────────────────────────────────────────────────────────────────┐
    │  User idea    /v4-reflect finding    Epic sub-feature (raw)     │
    └──────────────────────────────────────────────────────────────────┘
                           │
                           ▼
                   ┌───────────────┐
                   │  0-backlog/   │
                   │     raw/      │  ← Freeform capture
                   └───────┬───────┘
                           │
                           │ User: "/v4-scope {item}"
                           ▼
                   ┌───────────────┐
                   │   /v4-scope   │ ◄── STANDALONE (not in /v4-feature)
                   └───────┬───────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
    ┌─────────────────┐       ┌─────────────────┐
    │  Single feature │       │  EPIC detected  │
    │  → refined/     │       │  → Ask: A or B? │
    └────────┬────────┘       └────────┬────────┘
             │                         │
             ▼                         │
    ┌───────────────┐ ◄────────────────┘
    │  0-backlog/   │
    │   refined/    │  ← Structured, ready
    └───────┬───────┘
            │
            │ User: "/v4-feature {item}"
            ▼
    ┌───────────────┐
    │  /v4-feature  │ ◄── Only accepts refined/
    │               │
    │  Orchestrates:│
    │  /v4-analyze  │
    │  /v4-plan     │
    │  /v4-build    │
    │  /v4-ship     │
    └───────────────┘
```

---

## File Changes Summary (v4 Migration)

### NEW /v4-* Skills to Create

| Skill | Lines | Type | Description |
|-------|-------|------|-------------|
| `v4-scope.md` | ~150 | Worker | Standalone refiner: raw → refined |
| `v4-feature.md` | ~80 | Orchestrator | Entry validator + phase coordinator |
| `v4-analyze.md` | ~80 | Orchestrator | Analyze phase coordinator |
| `v4-requirements.md` | ~150 | Worker | Feature spec creation |
| `v4-ux.md` | ~150 | Worker | UX design |
| `v4-verify-analysis.md` | ~150 | Worker | QA analysis + scope check |
| `v4-plan.md` | ~80 | Orchestrator | Plan phase coordinator |
| `v4-research.md` | ~150 | Worker | Context7 + codebase research |
| `v4-design.md` | ~150 | Worker | Technical implementation plan |
| `v4-checklist.md` | ~150 | Worker | Generate verification checklist |
| `v4-verify-plan.md` | ~150 | Worker | QA implementation plan |
| `v4-build.md` | ~80 | Orchestrator | Build phase coordinator |
| `v4-implement.md` | ~200 | Worker | Code implementation |
| `v4-test.md` | ~150 | Worker | Test writing |
| `v4-inspect.md` | ~150 | Worker | Browser/manual verification |
| `v4-ship.md` | ~80 | Orchestrator | Ship phase coordinator |
| `v4-reflect.md` | ~150 | Worker | Retrospective → raw/ |
| `v4-close.md` | ~100 | Worker | Commit + archive |
| `v4-note.md` | ~80 | Worker | Mid-implementation capture |
| `v4-initialize.md` | ~80 | Orchestrator | Project init coordinator |
| `v4-ecosystem.md` | ~150 | Worker | Stack decisions |
| `v4-scaffold.md` | ~150 | Worker | Project skeleton |
| `v4-validate.md` | ~150 | Worker | Foundation verification |
| `v4-init-close.md` | ~100 | Worker | Init commit + backlog setup |

### Files to DELETE

```
DELETE all /v2-* commands:
- v2-analyze-feature.md
- v2-close-feature.md
- v2-create-checklist.md
- v2-design-ux.md
- v2-document-assumptions.md
- v2-implement-feature.md
- v2-plan-implementation.md
- v2-research-libraries.md
- v2-run-retrospective.md
- v2-verify-a11y.md
- v2-verify-analysis.md
- v2-verify-browser.md
- v2-verify-e2e-tests.md
- v2-verify-integration-tests.md
- v2-verify-plan.md
- v2-verify-unit-tests.md
- v2-verify-ux.md

DELETE all unprefixed commands:
- analyze-feature.md
- close-feature.md
- implement-feature.md
- plan-implementation.md
- verify-feature.md
```

### Convention Files (per project)

```
project-root/
├── project-checks.md       ← Project-specific checklist items
└── 0-backlog/
    ├── raw/                ← Freeform items
    └── refined/            ← Scoped features ready for /v4-feature
```

---

## Implementation Order

### Phase 1: Core Infrastructure
1. Create `v4-scope.md` (standalone refiner)
2. Create `v4-feature.md` (with refined/ validation)
3. Create `v4-reflect.md` (always raw/)
4. Create `v4-note.md`

### Phase 2: Analyze Phase
5. Create `v4-analyze.md` (orchestrator)
6. Create `v4-requirements.md`
7. Create `v4-ux.md`
8. Create `v4-verify-analysis.md` (with scope recall)

### Phase 3: Plan Phase
9. Create `v4-plan.md` (orchestrator)
10. Create `v4-research.md`
11. Create `v4-design.md`
12. Create `v4-checklist.md` (with Section 6)
13. Create `v4-verify-plan.md`

### Phase 4: Build Phase
14. Create `v4-build.md` (orchestrator)
15. Create `v4-implement.md` (with /v4-note awareness)
16. Create `v4-test.md` (with /v4-note awareness)
17. Create `v4-inspect.md` (with /v4-note awareness)

### Phase 5: Ship Phase
18. Create `v4-ship.md` (orchestrator)
19. Create `v4-close.md`

### Phase 6: Initialize Flow
20. Create `v4-initialize.md` (orchestrator)
21. Create `v4-ecosystem.md`
22. Create `v4-scaffold.md`
23. Create `v4-validate.md`
24. Create `v4-init-close.md`

### Phase 7: Cleanup
25. DELETE all /v2-* files
26. DELETE all unprefixed files
27. Update any cross-references

---

*End of Solution Proposal v4 (Refined)*
