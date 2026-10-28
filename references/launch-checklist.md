# Launch checklist

Run before a site goes live and after every big feature. Work top to bottom: security first, because a leak can't be undone.

1. Run `scripts/launch_audit.py <dir>` for the automatic checks.
2. Then go through every item below by hand.
3. Fix each one and record the file you changed.
4. Finish with a table: item · pass / fixed / needs Minh · file.

"Needs Minh" means it lives in a dashboard, DNS, a hosting console or a legal decision. Say exactly where to click. Never hide a failure.

---

## 1. Security

**Data and access**
- [ ] **RLS on every table** (Supabase/Postgres). Users only read and write their own rows. Tables created in raw SQL don't get RLS automatically. This should return no rows:
  `select tablename from pg_tables where schemaname='public' and not rowsecurity;`
- [ ] **Server-side permissions.** Check auth and ownership on the server for every request, never only in the UI. Every route that takes an id must confirm the caller owns that object (IDOR).
- [ ] **Protect admin routes.** Check the role on the server, in middleware and in the handler. Hiding the link isn't protection.
- [ ] **Parameterized SQL.** Never build queries with string concatenation or template strings. Use the ORM or `$1` placeholders.

**Secrets**
- [ ] **API secrets stay server-side.** No secret, service-role or private keys in client code, bundles, or `NEXT_PUBLIC_` / `VITE_` vars. Rotate any key that was ever shipped to the browser or committed.
- [ ] **`.env*` in `.gitignore`**, and never committed. Check `git log --all -- .env`. If it's in history, rotate the keys; deleting the file isn't enough. Commit a `.env.example` with names only.
- [ ] **No tokens in localStorage.** Use `HttpOnly; Secure; SameSite=Lax` cookies for sessions.
- [ ] **No sensitive data in logs**: passwords, tokens, card numbers, full emails, request bodies of auth routes. Redact before logging, client and server.

**Input and requests**
- [ ] **Validate form inputs on the server** with a schema (zod, valibot, pydantic). Client validation is only for UX.
- [ ] **Validate file uploads**: check type by magic bytes rather than extension, enforce a size limit, rename files, store them outside the web root or in a private bucket, and never execute or serve them inline as HTML/SVG from your domain.
- [ ] **Rate-limit requests** per IP and per user. Be strictest on login, signup, password reset, contact forms, and any AI or paid-API endpoint.
- [ ] **Spam protection on public forms**: honeypot field + rate limit, and Turnstile/hCaptcha if spam still gets through.
- [ ] **Block XSS.** Use no `dangerouslySetInnerHTML` / `v-html` / `innerHTML` with user data; sanitize with DOMPurify if you must render HTML. Set a Content-Security-Policy.
- [ ] **Tighten CORS.** Allow-list exact origins, never `*` with credentials, and only the methods/headers you use.
- [ ] **Verify webhook signatures** (Stripe, GitHub, etc.) against the raw body before trusting the payload. Reject replays using the timestamp.

**Accounts**
- [ ] **Hash passwords** with argon2id or bcrypt (cost ≥ 12). Never store plain text, MD5 or SHA-only hashes. Better still, use the auth provider.
- [ ] **Verify email addresses** before granting access or sending anything important.

**Production**
- [ ] **Debug off in production**: no `DEBUG=True`, no stack traces shown to users, no source maps exposed publicly unless intended, and dev tools/routes removed.
- [ ] **Force HTTPS**: redirect http → https and set the `Strict-Transport-Security` header.
- [ ] **Security headers**: CSP, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `frame-ancestors`.
- [ ] **Update dependencies**: `npm audit` / `pnpm audit` / `pip-audit`. Fix highs and criticals, and remove unused packages.
- [ ] **Claude Code security review**: run `/security-review` on the branch, and `/code-review` for correctness. Fix what they confirm.

## 2. SEO

