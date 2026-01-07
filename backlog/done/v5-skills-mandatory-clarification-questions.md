# SCOPED_FEATURE: v5 Skills Mandatory Clarification Questions

**Size:** XL (4 indicators)
**Date:** 2026-01-07
**Estimated Files:** 18 skill files in `~/.claude/commands/`
**Dependencies:** None

## Description

Add mandatory `AskUserQuestion` calls to all v5 skills. Every skill invocation must ask at least one clarifying question before producing output. Questions should be asked until clarity is achieved (no artificial limit).

## Scope IN

- **All v5 skills** (18 files): scope, analyze, requirements, ux, research, design, checklist, verify-analysis, verify-plan, plan, build, implement, test, inspect, ship, close, reflect, note
- **Mandatory questioning gates** at entry and/or mid-execution
- **Clarification log** in output artifacts
- **Detection triggers** for uncertainty, ambiguity, conflicts
- **Always ask** policy (even when spec appears complete)

## Out of Scope (NOT)

- v4 skills (deprecated, will be removed)
- Making questions skippable via flags
- Backwards compatibility with old artifacts
- Changes to artifact output formats (except adding clarification log)

## Success Criteria

- [ ] Every v5 skill file contains at least one `AskUserQuestion` instruction
- [ ] Exploration vs solution intent is detected and asked about in v5-scope
- [ ] High-risk assumptions trigger questions in v5-verify-analysis
- [ ] UX skill asks for current state visibility
- [ ] Research skill asks about existing ecosystem preferences
- [ ] Clarification log section appears in all output artifacts
- [ ] Skills can trigger re-scoping when analysis reveals problems

---

## Implementation Specification

### Phase 1: Entry Point Skills

#### v5-scope.md

**Add after "Capture Request" step:**

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

**Detection triggers** (auto-select B/C if present):
- "maybe", "not sure", "alternatives", "options", "explore", "could", "might"
- Missing success criteria in raw item
- Vague language ("improve", "better", "faster")

Document in output:
**Intent:** Exploration | Solution | Problem
**Confidence:** High | Medium | Low
```

**Add after classification step:**

```markdown
### 4b. Scope Validation (MANDATORY)

Present the proposed scope to user via AskUserQuestion:

"Does this scope match your intent?"
- Show: Description, Scope IN, Out of Scope, Success Criteria
- Options:
  - A) Yes, proceed
  - B) Adjust scope (specify what to change)
  - C) This is too narrow - I wanted more
  - D) This is too broad - I wanted less
```

#### v5-feature.md

**Add after entry validation:**

```markdown
### Entry Clarification (MANDATORY)

Before loading SCOPED_FEATURE, ask:

"Ready to implement {feature-name}. Any last-minute changes?"
- A) Proceed as scoped
- B) I want to adjust scope first → direct to /v5-scope
- C) Show me the scope summary before proceeding
```

---

### Phase 2: Analysis Skills

#### v5-requirements.md

**Add before Problem Statement:**

```markdown
### 0. Context Gathering (MANDATORY)

Use AskUserQuestion:

"Who is the primary user for this feature?"
- List detected personas from SCOPED_FEATURE
- Allow "Other" for custom input

"What's the main pain point this solves?"
- A) [Inferred from scope]
- B) Different pain point (specify)

If multiple BDD scenarios possible:
"Which error scenarios should I cover?"
- Multiselect from detected error types
```

**Add after Assumptions step:**

```markdown
### 4b. Assumption Validation (MANDATORY)

For each assumption with Low/Medium confidence:

"I'm assuming [assumption]. Is this correct?"
- A) Yes
- B) No, actually [correct answer]
- C) I don't know - let's research
```

#### v5-ux.md

**Add at start:**

```markdown
### 0. Current State (MANDATORY)

Use AskUserQuestion:

"Can you describe or show the current UI state?"
- A) I'll paste a screenshot → wait for image
- B) I'll describe it → wait for description
- C) This is a new UI, no current state
- D) Use existing codebase to understand current state

"Should I preserve or rethink the current UI patterns?"
- A) Preserve existing patterns, add new elements
- B) Okay to refactor existing patterns
- C) Complete redesign is acceptable
```

**Add after State Definitions:**

```markdown
### 2b. State Confirmation (MANDATORY)

"I identified these UI states: [list]. Missing any?"
- A) Looks complete
- B) Add: [specify]
- C) Remove: [specify]
```

#### v5-verify-analysis.md

**Add after Assumption Audit:**

```markdown
### 3b. High-Risk Resolution (MANDATORY)

