# Methodology Improvement: Problem Statement

**Date:** 2026-01-03
**Scope:** Analysis of v3 slash commands, archive retrospectives, and user observations

---

## 1. Problems Identified from v3 Commands Architecture

### 1.1 Missing Project Initialization Phase
The current workflow assumes an existing codebase. There is no orchestrator phase for:
- Greenfield projects requiring architectural decisions
- High-level feature breakdown from user intent
- Technology stack decisions before implementation begins

### 1.2 Disconnected Scope from Product Context
`/v3-scope` operates in isolation:
- Not connected to a broader product backlog
- Does not incorporate learnings from previous retrospectives
- User intents and retrospective items are not fed into scope decisions

### 1.3 UX Skill Lacks Critical Thinking Capabilities
`/v3-ux` is additive-only and doesn't:
- Challenge existing semantics ("do we still need this?")
- Ask for screenshots to understand current state
- Consider refactoring or removing existing UI elements
- Think outside the box of what already exists

### 1.4 Reflection Timing is Wrong
`/v3-reflect` only runs at the end during `/v3-ship`:
- Issues encountered mid-implementation are not captured in context
- Learning happens too late to benefit the current feature
- Ad-hoc problems require waiting until closure to document

### 1.5 Archive Timing Creates Inconsistency
Currently `/v3-ship` runs `/v3-close` (which archives) BEFORE `/v3-reflect`:
- Retrospective is written after the workbench is already archived
- Retrospective should capture the final state before archiving
- Order should be: reflect FIRST (capture lessons), THEN archive everything together

### 1.6 verify-analysis Doesn't Guard Scope Expansion
`/v3-verify-analysis` checks completeness but doesn't:
- Assess if analysis findings expanded scope beyond manageable
- Guard against analysis revealing too many changes
- Force re-scoping if complexity grew during analysis

### 1.7 No Project Initialization Orchestrator
The v3 workflow assumes an existing codebase. For greenfield projects, there is no:
- Orchestrator phase for architectural decisions based on user intent
- Structured breakdown of user intent into high-level features
- Explicit decision-making before the first line of code

**Missing sub-phases for initialization:**

**1.7.1 No Ecosystem Decision Phase (Initialization)**
Before the first feature, new projects need:
- Explicit technology stack selection (frameworks, runtimes)
- Version pinning decisions using context7 for compatibility
- An artifact documenting "why this stack" for this project

**1.7.2 No First-Commit Architecture Verification (Initialization)**
For new projects, the very first commit should be:
- A "hello world" skeleton proving the architecture works
- Minimal working code validating chosen ecosystem
- Not a full feature, just proof the stack is viable

**1.7.3 No Robustness Verification (Initialization)**
Before building features on a new project:
- No check that the initialized app is robust
- No validation of error handling patterns
- Architecture should be verified as solid before features are added

*Note: These are initialization-time concerns for NEW projects, not per-feature concerns during normal sprints. Per-feature library research is handled by `/v3-research`.*

---

## 2. Problems Identified from Archive Retrospectives

