# Implementation Plan: v5 Skills Mandatory Questions

**Date:** 2026-01-07
**Feature:** v5-skills-mandatory-clarification-questions

## Affected Files

### Skill Files (Primary)

| File | Change Type | Description |
|------|-------------|-------------|
| ~/.claude/commands/v5-scope.md | Modify | Add intent + validation questions |
| ~/.claude/commands/v5-feature.md | Modify | Add entry confirmation |
| ~/.claude/commands/v5-requirements.md | Modify | Add persona + assumption questions |
| ~/.claude/commands/v5-ux.md | Modify | Add current state + review questions |
| ~/.claude/commands/v5-verify-analysis.md | Modify | Add high-risk resolution |
| ~/.claude/commands/v5-research.md | Modify | Add ecosystem preference question |
| ~/.claude/commands/v5-design.md | Modify | Add approach + validation questions |
| ~/.claude/commands/v5-checklist.md | Modify | Add completeness review |
| ~/.claude/commands/v5-verify-plan.md | Modify | Add issue resolution |
| ~/.claude/commands/v5-implement.md | Modify | Add pre-implementation check |
| ~/.claude/commands/v5-test.md | Modify | Add failure triage |
| ~/.claude/commands/v5-inspect.md | Modify | Add verification guidance |
| ~/.claude/commands/v5-close.md | Modify | Add commit confirmation |
| ~/.claude/commands/v5-reflect.md | Modify | Add retrospective prompts |
| ~/.claude/commands/v5-note.md | Modify | Add classification + priority |

### Orchestrator Files (No Questions)

| File | Change Type | Description |
|------|-------------|-------------|
| ~/.claude/commands/v5-analyze.md | No change | Orchestrator - delegates to sub-skills |
| ~/.claude/commands/v5-plan.md | No change | Orchestrator - delegates to sub-skills |
| ~/.claude/commands/v5-build.md | No change | Orchestrator - delegates to sub-skills |

## Database Changes

None.

## Implementation Approach

### Pattern Template

Each skill will follow this pattern for adding questions:

```markdown
### [Step Number]. [Question Step Name] (MANDATORY)

Use AskUserQuestion:

"[Question text]?"
- A) [Option with description]
- B) [Option with description]
- C) [Option with description]

[Detection triggers if applicable]

Document response in Clarification Log.
```

### Output Template

Each skill's output section will be updated to include:

```markdown
## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| [Question asked] | [User response] | [How it affected output] |
```

## Implementation Order

### Batch 1: Entry Points (Critical Path)

| Order | File | Rationale |
|-------|------|-----------|
| 1 | v5-scope.md | First user touchpoint, sets exploration/solution mode |
| 2 | v5-feature.md | Orchestrator entry, confirms before full flow |

### Batch 2: Analysis Phase

| Order | File | Rationale |
|-------|------|-----------|
| 3 | v5-requirements.md | Defines problem/personas |
| 4 | v5-ux.md | Needs current state visibility |
| 5 | v5-verify-analysis.md | Resolves high-risk assumptions |

### Batch 3: Planning Phase

| Order | File | Rationale |
|-------|------|-----------|
| 6 | v5-research.md | Respects existing ecosystem |
| 7 | v5-design.md | Architectural decisions |
| 8 | v5-checklist.md | Verification completeness |
| 9 | v5-verify-plan.md | Issue resolution |

### Batch 4: Build Phase

| Order | File | Rationale |
|-------|------|-----------|
| 10 | v5-implement.md | Pre-coding confirmation |
| 11 | v5-test.md | Failure handling |
| 12 | v5-inspect.md | Manual verification |

### Batch 5: Ship Phase

| Order | File | Rationale |
|-------|------|-----------|
| 13 | v5-close.md | Commit confirmation |
| 14 | v5-reflect.md | Retrospective capture |
| 15 | v5-note.md | Finding classification |

## Detailed Changes Per File

### 1. v5-scope.md

**Insert after line 19 (after "### 1. Capture Request"):**

