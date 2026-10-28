# Agents and model routing

The lead (main session) plans, talks to the user and verifies. Agents do the scoped work. Pick the **cheapest model that can do the job well**.

| Agent | Model | Does | Never |
|---|---|---|---|
| `web-architect` | **opus** | Reviews PLAN.md and stack choices, untangles hard bugs, data model and auth design | Writes routine UI |
| `web-security` | **opus** | Security review of code and config (launch-checklist §1), auth/payments/webhooks | Skims. It must read the actual handlers |
| `web-researcher` | sonnet | Competitor and reference research → RESEARCH.md | Copies anyone's text or design |
| `web-designer` | sonnet | Design directions, tokens, layout, component styling | Picks defaults (see design.md) |
| `web-copywriter` | sonnet | Headlines, page copy, CTAs, microcopy, meta text | Invents claims, stats or reviews |
| `web-builder` | sonnet | Implements one PLAN task: pages, components, forms, API routes | Takes on tasks outside its brief |
| `web-qa` | sonnet | Browser testing, a11y, Lighthouse, audits, regression checks | Fixes code. It reports, the lead routes the fixes |
| `web-polish` | **haiku** | Mechanical work: alt text, meta tags, sitemap/robots, image compression, link fixes, renames, log/plan updates | Design or logic decisions |

**Routing rules**
- Security, auth, payments, data model, and anything where a mistake leaks data or money → **opus**.
- Writing, building, testing, researching → **sonnet** (the default).
- Repetitive, well-specified edits with no judgement call → **haiku**.
- If a haiku or sonnet task fails twice, re-run it one tier up and log it.
- The lead never hands off: talking to the user, approving gates, verifying done-checks.

## Installing the agents (once)

The agent files live in this skill's `agents/` folder, each with its `model:` pinned. Copy them into the user's agents folder (ask first: it adds 8 agents to every project):

```bash
cp ~/.claude/skills/minhs-website/agents/*.md ~/.claude/agents/
```

They load in the next session. Until then, or if the user declines, use the built-in `general-purpose` agent with the `model` parameter set from the table, and paste the role from `agents/<name>.md` at the top of the brief.

## Brief template (every handoff)

Agents start with no memory of this conversation. Give them exactly what they need, and no more.

```
Role: <agent name> for <project name>.
Read first: CLAUDE.md, docs/PRD.md §<relevant>, docs/PLAN.md task <id>.
Task <id>: <one sentence>.
Files you may touch: <paths>. Don't touch anything else.
Done when: <command or observable result>.
Constraints: <design tokens / stack rules / "no new dependencies">.
When finished: append one line to docs/LOG.md and reply with what changed, the files touched,
and the done-check output. If blocked, stop and say why. Don't guess.
```

## Parallelism

Tasks that touch different files and don't need each other's output can run at the same time (e.g. copywriter on copy while builder scaffolds the layout). Two agents never edit the same file at once. The researcher and QA are read-only, so they can always run in parallel.

## Token discipline

- Point agents at file paths and sections, not whole documents.
- Ask for short replies: the result, files and check output, not a narrative.
- One task per agent run. Don't chain whole phases into one brief.
- Don't re-read the full PRD every task. CLAUDE.md carries the summary.
