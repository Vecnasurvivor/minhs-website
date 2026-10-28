# Build mode: idea → shipped website

Use this whenever someone wants a new website or a big rebuild. The main session is the **lead**: it talks to the user, owns the files below, and hands work to agents (`agents.md`). It never skips a gate.

## Project files (create these first, before anything else)

Copy from `templates/` into the project and fill them in as you go:

| File | Purpose | Who writes |
|---|---|---|
| `CLAUDE.md` | How to run, build and test; stack; conventions; links to the docs below. Under 150 lines. | Lead |
| `docs/PRD.md` | What we're building and why. The source of truth. | Lead, approved by user |
| `docs/RESEARCH.md` | Competitors and what to steal or avoid | web-researcher |
| `docs/PLAN.md` | Phased task checklist, each task with an owner agent, model and done-check | Lead, reviewed by web-architect |
| `docs/LOG.md` | Append-only diary: every decision, delegation, result, blocker | Everyone appends; never rewrite history |

**State lives in files, not memory.** A fresh session, or a fresh agent, must be able to continue from `CLAUDE.md` + `PLAN.md` + `LOG.md` alone.

Log format, one line per event:

```
2026-10-28 14:02 | lead | decision | Chose Astro over Next: content site, no auth needed
2026-10-28 14:10 | web-builder(sonnet) | done | T2.1 hero section — check passed (npm run build)
```

## Phases and gates

`⛔ GATE` means stop and wait for the user's answer. Never assume yes.

### 0. Setup
**First look for what already exists**: the business's notes, an existing repo or site, and a live domain (search the disk for the name, read its CLAUDE.md, notes and log). If a site is already live, stop and ask with a popup: improve or audit it, build something separate (a new vertical, a different venture), or rebuild. Never build a second site that competes with a live one.

Then create the project folder and the 5 files above. If the project already has its own CLAUDE.md, log or plan files, use and extend those rather than creating duplicates. Log "project started".

### 1. Discover ⛔ GATE
Interview the user with `discovery.md` §1, using **`AskUserQuestion` popups**: at most 2 rounds of up to 4 questions each, with defaults for everything else. Never send a text questionnaire. Don't design or code anything yet.

The goal is what *they* actually want, not what a generic site has. Push back on vague answers: "modern and clean" is not a direction.

### 2. Research
Hand off to **web-researcher** (sonnet) with `discovery.md` §2. Output: `docs/RESEARCH.md` covering 5–8 competitors or references, with patterns to borrow and clichés to avoid. Spend ≤ 15 minutes on it, not a thesis.

### 3. PRD ⛔ GATE
The lead writes `docs/PRD.md` from the interview + research. Show the user a short summary: goal, audience, pages, key features, non-goals, success metric, open questions. Ask them to approve or edit. **Nothing gets built until the PRD is approved.** Log the approval with the user's words.

### 4. Design direction ⛔ GATE
Hand off to **web-designer** (sonnet) with `design.md`. They propose **2–3 distinct directions** (name, mood, type pairing, palette, one layout idea, one signature detail). The user picks one, or mixes them. Write the chosen tokens into `CLAUDE.md` under "Design".

### 5. Plan
The lead writes `docs/PLAN.md`:
- Phases as **vertical slices** (a page or feature working end to end), not layers ("all CSS, then all JS").
- Each task fits in one agent run, and has an **owner agent + model**, **files**, and a **done-check** (a command or an observable result).
- The last phase of every plan is: security review → QA → launch checklist → pre-ship report.

Hand the plan to **web-architect** (opus) for a one-pass review: risks, missing tasks, wrong stack choices. Apply the fixes, then log.

Show the user the phase list (not every task) in one message. Ask only if something changed from the PRD.

### 6. Build loop
Repeat until every task is checked:
1. Pick the next unchecked task whose dependencies are done.
2. Delegate it to its owner agent with the brief template in `agents.md`. Independent tasks can run in parallel.
3. When the agent returns: run the done-check yourself, because an agent's "done" isn't proof.
4. Pass → tick it in `PLAN.md` and log it. Fail → send it back once with the error. If it fails twice, log a blocker and ask the user.
5. At the end of each phase, tell the user in 2–3 lines what now works and what's next.

Scope creep: if the user asks for something new mid-build, add it to `PLAN.md` as a new task (or to the PRD if it's a new feature), log it, and keep going.

### 7. Review
- **web-security** (opus): `launch-checklist.md` §1 plus `/security-review`.
- **web-qa** (sonnet): runs the site in a browser and checks every page at 375 px and 1440 px, keyboard only, forms, the 404 page, plus Lighthouse/PageSpeed, `scripts/launch_audit.py` and `scripts/motion_audit.py`.
- **web-polish** (haiku): fixes mechanical findings (alt text, meta, sitemap, image compression, broken links).
- The lead fixes or delegates real findings, then re-runs the audits.

### 8. Pre-ship report ⛔ GATE
Before deploying, or before calling it done, send the user:
- What was built (pages and features vs the PRD; flag anything cut or changed)
- Audit results: security, launch_audit, Lighthouse scores, a11y
- What needs them (DNS, env vars, dashboards, legal text review, real content and photos)
- Known limits and suggested next steps

Ship only on an explicit yes. Then log "shipped" with the URL.

## Anti-slop rules for the lead

- Don't invent features, testimonials, stats, logos or team members. Use clearly marked placeholders and list them in the pre-ship report.
- Don't pad with generic sections ("Why choose us", three icon cards, a fake FAQ) unless the PRD asks for them.
- Every section must earn its place: the PRD names who it's for and what it makes them do.
- Prefer one sharp page over five thin ones.
- If you're unsure what the user wants, ask. One question costs less than a rebuild.

## Small requests

For a single change ("add a contact form", "fix the hero"), skip the gates: read `CLAUDE.md` + `PLAN.md` if they exist, do the work, and append to `LOG.md`.
