# Folder Structure Reorganization - SCOPED_FEATURE

**Size:** M
**Scoped:** 2026-01-06
**Files affected:** TBD (depends on analysis)
**Dependencies:** None
**Ready for:** /v4-feature

---

## User Intent (Preserved)

> "I don't like the current structure of the project. Give relevant alternatives."

**Concerns raised:**
- Too many files
- Potential dead/unnecessary files
- Desire for grouping (backend vs frontend vs docs, or less strict but valuable)

**Key note:** User is exploring options, not prescribing a solution. They want alternatives presented, not a predetermined reorganization.

---

## Scope (IN)

- Understand current structure deeply
- Identify actual problems (not assumed ones)
- Present reorganization alternatives with honest trade-offs
- Let user decide direction before implementing anything

## Out of Scope (NOT)

- Jumping to implementation without user approval
- Prescribing a single "correct" structure

## Success Criteria

- [ ] User understands current structure's strengths and weaknesses
- [ ] User sees 2-3 viable alternatives
- [ ] User chooses direction (or decides current structure is fine)
- [ ] If change chosen, implementation respects the decision

---

## ⚠️ Process Note for /v4-feature

**This item needs further refinement during Analyze phase.** The user expressed uncertainty about what they want. The /v4-feature workflow should:

1. Treat Analyze phase as exploratory
2. Present findings and alternatives before planning implementation
3. Use AskUserQuestion to validate direction before proceeding to Plan

This is an "intent-first" scoped item, not a "solution-defined" one.