### 2.1 Recurring: SCSS Token Misuse
Across multiple features (SAVED-JOB-DESCRIPTIONS, EXPANDABLE-RESUMES):
- Undefined SCSS variables used (`$spacing-sm` doesn't exist)
- Available tokens not checked before writing styles
- No checklist item for "SCSS variables exist in _tokens.scss"

### 2.2 Recurring: Invalid HTML Structure
Multiple features had button nesting issues:
- `<button>` inside `<button>` (SAVED-JOB-DESCRIPTIONS, EXPANDABLE-RESUMES)
- Semantic HTML not verified during component design
- UX wireframes don't indicate clickable region constraints

### 2.3 Recurring: System Dependencies Not Documented Early
From PDF-EXPORT retrospective:
- WeasyPrint required `DYLD_FALLBACK_LIBRARY_PATH`
- Not discoverable from pip install alone
- Environment requirements belong in research phase, not debugging

### 2.4 No Frontend E2E Tests
Consistently mentioned across retrospectives:
- Only manual inspection for frontend
- No Playwright or Cypress tests
- Risk of regression when features interact

### 2.5 Toast/Notification Integration Inconsistent
From SAVED-JOB-DESCRIPTIONS:
- `showToast` calls exist but Toast component not integrated
- Existing patterns not discovered during implementation
- Cross-cutting concerns need explicit checklist items

### 2.6 Watch Mode Not Verified
From SCSS-REFACTOR:
- Build verified but live recompilation not tested
- Dev workflow not part of verification checklist

### 2.7 LLM Prompt Engineering Not Planned For
From JOB-TAILORED-RESUME:
- Prompt iteration required "several refinements"
- Not allocated as implementation work in planning
- Should be treated as code requiring iteration

### 2.8 Environment Check Missing from Checklists
From PDF-EXPORT:
- System dependencies (brew, library paths) discovered during testing
- Should be Section 0 verification item

### 2.9 Browser vs PDF Rendering Differences
From PDF-EXPORT:
- Assumption "Live preview matches PDF exactly" was only partially correct
- Minor differences between browser and WeasyPrint rendering
- Could have been flagged as known limitation upfront

---

## 3. Problems Identified from User Observations

### 3.1 UX Skill is Too Conservative
User observation: "Don't hesitate to assess the need of a rebuild"
- Current UX adds features without questioning existing ones
- "Frankensteinization" risk: bolting on without cleaning up
- Should ask: "do we still need this with this new user intent?"

### 3.2 Semantic Challenges are Avoided
User observation: "Semantic should always be challenged without being afraid to change it"
- Current UX preserves existing semantics by default
- No mechanism to propose semantic restructuring
- UX designer mindset should be more exploratory

### 3.3 Visual Context is Not Requested
User observation: "Ask screenshots if needed"
- UX skill doesn't request visual evidence of current state
- Wireframes are created without seeing current UI
- Screenshots would inform better design decisions

### 3.4 Scope is Disconnected from Continuous Improvement
User observation: "Should be part of a broader product backlog stage"
- Individual features are scoped in isolation
- Retrospective learnings don't flow back to scope
- No backlog accumulation mechanism

### 3.5 Reflection is Not Continuous
User observation: "every time agent encounters an issue"
- Issues during build are not immediately documented
- Waiting until /v3-reflect loses context
- Mid-implementation friction should be captured in-moment

### 3.6 Archive Order is Wrong
User observation: "archive the workbench before /v3-reflect runs"
- Current order: close → reflect → (implicitly archive during close)
- Should be: archive workbench state → then write retrospective

### 3.7 Scope Creep After Analysis Not Detected
User observation: "make sure the scope remains manageable after analysis"
- Analysis can reveal complexity not visible at scoping
- No checkpoint to re-assess scope based on findings
- Features can grow beyond single-feature scope during analysis

### 3.8 No Project Initialization Orchestrator with Sub-Phases
User observation: "Initializer orchestrator phase consisting of architectural decisions based on user intent and high level features"

The v3 workflow lacks a dedicated initialization orchestrator for new projects. User proposed sub-phases:

**Sub-phase: `/ecosystem`**
User observation: "Decides what to use, which version (use context7)"
- Technology stack decisions should be explicit, not embedded
- Context7 should be used systematically for version compatibility
- Produces an artifact: ecosystem decisions for this project

**Sub-phase: `/build` (for initialization)**
User observation: "build the first commit architecture with a hello world working"
- First commit should prove architecture viability
- Not a full feature, just a working skeleton
- Validates ecosystem choices before building features

**Sub-phase: `/verify` (for initialization)**
User observation: "check whether the app is robust"
- After hello world, verify the foundation is solid
- Check error handling patterns, resilience
- Architecture should be robust before adding features

*Note: These are sub-commands of `/initializer` for NEW projects only, not for normal feature sprints.*

---

## 4. Problem Categories Summary

| Category | Count | Description |
|----------|-------|-------------|
| **Missing Initialization Phase** | 1 | Project bootstrapping orchestrator with 3 sub-phases (ecosystem, build, verify) |
| **Timing/Order** | 2 | Reflect timing (should be continuous), Archive order (reflect before archive) |
| **Scope Management** | 2 | Backlog integration, Post-analysis scope verification |
| **UX Limitations** | 3 | No visual input, No semantic challenge, Additive-only |
| **Checklist Gaps** | 5 | SCSS tokens, HTML validity, Environment, Toast, Watch mode |
| **Testing Gaps** | 2 | E2E frontend, LLM prompt iteration |

---

## 5. Cross-Cutting Themes

### Theme A: Continuous Learning Not Integrated
Retrospectives capture lessons but don't feed back into:
- Future scope decisions
- Checklist improvements
- UX design considerations

### Theme B: No Foundation Verification for New Projects
For existing projects, v3 verifies features well:
- Feature requirements (spec coverage)
- Feature UX (design match)
- Feature tests (passing)

But for NEW projects, there's no verification of:
- Ecosystem viability (stack choices work together)
- Architecture validity (hello world skeleton works)
- Foundation robustness (error handling, resilience)

*This is an initialization-time gap, not a per-feature gap.*

### Theme C: UX is Documentation-Driven, Not Discovery-Driven
Current UX produces:
- User journeys
- State definitions
- Wireframes

But doesn't engage in:
- Questioning existing design
- Requesting visual context
- Proposing alternative approaches

### Theme D: Analysis Can Expand Scope Unchecked
The flow: Scope → Requirements → UX → Verify
Allows complexity to grow at each step without re-checking if scope is still appropriate.

---

*End of Problem Statement*
