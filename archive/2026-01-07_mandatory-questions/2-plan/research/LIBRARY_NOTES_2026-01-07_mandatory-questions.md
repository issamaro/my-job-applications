# Library Notes: v5 Skills Mandatory Questions

**Date:** 2026-01-07
**Feature:** v5-skills-mandatory-clarification-questions

## Runtime

No runtime changes - this feature modifies markdown skill files only.

## Dependencies

None. Skills are plain markdown files interpreted by Claude Code.

## Skill File Format Analysis

### Location
```
~/.claude/commands/v5-*.md
```

### Structure
```markdown
---
description: [Short description for skill picker]
argument-hint: [Optional argument placeholder]
allowed-tools: [Optional tool permissions]
---

# [Skill Name]

**Input:** [What the skill expects]
**Output:** [What the skill produces]

## Steps

### 1. [Step Name]
[Instructions]

### 2. [Step Name]
[Instructions]

## Output
[Output format specification]

## Next
[What skill to invoke next]
```

### Key Patterns

1. **AskUserQuestion usage** - Reference the tool by name in instructions:
   ```markdown
   Use AskUserQuestion:
   "Question text?"
   - A) Option 1
   - B) Option 2
   ```

2. **Conditional logic** - Use "If" statements:
   ```markdown
   If [condition]: [action]
   ```

3. **Detection triggers** - List patterns to watch for:
   ```markdown
   **Detection triggers:**
   - "keyword1", "keyword2"
   - [pattern description]
   ```

4. **Output documentation** - Add to artifact format:
   ```markdown
   ## Clarification Log
   | Question | Answer | Impact |
   |----------|--------|--------|
   ```

## Existing Question Pattern

Only one skill currently asks questions:

**v5-ecosystem.md:46**
```markdown
If Python project lacks pyproject.toml: STOP and ask user whether to create with `uv init`.
```

This is the pattern to replicate across all skills.

## Files to Modify

| File | Size | Questions to Add |
|------|------|------------------|
| v5-scope.md | 1880 bytes | 2 (intent, validation) |
| v5-feature.md | 1360 bytes | 1 (last-minute changes) |
| v5-requirements.md | 1607 bytes | 2 (persona, assumptions) |
| v5-ux.md | 2370 bytes | 2 (current state, states review) |
| v5-verify-analysis.md | 1941 bytes | 1 (high-risk resolution) |
| v5-research.md | 1197 bytes | 1 (ecosystem preferences) |
| v5-design.md | 1556 bytes | 2 (approach, validation) |
| v5-checklist.md | 1820 bytes | 1 (completeness review) |
| v5-verify-plan.md | 1645 bytes | 1 (issue resolution) |
| v5-implement.md | 2037 bytes | 1 (pre-implementation) |
| v5-test.md | 1127 bytes | 1 (failure triage) |
| v5-inspect.md | 1412 bytes | 1 (verification guidance) |
| v5-close.md | 1936 bytes | 1 (commit confirmation) |
| v5-reflect.md | 1564 bytes | 2 (what went well/improved) |
| v5-note.md | 1457 bytes | 2 (classification, priority) |
| v5-analyze.md | 1291 bytes | 0 (orchestrator only) |
| v5-plan.md | 1473 bytes | 0 (orchestrator only) |
| v5-build.md | 1445 bytes | 0 (orchestrator only) |

**Total:** 18 files, 21 question blocks to add

## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| N/A - research phase | N/A | Direct file analysis used |
