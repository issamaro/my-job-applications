# Project Phase

```
current_phase: prototype
phase_since: 2026-05-12
notes: bootstrap — reassess with /v6-roadmap
```

The current phase is marked `[CURRENT]`. Tick boxes as work lands. Advance `current_phase` and `phase_since` above when the gate criteria for the next phase are met. Run `/v6-roadmap` to reassess and identify what to ship next.

---

## Phase 1 — Prototype  [CURRENT]

**Goal:** prove the core interaction works end-to-end. Localhost-grade.
**Gate to next phase (Alpha):** core happy path runs end-to-end and at least one trusted user (incl. yourself) has completed it without you driving.

- [ ] Framework chosen, with one-line rationale recorded
- [ ] Runtime + lockfile committed
- [ ] One-command local dev (documented in README)
- [ ] Core happy path works end-to-end with fixture data
- [ ] Target device class decided (desktop / mobile / both)
- [ ] Git repo initialized, README has run instructions

## Phase 2 — Alpha

**Goal:** real URL, real data, ~1–10 trusted users (incl. dogfooding).
**Gate to next phase (Beta):** used daily for 2+ weeks without data loss, and someone besides you has completed the core flow.

- [ ] Real hosting target + HTTPS
- [ ] One-command (or auto) deploy from main
- [ ] Real database (managed or persistent local)
- [ ] Migrations tool + at least one migration applied
- [ ] Backups configured + restored once
- [ ] Real auth (not hardcoded user)
- [ ] Sessions + password reset / re-auth path
- [ ] Secrets in env / vault, not in repo
- [ ] HTTPS only, HSTS, basic input validation
- [ ] Frontend + backend error tracking
- [ ] Uptime ping on the homepage
- [ ] Empty / loading / error states for core flow
- [ ] Privacy policy stub (if collecting user data)
- [ ] Account deletion path (even if manual)

## Phase 3 — Beta

**Goal:** strangers can sign up; things must not silently break.
**Gate to next phase (GA):** N weeks of stable error rate, no data-loss incidents, at least one non-friend retained user.

- [ ] Staging environment mirroring prod
- [ ] CI runs tests on PRs/main before deploy
- [ ] Health-check endpoint + uptime alerts
- [ ] Unit tests on core domain logic
- [ ] One e2e test of signup → core action
- [ ] Pre-commit lint + format
- [ ] Accessibility smoke test (axe or keyboard pass)
- [ ] Email verification + rate-limited auth
- [ ] Audit log for sensitive actions
- [ ] Self-serve data export + account deletion
- [ ] PII inventory written down
- [ ] Retention policy per data type
- [ ] Restore drill done in staging
- [ ] Full design tokens (color / type / spacing / radius)
- [ ] WCAG 2.1 AA on top flows
- [ ] Keyboard navigation works
- [ ] Real privacy policy + terms of service
- [ ] Transactional email with SPF/DKIM/DMARC

## Phase 4 — GA (v1)

**Goal:** marketing-page public, defensible, on-call-able.
**Gate to next phase (Scale & Harden):** launched, didn't fall over, ready to grow.

- [ ] Availability + latency + error-rate SLOs stated
- [ ] Error budget policy
- [ ] Distributed tracing or request-correlation IDs
- [ ] Metrics dashboard for top 5 user flows
- [ ] Real User Monitoring
- [ ] Synthetic checks on critical flows
- [ ] Alert routing to a channel you actually watch
- [ ] Runbooks for top 5 likely alerts
- [ ] CSP + Permissions-Policy headers
- [ ] Threat model documented
- [ ] OWASP Top 10 walked
- [ ] First external pen-test (or rigorous self-audit)
- [ ] SAST in CI
- [ ] Incident response template
- [ ] Landing page distinct from app
- [ ] Sitemap + robots + Open Graph
- [ ] Status page
- [ ] Support channel + response SLA
- [ ] Changelog

## Phase 5 — Scale & Harden

**Goal:** survives growth and adversaries.
**Gate to next phase:** continuous — this phase doesn't end.

- [ ] Load tests at 2× expected peak
- [ ] Caching layer with invalidation rules
- [ ] Async paths for heavy writes (queue)
- [ ] Multi-region or DR plan if uptime demands it
- [ ] OLTP / OLAP split
- [ ] Feature flags
- [ ] Canary or blue/green deploys
- [ ] Migration rollback drills
- [ ] CODEOWNERS + ADR directory (if team grows)
- [ ] On-call rotation + paging policy
- [ ] Postmortem cadence
- [ ] Annual pen-test + access reviews
- [ ] Backup restore on a calendar

---

## Brownfield adoption

If this project predates the phase model, run `/v6-roadmap` once to assess current state honestly. Tick only what you can prove is true today; everything else stays unticked.
