---
date: 2026-07-06
slug: screen-frame-ownership
---

Title: Lean-code debt in ResumeGenerator.svelte deferred to slice 6

During the screen-frame-ownership build, the lean-code-reviewer flagged ResumeGenerator.svelte: nine forbidden verb names (handleGenerate, handleCancel, handleBack, handleRegenerate, handleSelectResume, handleLoadJob, handleClearLoaded, handleSaveJob, goToProfile) and handleGenerate as a five-job god function (input check, view/state mutation, status-interval + AbortController drive, resume read, error classification). All pre-existing. Decision: deferred to slice 6 (tailor-cv-screen), which owns generator-screen rework per the refined item's user-stated hard limit (Scope OUT). The Lean Code header this run had added to the file was removed again so the file does not over-claim compliance; the restyled-file convention ties headers to a file's editorial pass. Ledger visibility: one line added under SLICE_INDEX.md "Still open". Full findings: workbench/3-build/review/LEAN_CODE_REVIEW_2026-07-06_screen-frame-ownership.md.
