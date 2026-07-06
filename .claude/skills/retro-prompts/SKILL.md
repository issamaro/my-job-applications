---
name: retro-prompts
description: Retrospective on LLM resume-generation quality. Walks one (or several) recent generated_resumes through input → prompt-at-time-of-generation → output, grades against documented contracts (350-char caps, first-person summary, all work_experiences included, match_score realism), correlates findings with recent commits to services/llm/base.py, then asks the user targeted questions before recommending changes to JD shape, master-data shape, output shape, and separation of concerns. Use whenever the user types /retro-prompts or asks for a prompt retrospective, prompt-quality regression check, or LLM output audit.
disable-model-invocation: true
---

# /retro-prompts — LLM output retrospective

A guided session that reconstructs the data trail of one or more recent
resume generations, grades the output against the contracts the prompt itself
declares, correlates failures with recent prompt-file commits, asks the user
the questions only they can answer, then writes a retrospective doc with
prioritized recommendations.

## When to run

- After a prompt edit landed and you want a regression check
- Periodically (weekly?) to catch drift
- When a specific bad output prompted "why did the LLM do that?"

## Inputs you will need

- Project root contains `app.db` (SQLite), `services/llm/base.py` (prompts), `git`.
- The user is here and can answer 2–4 multiple-choice questions mid-flow.

## Step 1 — Pick the sample

Default: the 5 most recent rows. Show the list and let the user pick.

```bash
sqlite3 -header -column app.db "
  SELECT id, job_id, job_title, company_name,
         ROUND(match_score, 1) AS score,
         language,
         created_at
  FROM generated_resumes
  ORDER BY created_at DESC
  LIMIT 5;
"
```

Use AskUserQuestion to ask which row(s) to inspect. Options:
- "All 5 in parallel" (recommended for regression sweeps)
- "Just the latest"
- "Pick one by id"
- "Pick a custom range/date"

## Step 2 — Reconstruct the trail (per chosen row)

For each `resume_id`, pull every piece of the trail in parallel.

```bash
RESUME_ID=<id>
JOB_ID=<job_id from row>
CREATED_AT="<created_at from row>"
USER_ID=$(sqlite3 app.db "SELECT user_id FROM generated_resumes WHERE id=$RESUME_ID;")

# JD as the LLM saw it (prefer jd_version_id snapshot if present, else live jobs.original_text)
sqlite3 app.db "
  SELECT COALESCE(jv.original_text, j.original_text) AS jd_text
  FROM generated_resumes gr
  JOIN jobs j ON j.id = gr.job_id
  LEFT JOIN job_versions jv ON jv.id = gr.jd_version_id
  WHERE gr.id = $RESUME_ID;
"

# Output: the resume + analysis the LLM returned
sqlite3 app.db "SELECT resume_content, job_analysis, match_score FROM generated_resumes WHERE id=$RESUME_ID;"

# Profile snapshot — CURRENT state for this user (the row stored at gen-time is NOT preserved; flag this in findings)
sqlite3 -json app.db "SELECT * FROM users WHERE id=$USER_ID;"
sqlite3 -json app.db "SELECT * FROM work_experiences WHERE user_id=$USER_ID ORDER BY id;"
sqlite3 -json app.db "SELECT * FROM skills WHERE user_id=$USER_ID;"
sqlite3 -json app.db "SELECT * FROM education WHERE user_id=$USER_ID;"
sqlite3 -json app.db "SELECT * FROM projects WHERE user_id=$USER_ID;"
sqlite3 -json app.db "SELECT * FROM languages WHERE user_id=$USER_ID;"
```

Get the prompt **as it was at generation time**:

```bash
PROMPT_HASH=$(git log --before="$CREATED_AT" -1 --format=%H -- services/llm/base.py)
git show "$PROMPT_HASH:services/llm/base.py" > /tmp/prompt-at-$RESUME_ID.py
```

Note the hash and short commit subject so the report can quote it.

## Step 3 — Grade against the contracts

The prompt itself declares the contracts. Check each output against them.

**Hard-cap checks** (mechanical, no judgment):

```bash
python3 - <<'PY'
import json, sqlite3
db = sqlite3.connect("app.db")
row = db.execute("SELECT resume_content, job_analysis FROM generated_resumes WHERE id=?", (RESUME_ID,)).fetchone()
resume = json.loads(row[0]); analysis = json.loads(row[1]) if row[1] else {}

problems = []
summary = resume.get("summary", "")
if len(summary) > 350:
    problems.append(f"summary length {len(summary)} > 350")

for we in resume.get("work_experiences", []):
    d = we.get("description", "") or ""
    if len(d) > 350:
        problems.append(f"we[{we.get('id')}] description {len(d)} > 350")
    if not we.get("included", False):
        problems.append(f"we[{we.get('id')}] included=False (rule forbids this)")

# First-person / no-third-person check on summary
# Compare against the user's first/last name pulled in Step 2
# Flag if summary starts with the candidate's name or contains "{First} is/was/has"

# match_score plausibility: count matched vs unmatched in job_analysis
req = analysis.get("required_skills", [])
matched = sum(1 for s in req if s.get("matched"))
total = len(req) or 1
print(json.dumps({"matched_pct": matched/total, "score": resume.get("match_score"), "problems": problems}, indent=2))
PY
```

