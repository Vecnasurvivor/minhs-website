---
name: minhs-website
description: "Minh's all-in-one website skill, from idea to shipped site. Build mode runs an agentic workflow \u2014 interview the user, research competitors, write a PRD and get approval, pick a design direction, plan, then hand tasks to specialist agents on cost-matched models (Opus for security and architecture, Sonnet for building, design, copy and QA, Haiku for mechanical fixes), keeping CLAUDE.md, PRD, PLAN and LOG files, with a pre-ship report before launch. Also covers anti-slop design and copy, stack choice, integrations, deploy, motion and animation (scroll, timelines, springs, Lottie, Rive, Magic UI, React Bits), 3D/VR/AR (Zdog, Vanta, Spline, A-Frame, three.js, model-viewer, Blender/Substance assets), and a launch checklist (security, SEO, performance, accessibility, legal pages) with audit scripts. Use when building, redesigning, planning, auditing, animating or shipping any website or landing page."
---

# minhs-website

## Which mode

- **New site, rebuild, or "build me a website"** → **Build mode**: read `references/workflow.md` and follow it phase by phase. It uses `agents.md`, `discovery.md`, `design.md`, `build.md` and the `templates/`. Never skip its ⛔ gates: the PRD needs approval before building, and the pre-ship report needs approval before launch.
- **One change to an existing site** → read the project's `CLAUDE.md` / `docs/PLAN.md` if present, use the matching guide below, and append to `docs/LOG.md`.
- **"Audit / check / ready to launch?"** → `references/launch-checklist.md` + both scripts.

## Guides

| Need | Read |
|---|---|
| The full idea → launch process, gates, project files | `references/workflow.md` |
| Which agent and which model for which job; handoff brief | `references/agents.md` |
| Interview questions, competitor research method | `references/discovery.md` |
| Design directions, tokens, anti-slop rules, UI rules, copy | `references/design.md` |
| Stack choice, structure, integrations, testing, deploy | `references/build.md` |
| Going live: security, SEO, speed, a11y, legal | `references/launch-checklist.md` |
| Scroll reveals, scroll-driven effects, sticky sections | `references/scroll.md` |
| Timelines, staggers, SVG drawing/morphing, counters | `references/timelines.md` |
| React springs, drag, layout and exit animation | `references/springs-react.md` |
| Lottie / dotLottie / Rive designer files | `references/vector.md` |
| Ready-made animated components (Magic UI, React Bits) | `references/components.md` |
| Decorative depth: tilt, animated backgrounds, Zdog | `references/3d-decorative.md` |
| Real 3D: model-viewer, Spline, A-Frame/WebXR, r3f | `references/3d-scenes.md` |
| Blender / Substance → optimized glTF | `references/3d-assets.md` |
| Minh's own collected tricks | `references/notes.md` (skim it every time, and prefer it when a trick fits) |

## Motion ladder (stop at the first rung that works)

1. **CSS**: transitions, `@keyframes`, scroll-driven animations, View Transitions.
2. **Web Animations API** (`el.animate()`).
3. **One library** per job: Anime.js (timelines/SVG), Motion (React), dotLottie/Rive (designer files).
4. **3D** only when depth is the point.

Never install two libraries for the same job. Check `package.json` first.

## Non-negotiables (every mode)

- Ask the user when unsure. Never invent content, stats, reviews or logos: placeholders are marked `[NEEDS: …]` and listed in the pre-ship report.
- Animate `transform`/`opacity` only. Respect `prefers-reduced-motion`. Lazy-load 3D and big media, with a static fallback.
- Secrets stay server-side, permissions are checked on the server, and inputs are validated on the server.
- Lighthouse mobile ≥ 90, WCAG AA contrast, works at 375 px, keyboard usable.
- Nothing ships without the pre-ship report and the user's yes.

## Tools

```bash
python3 ~/.claude/skills/minhs-website/scripts/launch_audit.py .   # security/SEO/legal-page/a11y static scan
python3 ~/.claude/skills/minhs-website/scripts/motion_audit.py .   # jank, reduced motion, heavy 3D/Lottie, duplicate libs
cp ~/.claude/skills/minhs-website/agents/*.md ~/.claude/agents/     # install the 8 web-* agents (ask the user first)
```

Both scripts exit with 1 when they find issues, and `--selftest` checks the scanner itself.
