# minhs-website

A Claude Code skill for building websites from idea to launch: interview, competitor research, PRD, design direction, plan, then specialist agents on cost-matched models, with a pre-ship report before launch. Also covers anti-slop design and copy, motion, 3D, and a launch checklist with audit scripts.

## Install

```bash
git clone https://github.com/Vecnasurvivor/minhs-website ~/.claude/skills/minhs-website
```

Optional: copy the agents so the build workflow can hand off to them.

```bash
cp ~/.claude/skills/minhs-website/agents/*.md ~/.claude/agents/
```

Then ask Claude to build, audit or ship a website, or type `/minhs-website`.

## What's inside

- `SKILL.md` — entry point and mode picker
- `references/` — workflow, discovery, design, build, motion, 3D, launch checklist
- `agents/` — web-architect, web-builder, web-designer, web-copywriter, web-researcher, web-qa, web-security, web-polish
- `templates/` — CLAUDE.md, PRD, PLAN, LOG, RESEARCH files for a new project
- `scripts/` — `launch_audit.py`, `motion_audit.py`, `slop_scan.py`
- `examples/` — a good site and a "slop" site to test `slop_scan.py` against

```bash
python3 scripts/slop_scan.py examples/slop-site
```