**Judgment checks** (need the JD + profile in view):
- Are `included=false` skills/education/projects actually irrelevant to the JD?
- Does the summary read as the candidate speaking?
- Are `match_reasons` per work experience grounded in the JD or hallucinated?

## Step 4 — Correlate with prompt churn

Look at every commit to the prompt file in the window covering the sample:

```bash
OLDEST=$(sqlite3 app.db "SELECT MIN(created_at) FROM generated_resumes WHERE id IN (<chosen_ids>);")
git log --follow --since="$OLDEST" --format="%h  %ad  %s" --date=short -- services/llm/base.py
git log --follow --since="$OLDEST" -p -- services/llm/base.py | head -300
```

For each grading failure, point at the commit that touched the relevant clause (e.g., a 350-char overflow after the cap clause was last edited is more interesting than one from before it).

If no recent prompt change explains the failure → flag as model drift, data-shape issue, or prompt has never enforced the rule strictly enough.

## Step 5 — Ask the user (use AskUserQuestion)

Pick the 2–3 questions that the grading actually surfaced. Phrase each as a real choice with concrete options. Examples:

- "Row 42's summary opens with '{First} {Last} is a ...'. Was this acceptable in the previous run too, or is this new?"
- "JD `original_text` for row 38 is 2.3k chars of HTML noise. Is your normal flow to clean before paste, or paste raw?"
- "`match_score=85` while 3/8 required skills unmatched. Is the score consistently too generous, or only on this row?"

Always include "I don't know / skip" as the last option.

## Step 6 — Recommend (only the axes with evidence)

Group recommendations into four buckets. Only include a bucket if Step 3/4/5 produced evidence for it.

**JD shape**
- Pre-clean (strip HTML, boilerplate, recruiter intro) before storing?
- Split `original_text` into title/company/body before feeding the prompt?
- Cap JD length passed to the LLM and log truncation?

**Master-data shape**
- Snapshot the profile at generation time (new column `profile_snapshot TEXT` on `generated_resumes`) so retros stop being lossy?
- Normalize skill names (canonical list) so `match_score` can be computed deterministically?
- Distinguish "skills the user wants to highlight" from "everything the user knows"?

**Output shape**
- Enforce length caps server-side post-LLM (truncate or reject + retry) instead of begging the prompt?
- Compute `match_score` outside the LLM from `job_analysis.required_skills[*].matched`?
- Validate first-person voice on `summary` server-side with a cheap regex check?

**Separation of concerns**
- Two LLM calls: (1) JD-analysis cached on `job_versions.id`, (2) profile-tailoring per resume?
- Move `LANGUAGE_INSTRUCTIONS` out of the prompt body into structured input?
- Move the "all work_experiences included" rule out of the prompt entirely — let the LLM omit and the server backfills missing ones with `included=true` defaults?

## Step 7 — Write the retro doc

Append to `methodology-improvement/retro-<YYYY-MM-DD>.md` (create if missing). Structure:

```markdown
# Prompt retro — <date>

## Sample
- Rows inspected: <ids>
- Prompt commit at generation time(s): <hashes + subjects>

## Findings (grouped)
### Length cap violations
- ...

### Voice / third-person leaks
- ...

### match_score plausibility
- ...

### Other
- ...

## Likely regression sources
- <commit-hash> "subject" — touched X clause; failures in rows Y, Z appeared after this commit.

## User-confirmed context
- <question 1> → <answer>
- <question 2> → <answer>

## Recommendations
### JD shape
### Master-data shape
### Output shape
### Separation of concerns

## Decisions / next actions
- [ ] ...
```

End with a one-screen summary printed to the user — file path + the top 3 recommendations.

## Anti-patterns (do not do)

- Do not edit prompts or code as part of the retro. Output is a doc + recommendations only.
- Do not assume the profile at generation time matches the current profile — always flag that no snapshot exists (unless/until a `profile_snapshot` column is added).
- Do not skip the git correlation step. "Is this a regression?" is the single highest-value question this skill can answer.
- Do not grade subjectively when a mechanical check works (length, included flags, score-vs-matched ratio).