```markdown
### 1b. Intent Clarification (MANDATORY)

Use AskUserQuestion:

**Question 1 - Intent:**
"What type of request is this?"
- A) I know what I want - define it precisely
- B) I'm exploring options - show me alternatives
- C) I have a problem - help me find solutions

**Question 2 - Confidence:**
"How confident are you about the solution approach?"
- A) Very confident - I've thought this through
- B) Somewhat confident - open to suggestions
- C) Not confident - need guidance

**Detection triggers** (suggest B/C if present in raw input):
- "maybe", "not sure", "alternatives", "options", "explore", "could", "might"
- Missing success criteria
- Vague language ("improve", "better", "faster")

Document in SCOPED_FEATURE:
- **Intent:** Exploration | Solution | Problem
- **Confidence:** High | Medium | Low
```

**Insert after line 48 (after classification handling):**

```markdown
### 4b. Scope Validation (MANDATORY)

Before writing output, present scope to user:

Use AskUserQuestion:
"Does this scope match your intent?"
- A) Yes, proceed
- B) Adjust scope - [specify changes]
- C) Too narrow - I wanted more
- D) Too broad - I wanted less

If B/C/D: Revise scope based on feedback, re-validate.
```

**Add to output format:**

```markdown
## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
```

---

### 2. v5-feature.md

**Insert after line 14 (after entry validation):**

```markdown
### Entry Confirmation (MANDATORY)

Use AskUserQuestion:
"Ready to implement '{feature-name}'. Any changes before we start?"
- A) Proceed as scoped
- B) Review scope first - show me the summary
- C) Adjust scope - run /v5-scope again

If B: Display SCOPED_FEATURE summary, then re-ask A/C.
If C: STOP → direct to /v5-scope.
```

---

### 3. v5-requirements.md

**Insert after line 8 (before "## Steps"):**

```markdown
### 0. Context Gathering (MANDATORY)

Use AskUserQuestion:

"Who is the primary user for this feature?"
- A) [Inferred persona from SCOPED_FEATURE]
- B) Different user type - specify

"What's the main pain point this solves?"
- A) [Inferred from scope description]
- B) Different pain point - specify
```

**Insert after line 52 (after Assumptions section):**

```markdown
### 4b. Assumption Validation (MANDATORY)

For each assumption with category noted, ask:

Use AskUserQuestion:
"I'm assuming: [assumption text]. Correct?"
- A) Yes, that's correct
- B) No - [provide correct information]
- C) Unsure - needs research

If any B: Update assumption.
If any C: Flag for resolution in verify-analysis.
```

**Add to output format:**

```markdown
## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
```

---

### 4. v5-ux.md

**Insert after line 9 (after skip condition):**

```markdown
### 0. Current State (MANDATORY)

Use AskUserQuestion:

"What's the current UI state for this feature area?"
- A) I'll describe it - [wait for description]
- B) No current UI - this is new
- C) Check the codebase - infer from existing templates

"Should I preserve existing UI patterns or rethink them?"
- A) Preserve - add new elements to existing design
- B) Refactor allowed - improve existing patterns
- C) Redesign welcome - propose better approaches
```

**Insert after line 32 (after State Definitions):**

```markdown
### 2b. State Review (MANDATORY)

Use AskUserQuestion:
"I identified these UI states: [list states]. Complete?"
- A) Looks complete
- B) Add state: [specify]
- C) Remove state: [specify]
```

**Add to output format:**

```markdown
## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
```

---

### 5. v5-verify-analysis.md

**Insert after line 36 (after Assumption Audit):**

```markdown
### 3b. High-Risk Resolution (MANDATORY)

For each assumption with Low confidence + High impact:

Use AskUserQuestion:
"High-risk assumption: '[assumption]'. How to proceed?"
- A) Accept risk - proceed anyway
- B) Research first - pause to validate
- C) Change approach - avoid this assumption
- D) Need stakeholder input - escalate

If any HIGH-RISK remains unresolved: Status = ISSUES, not VERIFIED.
```

**Add to output format:**

```markdown
## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
```

---

### 6. v5-research.md

**Insert after line 7 (before "## Steps"):**

```markdown
### 0. Existing Ecosystem Check (MANDATORY)

Before Context7 lookup, check project files:
- Read `.python-version` if exists
- Read `pyproject.toml` dependencies if exists
- Read `.nvmrc` if exists
- Read `package.json` dependencies if exists

If existing ecosystem detected:

Use AskUserQuestion:
"Project uses [detected versions/libraries]. Should I:"
- A) Respect existing versions - stay compatible
- B) Suggest upgrades - if beneficial
- C) Research alternatives - regardless of existing
```

