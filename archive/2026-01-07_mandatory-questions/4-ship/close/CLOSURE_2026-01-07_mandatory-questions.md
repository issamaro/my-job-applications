# Closure: v5 Skills Mandatory Questions

**Date:** 2026-01-07
**Feature:** v5-skills-mandatory-clarification-questions

## Deliverables

| Item | Status | Location |
|------|--------|----------|
| Code (skill files) | Complete | ~/.claude/commands/v5-*.md |
| Tests | PASS | archive/2026-01-07_mandatory-questions/3-build/test/ |
| Inspection | PASS | archive/2026-01-07_mandatory-questions/3-build/inspect/ |
| Change Log | Complete | archive/2026-01-07_mandatory-questions/4-ship/close/ |
| Backlog moved | Complete | backlog/done/ |
| Archived | Complete | archive/2026-01-07_mandatory-questions/ |
| Committed | Complete | See below |

## Commit Reference

- **Hash:** 5e40f96
- **Message:** feat: Add mandatory clarification questions to all v5 skills
- **Files:** 9 files, 1655 insertions

## Archive Location

```
archive/2026-01-07_mandatory-questions/
├── 2-plan/
│   ├── checklist/
│   ├── design/
│   ├── research/
│   └── verify/
├── 3-build/
│   ├── inspect/
│   └── test/
└── 4-ship/
    ├── close/
    └── reflect/
```

## Summary

Added mandatory AskUserQuestion blocks to 15 v5 skill files. Every skill now:
1. Asks at least one clarifying question before proceeding
2. Documents questions/answers in Clarification Log
3. Uses "(MANDATORY)" marker for question blocks

## Note on Skill File Location

The actual skill files are in `~/.claude/commands/` which is a global user configuration directory, not part of this repository. Only the planning/verification artifacts are committed to the project.

## Clarification Log

| Question | Answer | Impact |
|----------|--------|--------|
| Commit confirmation | Commit as shown | Created commit 5e40f96 |
