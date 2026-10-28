# Discovery and research

## 1. Interview (lead, before any design or code)

**Ask with the `AskUserQuestion` popup, never as a wall of text.** Each popup holds at most 4 questions with 2–4 options each. The user can always pick "Other" and type. Put the recommended option first, marked "(Recommended)".

- **Round 1 (always)**: what the site is, the one visitor action, the pages, the vibe.
- **Round 2 (only what round 1 left open)**: must-have features, existing content, hosting, success metric.
- Never more than 2 rounds. Everything else gets a sensible default, written into the PRD as an assumption the user can correct at the PRD gate.
- Skip any question the user already answered in their own words.
- After each round, reply with one line on what you understood.

The full question bank is below. Pick from it; don't ask it all.

**The business**
1. What is it, in one sentence, and who pays you?
2. Who exactly is the visitor? (age, job, what they're worried about, device)
3. What's the **one** action a visitor should take? (book, buy, sign up, call, apply)
4. What makes you different from the obvious alternative? Real reasons only.

**The site**
5. Which pages? [Home, About, Services/Product, Pricing, Contact, Privacy, Terms]
6. Must-have features? (booking, payments, blog/CMS, login, search, multi-language, forms)
7. What content exists already: copy, photos, logo, brand colours, testimonials? What's missing?
8. Sites you love, and sites you hate? Name what you like about each (layout, mood, a detail).

**Constraints**
9. Domain, hosting, and existing stack or accounts? [Vercel + a new repo]
10. Who edits content after launch, and how technical are they?
11. Budget for paid services (CMS, email, booking tool, analytics)? [free tiers]
12. Deadline, and what does "launched" mean to you?
13. Legal context: country, do you sell, do you collect personal data?

**Success**
14. How will you know it worked in 3 months? (leads per week, sales, signups)

Turn the answers into PRD §1–3. Anything still unknown becomes an "Open question" in the PRD. Don't fill gaps with guesses.

## 2. Competitor research (web-researcher)

Brief: the PRD's business, audience and region. Find **5–8** sites:
- 3–5 direct competitors (same offer, same market)
- 1–2 best-in-class sites from adjacent markets (to raise the bar)
- 1 that the user named as a love or hate reference

For each one, record:

| Field | Note |
|---|---|
| URL + one line on who they are | |
| Hero promise (paraphrased) and main CTA | What do they lead with? |
| Page structure | Sections in order |
| Pricing / offer visibility | Shown? Hidden? How framed? |
| Trust signals | Reviews, logos, guarantees, credentials |
| Design | Mood, type, colour, one memorable detail |
| Speed / mobile | PageSpeed mobile score if quick, plus obvious issues |
| Weakness | Where they lose a visitor |

Then write a synthesis (max 15 bullets):
- **Table stakes**: what every competitor has, which we need too.
- **Gaps**: what nobody does well, which is our opening.
- **Clichés to avoid**: what everyone does that makes them look the same.
- **Positioning angle**: one sentence on how we stand apart.

Rules: paraphrase, never copy text, images or code. Note the source URL for every claim. Use the browser for live pages. Stay under ~15 minutes.

If the `minhs-seo` skill is available, add a keyword snapshot: the top 10 search terms competitors rank for.