**Add to output format:**

```markdown
## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
```

---

### 7. v5-design.md

**Insert after line 24 (after Affected Files):**

```markdown
### 1b. Approach Selection (MANDATORY)

If multiple valid implementation approaches exist:

Use AskUserQuestion:
"I can implement this using:"
- A) [Approach 1] - [tradeoff summary]
- B) [Approach 2] - [tradeoff summary]
- C) [Approach 3] - [tradeoff summary]

Document selected approach in IMPL_PLAN.
```

**Insert after line 48 (after Implementation Order):**

```markdown
### 4b. Plan Review (MANDATORY)

Use AskUserQuestion:
"Implementation order: [list steps]. Any concerns?"
- A) Looks good - proceed
- B) Change order - [specify]
- C) Missing step - [specify]
```

**Add to output format:**

```markdown
## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
```

---

### 8. v5-checklist.md

**Insert before output section:**

```markdown
### Checklist Review (MANDATORY)

Use AskUserQuestion:
"Created [N] verification points. Review summary:"
[Show checklist categories and counts]
- A) Looks complete
- B) Add checks for: [specify]
- C) Too many checks - simplify: [specify]
```

**Add to output format:**

```markdown
## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
```

---

### 9. v5-verify-plan.md

**Insert after issue detection:**

```markdown
### Issue Resolution (MANDATORY)

For each issue found:

Use AskUserQuestion:
"Plan issue: '[description]'. Resolution?"
- A) [Suggested fix 1]
- B) [Suggested fix 2]
- C) Accept as-is - note the risk
```

**Add to output format:**

```markdown
## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
```

---

### 10. v5-implement.md

**Insert after prerequisites:**

```markdown
### 0. Pre-Implementation (MANDATORY)

Use AskUserQuestion:
"Ready to write code for [feature]. Confirm:"
- A) Proceed with implementation
- B) Show plan summary first
- C) Start from specific step: [specify]
```

**Add to output format (if any):**

```markdown
## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
```

---

### 11. v5-test.md

**Insert in failure handling section:**

```markdown
### Test Failure Triage (MANDATORY)

If tests fail:

Use AskUserQuestion:
"[N] tests failed. How to proceed?"
- A) Fix code - make tests pass
- B) Update tests - tests are wrong
- C) Show failures - I'll decide
- D) Skip for now - document why
```

---

### 12. v5-inspect.md

**Insert before manual verification:**

```markdown
### Verification Guidance (MANDATORY)

Use AskUserQuestion:
"Please verify manually:"
[List verification items]

"Inspection results?"
- A) All pass
- B) Issues found: [describe]
- C) Can't verify [item] - need help
```

---

### 13. v5-close.md

**Insert before commit:**

```markdown
### Commit Confirmation (MANDATORY)

Use AskUserQuestion:
"Commit message: '[message]'. Proceed?"
- A) Commit as shown
- B) Change message: [specify]
- C) Add files: [specify]
- D) Don't commit yet
```

---

### 14. v5-reflect.md

**Insert in retrospective section:**

```markdown
### Retrospective Prompts (MANDATORY)

Use AskUserQuestion (free text):
"What went well during this feature?"
[Capture response]

"What could be improved?"
[Capture response]

"Patterns to document for future?"
- A) Yes: [specify]
- B) Nothing notable
```

---

### 15. v5-note.md

**Insert at note capture:**

```markdown
### Note Classification (MANDATORY)

Use AskUserQuestion:
"What type of finding?"
- A) Bug discovered
- B) Technical debt
- C) Enhancement idea
- D) Documentation gap
- E) Process improvement

"Priority?"
- A) Urgent - blocks work
- B) Important - for later
- C) Nice to have
```

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Questions slow down workflow | Medium | Medium | Keep questions focused, allow "proceed" as first option |
| User fatigue from too many questions | Low | Medium | "Always ask" per user choice, but questions are contextual |
| Skill files become too long | Low | Low | Questions are concise blocks, ~20-30 lines each |
| Breaking existing workflows | Low | High | No format changes to artifacts except adding Clarification Log |

## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| Scope: All skills or incremental? | All v5 skills | Full overhaul, 15 files modified |
| Skip logic for complete specs? | Always ask | No skip mechanism, every run validates |
| Question limit per skill? | As needed | No artificial limit |