- [ ] **Remove stray `noindex`** (meta robots or `X-Robots-Tag`) from pages that should rank. Staging leftovers are the classic cause.
- [ ] **Unique meta title (≤ 60 chars) and description (≤ 155 chars) on every page.**
- [ ] **Exactly one `<h1>` per page**, with headings in order (h1 → h2 → h3, no skipped levels).
- [ ] **Canonical tag** on every page, pointing at its own clean URL.
- [ ] **Clean URL slugs**: lowercase, hyphens, short, no IDs or query junk. Old URLs 301 to new ones.
- [ ] **Internal links** between related pages, with descriptive anchor text (not "click here").
- [ ] **Fix broken links**: no internal 404s and no dead external links.
- [ ] **`sitemap.xml`** listing all indexable URLs, and submitted in Search Console.
- [ ] **`robots.txt`** that allows the site, points to the sitemap, and blocks only admin/private paths.
- [ ] **Schema markup** (JSON-LD): Organization/LocalBusiness, plus Product, Article, FAQ or Breadcrumb as fits. Validate with Google's Rich Results Test.
- [ ] **Social preview**: `og:title`, `og:description`, `og:image` (1200×630), `twitter:card`.
- [ ] **Favicon** plus `apple-touch-icon`.
- [ ] **Custom 404 page** with navigation back. It must return a real 404 status.

For deeper SEO work (keywords, competitors, AI visibility), use the `minhs-seo` skill.

## 3. Performance

- [ ] **Core Web Vitals** pass on mobile: LCP < 2.5 s, INP < 200 ms, CLS < 0.1. Check PageSpeed Insights.
- [ ] **Compress images**: WebP/AVIF, sized to how they're displayed, `loading="lazy"` below the fold, `width`/`height` set to stop layout shift, and the hero image preloaded.
- [ ] **Page load speed**: defer non-critical JS, self-host or `font-display: swap` fonts, and cut third-party scripts.
- [ ] **Mobile friendly**: viewport meta, no horizontal scroll, tap targets ≥ 44 px, text ≥ 16 px. Test at 375 px wide.

## 4. Accessibility

- [ ] **Alt text** on every meaningful image. Decorative images get `alt=""`.
- [ ] **Colour contrast** ≥ 4.5:1 for body text and ≥ 3:1 for large text and UI parts.
- [ ] **Keyboard navigation**: everything reachable with Tab, a visible focus ring, no traps, and a skip-to-content link.
- [ ] **Form labels** tied to inputs, and error messages announced (not just shown in red).
- [ ] **Reduced motion** respected (see the motion guides).

## 5. Legal and trust

- [ ] **Privacy policy page**: what you collect, why, who you share it with, how long you keep it, and the user's rights (GDPR/CCPA).
- [ ] **Terms and conditions / TOS page.**
- [ ] **Refund policy** if you sell anything.
- [ ] **Cookie policy + consent banner**: no non-essential cookies or trackers before consent, with "Reject" as easy as "Accept" (EU).
- [ ] **Form consent**: an unticked checkbox for marketing emails, and a link to the privacy policy at signup.
- [ ] **Collect only what you need.** Drop fields you don't use, and avoid sensitive data (ID numbers, health, exact birth dates) unless it's required.
- [ ] **Audit analytics, tracking, third-party SDKs and external tools.** List each one: what it collects, whether it's in the privacy policy, and whether it waits for consent. Remove anything unused.
- [ ] **Set up analytics** (privacy-friendly where possible: Plausible, Umami, or GA4 behind consent) with key events tracked.
- [ ] **Verify licenses**: fonts, icons, images, illustrations, code and assets are owned, licensed or free for commercial use. Keep the proof. No trademarked names or logos you don't have rights to.
- [ ] **Business details visible**: legal name, contact email, and address/registration where the law requires it (an EU "Impressum").

**Honest selling**
- [ ] **No dark patterns**: no fake countdowns, pre-ticked add-ons, confirm-shaming, or cancel flows harder than signup.
- [ ] **No hidden fees.** The full price, including tax and shipping, is shown before checkout.
- [ ] **No fake reviews or testimonials.** Every one must be real and attributable.
- [ ] **No unsupported claims** ("#1", "guaranteed", medical/financial promises) without proof.

## 6. Conversion

- [ ] **One clear call to action** per page, visible without scrolling, with every other button visually secondary.
- [ ] **Form validation UX**: inline errors, input kept on error, a success state shown.
