# <project name>

<one sentence: what this site is and for whom>

## Commands
- Install: `...`
- Dev: `...`
- Build: `...`
- Test: `...`
- Audit: `python3 ~/.claude/skills/minhs-website/scripts/launch_audit.py . && python3 ~/.claude/skills/minhs-website/scripts/motion_audit.py .`

## Stack
- Framework: · Styling: · Hosting: · Forms/email: · CMS: · Analytics:

## Design (approved direction: <name>)
- Fonts: display ... / body ...
- Colours: --bg ... --fg ... --accent ... --muted ...
- Radius / spacing scale:
- Signature detail:
- Never: <defaults this project rejects>

## Conventions
- Components in `src/components`, one per file.
- No new dependency without a line in docs/LOG.md saying why.
- Secrets only in `.env` (server). `.env.example` lists the names.
- Every change: append to docs/LOG.md. Every finished task: tick docs/PLAN.md.

## Docs
- docs/PRD.md (source of truth) · docs/PLAN.md (tasks) · docs/LOG.md (history) · docs/RESEARCH.md
- Workflow and agents: the `minhs-website` skill (references/workflow.md, references/agents.md)