For each HIGH-RISK assumption (Low confidence + High impact):

Use AskUserQuestion:
"This assumption is risky: [assumption]. How should we proceed?"
- A) Accept the risk - proceed anyway
- B) Research to validate - pause for investigation
- C) Change approach to avoid this assumption
- D) Ask stakeholder for clarification

Do NOT proceed with VERIFIED status if unresolved HIGH-RISK assumptions exist.
```

---

### Phase 3: Planning Skills

#### v5-research.md

**Add at start:**

```markdown
### 0. Existing Ecosystem Check (MANDATORY)

Before Context7 lookup, check project files:
- .python-version → existing Python version
- pyproject.toml → existing dependencies
- .nvmrc → existing Node version
- package.json → existing npm packages

If existing ecosystem detected, ask:
"I see you're using [detected stack]. Should I:"
- A) Respect existing versions/libraries
- B) Suggest upgrades if beneficial
- C) Research alternatives regardless
```

#### v5-design.md

**Add after Affected Files Analysis:**

```markdown
### 1b. Architectural Preferences (MANDATORY)

If multiple valid approaches exist, ask:

"I can implement this using:"
- A) [Approach 1 - description]
- B) [Approach 2 - description]
- C) [Approach 3 - description]

"How should I handle [specific technical decision]?"
- Present options with tradeoffs
```

**Add after Implementation Order:**

```markdown
### 4b. Plan Validation (MANDATORY)

"Here's my implementation order: [list]. Concerns?"
- A) Looks good
- B) Change order (specify)
- C) Missing something (specify)
```

#### v5-checklist.md

**Add after generating checklist:**

```markdown
### Checklist Review (MANDATORY)

"I created [N] verification points. Review:"
- Show checklist summary
- A) Looks complete
- B) Add checks for: [specify]
- C) Remove unnecessary checks: [specify]
```

#### v5-verify-plan.md

**Add if design issues found:**

```markdown
### Design Issue Resolution (MANDATORY)

For each issue found:

"Issue: [description]. How to resolve?"
- A) [Suggested fix 1]
- B) [Suggested fix 2]
- C) Accept as-is with noted risk
```

---

### Phase 4: Build Skills

#### v5-implement.md

**Add before coding:**

```markdown
### 0. Pre-Implementation Check (MANDATORY)

"Ready to write code. Confirm:"
- A) Proceed with implementation
- B) Wait - I want to review the plan first
- C) Skip to specific step (specify)
```

#### v5-test.md

**Add if tests fail:**

```markdown
### Test Failure Triage (MANDATORY)

"[N] tests failed. How should I proceed?"
- A) Fix code to make tests pass
- B) Tests are wrong - update tests
- C) Skip these tests for now (explain why)
- D) Show me the failures first
```

#### v5-inspect.md

**Add for manual verification:**

```markdown
### Inspection Guidance (MANDATORY)

"Please verify these items manually:"
- [List items requiring human verification]

"What did you find?"
- A) All checks pass
- B) Issues found: [describe]
- C) Can't verify [specific item] - need help
```

---

### Phase 5: Ship Skills

#### v5-close.md

**Add before commit:**

```markdown
### Commit Confirmation (MANDATORY)

"Ready to commit with message: [message]. Proceed?"
- A) Commit as shown
- B) Change message to: [specify]
- C) Add more files to commit
- D) Don't commit yet
```

#### v5-reflect.md

**Add for retrospective:**

```markdown
### Retrospective Prompts (MANDATORY)

"What went well during this feature?"
- Free text input

"What could be improved?"
- Free text input

"Any patterns to document for future?"
- A) Yes: [specify]
- B) Nothing notable
```

#### v5-note.md

**Add at capture:**

```markdown
### Note Classification (MANDATORY)

"What type of finding is this?"
- A) Bug discovered
- B) Technical debt
- C) Enhancement idea
- D) Documentation gap
- E) Process improvement

"Priority?"
- A) Urgent - blocks current work
- B) Important - capture for later
- C) Nice to have
```

---

### Output Format Addition

All skills that produce artifacts must add a **Clarification Log** section:

```markdown
## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| [Question asked] | [User response] | [How it affected output] |
```

---

## Notes

- **Always ask** policy means even well-specified inputs get validation questions
- Questions should be contextual - don't ask about UX for backend-only features
- Use multiselect for questions with multiple valid answers
- Allow "Other" option for unexpected user needs
- Questions are part of the skill execution, not a separate step
