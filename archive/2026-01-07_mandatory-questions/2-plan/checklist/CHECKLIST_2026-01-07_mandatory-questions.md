# Verification Checklist: v5 Skills Mandatory Questions

**Date:** 2026-01-07
**Feature:** v5-skills-mandatory-clarification-questions

## Pre-Implementation Checks

- [ ] All 15 skill files exist in ~/.claude/commands/
- [ ] Backup of original files created (optional but recommended)
- [ ] Understand markdown skill file format

## Per-File Implementation Checks

### Batch 1: Entry Points

#### v5-scope.md
- [ ] Intent Clarification block added after "Capture Request"
- [ ] Contains Question 1 (request type) with 3 options
- [ ] Contains Question 2 (confidence) with 3 options
- [ ] Detection triggers documented
- [ ] Scope Validation block added after classification
- [ ] Clarification Log section added to output format
- [ ] SCOPED_FEATURE format includes Intent + Confidence fields

#### v5-feature.md
- [ ] Entry Confirmation block added after entry validation
- [ ] Contains 3 options (proceed/review/adjust)
- [ ] Conditional logic for B (show summary) documented
- [ ] Conditional logic for C (redirect to scope) documented

### Batch 2: Analysis Phase

#### v5-requirements.md
- [ ] Context Gathering block added before Steps
- [ ] Primary user question with inferred option
- [ ] Pain point question with inferred option
- [ ] Assumption Validation block added after Assumptions
- [ ] Per-assumption questioning pattern documented
- [ ] Clarification Log section added to output format

#### v5-ux.md
- [ ] Current State block added after skip condition
- [ ] Current state question with 3 options
- [ ] Preserve/refactor question with 3 options
- [ ] State Review block added after State Definitions
- [ ] Clarification Log section added to output format

#### v5-verify-analysis.md
- [ ] High-Risk Resolution block added after Assumption Audit
- [ ] 4 resolution options documented (accept/research/change/escalate)
- [ ] VERIFIED status conditional on resolution documented
- [ ] Clarification Log section added to output format

### Batch 3: Planning Phase

#### v5-research.md
- [ ] Existing Ecosystem Check block added before Steps
- [ ] File checks documented (.python-version, pyproject.toml, .nvmrc, package.json)
- [ ] Ecosystem preference question with 3 options
- [ ] Clarification Log section added to output format

#### v5-design.md
- [ ] Approach Selection block added after Affected Files
- [ ] Multiple approach presentation pattern documented
- [ ] Plan Review block added after Implementation Order
- [ ] 3 review options documented
- [ ] Clarification Log section added to output format

#### v5-checklist.md
- [ ] Checklist Review block added before output
- [ ] Summary presentation pattern documented
- [ ] 3 review options documented
- [ ] Clarification Log section added to output format

#### v5-verify-plan.md
- [ ] Issue Resolution block added after issue detection
- [ ] Per-issue questioning pattern documented
- [ ] Clarification Log section added to output format

### Batch 4: Build Phase

#### v5-implement.md
- [ ] Pre-Implementation block added after prerequisites
- [ ] 3 confirmation options documented
- [ ] Clarification Log section added (if applicable)

#### v5-test.md
- [ ] Test Failure Triage block added in failure handling
- [ ] 4 triage options documented
- [ ] Conditional execution on failures documented

#### v5-inspect.md
- [ ] Verification Guidance block added before manual verification
- [ ] Verification item presentation documented
- [ ] 3 result options documented

### Batch 5: Ship Phase

#### v5-close.md
- [ ] Commit Confirmation block added before commit
- [ ] 4 confirmation options documented
- [ ] Message display pattern documented

#### v5-reflect.md
- [ ] Retrospective Prompts block added
- [ ] Free text "went well" question documented
- [ ] Free text "improve" question documented
- [ ] Pattern capture question with 2 options

#### v5-note.md
- [ ] Note Classification block added at capture
- [ ] Finding type question with 5 options
- [ ] Priority question with 3 options

## Post-Implementation Checks

### Syntax Validation
- [ ] All modified files have valid YAML frontmatter
- [ ] All markdown headers are properly formatted
- [ ] No broken internal references

### Consistency Checks
- [ ] All question blocks use "Use AskUserQuestion:" pattern
- [ ] All question blocks marked "(MANDATORY)"
- [ ] All options use A/B/C/D format
- [ ] All skills with output have Clarification Log section

### Integration Testing
- [ ] v5-scope runs and asks intent question
- [ ] v5-scope asks validation question before output
- [ ] v5-requirements asks persona question
- [ ] v5-ux asks current state question
- [ ] v5-verify-analysis asks about high-risk assumptions (if any)
- [ ] v5-design asks approach question (if multiple valid)
- [ ] v5-close asks commit confirmation

## Success Criteria Mapping

| Success Criterion | Verification |
|-------------------|--------------|
| Every v5 skill has AskUserQuestion | Per-file checks above |
| Exploration vs solution detected in scope | v5-scope Intent question |
| High-risk assumptions trigger questions | v5-verify-analysis block |
| UX asks for current state | v5-ux Current State block |
| Research asks ecosystem preferences | v5-research Ecosystem Check |
| Clarification Log in outputs | Per-file output format check |
| Skills can trigger re-scoping | v5-verify-analysis SCOPE_CHANGE status |

## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| N/A - checklist phase | N/A | Comprehensive checks defined |
