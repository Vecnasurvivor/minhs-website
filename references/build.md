# Build: stack, structure, integrations, deploy

## Pick the stack (simplest that meets the PRD)

| Site | Stack |
|---|---|
| 1–5 pages, no editing needed | Plain HTML/CSS (+ a little JS), or **Astro** |
| Content site, blog, marketing, docs | **Astro** (+ Markdown/MDX content collections, or a headless CMS) |
| App features: login, dashboards, user data, payments | **Next.js** (App Router) + Supabase or another Postgres |
| Shop | Shopify (hosted or headless). Don't build a cart from scratch |
| Client wants to edit everything visually themselves | Framer / Webflow. Say so honestly; don't force code on them |

Styling: Tailwind v4 or plain CSS with custom properties (the design tokens). Pick one, not both styles mixed. TypeScript for anything beyond static pages.

Before adding a dependency, ask: does the platform or an installed package already do this?

## Structure

```
src/
  pages/ or app/       routes
  components/          one component per file; ui/ for primitives
  content/             markdown / CMS data
  lib/                 server helpers (db, email, auth): never imported by client code
  styles/tokens.css    design tokens from CLAUDE.md
public/                favicon, og image, robots.txt (or generated)
docs/                  PRD, PLAN, LOG, RESEARCH
.env.example           names only
```

## Integrations (defaults, swap if the PRD says otherwise)

| Need | Default | Notes |
|---|---|---|
| Contact form | Server route + Resend/Postmark email, or Formspree for static sites | Server validation, honeypot, rate limit |
| Booking | Cal.com embed | Don't build calendars |
| Payments | Stripe Checkout / Payment Links | Verify the webhook signature, and fulfil orders on the webhook, not the redirect |
| Auth + DB | Supabase (RLS on) or Clerk + Postgres | Server-side checks on every route |
| CMS | Content collections (dev edits), Sanity/Decap/Keystatic (client edits) | Match the PRD's "who edits" answer |
| Newsletter | Provider form (Buttondown, Kit, Mailchimp) | Double opt-in, unticked consent box |
| Analytics | Plausible/Umami (no banner needed in many cases) or GA4 behind consent | Track the PRD's one action as the key event |
| Search | Pagefind (static) | |
| Images | Framework image component (`astro:assets`, `next/image`) | AVIF/WebP, sized |
| i18n | Framework routing (`/en/`, `/de/`) + `hreflang` | Only if the PRD needs it |

## Quality while building

- Semantic HTML first: `header/nav/main/footer`, real buttons and links, one h1.
- Mobile first, fluid type and spacing from tokens.
- Every page has its title, description, canonical and OG tags from a shared SEO component.
- Every async UI has loading, empty, error and success states.
- No secrets in client code. Server-only modules live in `lib/`, and use `import 'server-only'` in Next.
- Commit after each passing task, with a message that references the task id (`T2.1: hero section`).

## Testing

- Build passes (`npm run build`) with no type errors.
- Smoke tests with **Playwright** for the critical path (home loads, main CTA works, form submits). Keep it to 3–6 tests, not a suite.
- Lighthouse CI or PageSpeed on the preview URL: aim for ≥ 90 mobile on every category.
- The audit scripts: `launch_audit.py` and `motion_audit.py`.

## Deploy

- **Vercel** (Next/Astro) or Netlify/Cloudflare Pages (static). Connect the repo, so every push to a branch gets a preview URL and `main` is production.
- Set env vars in the host dashboard (production and preview separately). Never commit them.
- Custom domain: add it in the host, set DNS (apex A/ALIAS + `www` CNAME), choose `www` or the bare domain and redirect the other, and make sure HTTPS is on.
- After deploying: smoke-test the live URL, submit the sitemap to Search Console, test the forms on production, and check analytics receives events.
- Keep a rollback ready (the previous deployment can be promoted).

## After launch (offer it in the pre-ship report)

Uptime monitor, error tracking (Sentry), monthly dependency updates, a quarterly content and SEO review with `minhs-seo`, and a backup of the CMS/DB.
