#!/usr/bin/env python3
"""slop_scan: find the tells of AI-generated websites in HTML, CSS, JSX/TSX, Vue, Svelte and Astro files.

Pattern-based and deterministic. It flags the tells; it cannot judge taste, and a clean score does
not make a design good. Only scan code you own or have permission to review.

  slop_scan.py PATH [PATH ...] [--json] [--fail-under N] [--list-rules]
"""
import argparse, colorsys, json, os, re, sys

EXTS = {".html", ".htm", ".css", ".scss", ".jsx", ".tsx", ".js", ".ts", ".vue", ".svelte", ".astro"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".nuxt", "vendor", "coverage", "__pycache__", ".venv"}
MAX_BYTES = 1_000_000
WEIGHT = {"high": 10, "medium": 5, "low": 2}

# ---- rule catalogue (id -> severity, title, fix) ------------------------------------------------
RULES = {
    "purple-gradient": ("high", "Purple / indigo gradient", "Take colour from the brand or product, not from the default AI palette. Use one flat accent, or a gradient between two related brand hues."),
    "gradient-text": ("high", "Gradient-filled headline text", "Emphasise with weight, size or a flat colour. Gradient text is the most recognisable AI-landing-page tell."),
    "default-font-stack": ("medium", "Only default / overused fonts", "Choose a typeface with character for headings and pair it with a calm text face. Self-host or load it deliberately."),
    "emoji-icons": ("medium", "Emoji used as icons", "Draw icons from one consistent set (or author SVG) with the same stroke and size. Or drop the icons."),
    "feature-card-grid": ("medium", "Three identical feature cards", "Vary scale and layout by importance. Lead with the one thing that matters; do not give every point equal weight."),
    "cliche-copy": ("medium", "Cliche marketing copy", "Say what the product does, for whom, in plain words. Replace slogans with a specific fact or number you can prove."),
    "glassmorphism-overuse": ("medium", "Glassmorphism on many surfaces", "Use blur for one specific job (a sticky nav, a modal scrim), not as decoration on every card."),
    "colored-glow": ("medium", "Coloured glow shadows", "Use a real shadow with an offset and a soft blur in a neutral tone, or none."),
    "placeholder-content": ("high", "Placeholder content shipped", "Replace lorem ipsum, John Doe and stock placeholder images with real content and real photos."),
    "fake-social-proof": ("medium", "Unverified social-proof numbers", "Keep a number only if it is real and you can point to its source. Otherwise show a real quote with a name."),
    "rounded-everything": ("low", "Large radius on everything", "Pick a radius scale of two or three values and keep sharp corners where they help hierarchy."),
    "centered-everything": ("low", "Everything centre-aligned", "Left-align body text and use alignment to build hierarchy; centre only short headings."),
    "default-cta-pair": ("low", "Default 'Get Started / Learn More' pair", "Name the action in the user's words: 'Start a free audit', 'See pricing'."),
    "animate-everything": ("low", "Animation on every element", "Pick one authored motion moment; leave the rest still."),
    "missing-basics": ("low", "Missing page basics", "Add a <title>, a viewport meta tag and alt text on images."),
}

def rule_list():
    return [(k, *v) for k, v in RULES.items()]

# ---- helpers ------------------------------------------------------------------------------------
def line_of(text, pos):
    return text.count("\n", 0, pos) + 1

def snippet(text, pos, width=90):
    start = text.rfind("\n", 0, pos) + 1
    end = text.find("\n", pos)
    end = len(text) if end == -1 else end
    s = text[start:end].strip()
    return s if len(s) <= width else s[:width - 1] + "…"

def parse_color(tok):
    """Return (hue 0-360, saturation 0-1, lightness 0-1) or None."""
    tok = tok.strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6})", tok)
    if m:
        h = m.group(1)
        if len(h) == 3: h = "".join(c * 2 for c in h)
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    else:
        m = re.fullmatch(r"rgba?\(\s*(\d+)[ ,]+(\d+)[ ,]+(\d+)", tok)
        if m:
            r, g, b = (int(m.group(i)) / 255 for i in (1, 2, 3))
        else:
            m = re.fullmatch(r"hsla?\(\s*([\d.]+)(?:deg)?[ ,]+([\d.]+)%[ ,]+([\d.]+)%", tok)
            if m:
                return float(m.group(1)) % 360, float(m.group(2)) / 100, float(m.group(3)) / 100
            named = {"purple": (275, 1, .25), "indigo": (275, 1, .25), "violet": (270, .76, .72), "blueviolet": (271, .76, .53),
                     "mediumpurple": (260, .6, .65), "rebeccapurple": (270, .5, .4), "fuchsia": (300, 1, .5), "magenta": (300, 1, .5)}
            return named.get(tok)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360, s, l

COLOR_TOKEN = re.compile(r"#[0-9a-fA-F]{3,6}\b|rgba?\([^)]*\)|hsla?\([^)]*\)|\b(?:purple|indigo|violet|blueviolet|mediumpurple|rebeccapurple|fuchsia|magenta)\b", re.I)

def is_purple(col):
    if not col: return False
    h, s, l = col
    return 245 <= h <= 320 and s >= 0.35 and 0.12 <= l <= 0.85

# ---- rules (each yields (rule_id, pos, message)) -------------------------------------------------
def r_purple_gradient(text, ext):
    for m in re.finditer(r"(?:linear|radial|conic)-gradient\(((?:[^()]|\([^()]*\))*)\)", text, re.I):
        cols = [parse_color(x.group(0)) for x in COLOR_TOKEN.finditer(m.group(1))]
        if any(is_purple(c) for c in cols):
            yield "purple-gradient", m.start(), "CSS gradient uses purple/indigo/violet"
    for m in re.finditer(r'class(?:Name)?\s*=\s*["\'{`]([^"\'`]*)', text):
        cls = m.group(1)
        if re.search(r"\bbg-gradient-to-", cls) and re.search(r"\b(?:from|via|to)-(?:purple|violet|indigo|fuchsia)-\d{2,3}", cls):
            yield "purple-gradient", m.start(), "Tailwind gradient uses purple/indigo/violet"

def r_gradient_text(text, ext):
    for m in re.finditer(r"background-clip\s*:\s*text|-webkit-background-clip\s*:\s*text|\bbg-clip-text\b", text, re.I):
        ctx = text[max(0, m.start() - 300): m.end() + 300]
        if re.search(r"gradient|text-transparent|-webkit-text-fill-color\s*:\s*transparent|color\s*:\s*transparent", ctx, re.I):
            yield "gradient-text", m.start(), "Headline text filled with a gradient"

GENERIC_FONTS = {"inter", "roboto", "arial", "helvetica", "helvetica neue", "system-ui", "-apple-system", "blinkmacsystemfont",
                 "segoe ui", "open sans", "sans-serif", "ui-sans-serif", "poppins", "space grotesk", "dm sans", "plus jakarta sans",
                 "outfit", "geist", "montserrat", "lato", "nunito", "sf pro display", "sf pro text"}
def r_default_fonts(text, ext):
    fams = []
    for m in re.finditer(r"font-family\s*:\s*([^;}\n]+)", text, re.I):
        for f in m.group(1).split(","):
            f = f.strip().strip("'\"").lower()
            if f and not f.startswith("var("): fams.append((f, m.start()))
    for m in re.finditer(r"fonts\.googleapis\.com/css2?\?family=([^\"'&>\s]+)", text):
        for f in re.split(r"[|&]", m.group(1)):
            f = f.split(":")[0].replace("+", " ").lower()
            if f: fams.append((f, m.start()))
    for m in re.finditer(r"\bfont-(?:sans)\b", text):
        fams.append(("sans-serif", m.start()))
    if fams and all(f in GENERIC_FONTS for f, _ in fams):
        yield "default-font-stack", fams[0][1], "Fonts used: " + ", ".join(sorted({f for f, _ in fams}))

EMOJI = r"[\U0001F300-\U0001FAFF\u2728\u26A1\u2705\u274C\u2B50\u2764\u2600-\u26FF]"
def r_emoji_icons(text, ext):
    hits = list(re.finditer(r"<(?:h[1-6]|li|strong|div|span|p)\b[^>]*>\s*" + EMOJI + r"\uFE0F?", text))
    hits += list(re.finditer(r'class\s*=\s*["\'][^"\']*icon[^"\']*["\'][^>]*>\s*' + EMOJI, text))
    if len(hits) >= 2:
        yield "emoji-icons", hits[0].start(), f"{len(hits)} emoji used as icons/bullets"

def r_card_grid(text, ext):
    grid = re.search(r"(?:^|[\s:\"'])(?:[a-z]+:)?grid-cols-3\b|repeat\(\s*3\s*,\s*(?:minmax\([^)]*\)|1fr)", text)
    cards = re.findall(r'class(?:Name)?\s*=\s*["\'{`][^"\'`]*\b(?:card|feature|feature-card)\b', text, re.I)
    if grid and len(cards) >= 3:
        yield "feature-card-grid", grid.start(), f"3-column grid with {len(cards)} card-style items"

CLICHES = [r"revolutioni[sz]e", r"unleash", r"supercharge", r"elevate your", r"seamless(?:ly)?", r"cutting[- ]edge",
           r"game[- ]chang(?:er|ing)", r"next[- ]gen(?:eration)?", r"empower(?:s|ing)?\b", r"to the next level",
           r"in today'?s fast[- ]paced", r"all[- ]in[- ]one platform", r"unlock the power", r"streamline your", r"world[- ]class",
           r"state[- ]of[- ]the[- ]art", r"harness the power", r"your one[- ]stop", r"take your .{1,30} to new heights"]
def r_cliche(text, ext):
    body = re.sub(r"<(script|style)\b.*?</\1>", " ", text, flags=re.S | re.I)
    found = {}
    for pat in CLICHES:
        for m in re.finditer(pat, body, re.I):
            found.setdefault(m.group(0).lower(), m.start())
    if found:
        first = min(found.values())
        yield "cliche-copy", first, "Phrases: " + ", ".join(sorted(found)[:6])

def r_glass(text, ext):
    hits = list(re.finditer(r"backdrop-blur|backdrop-filter\s*:\s*blur|-webkit-backdrop-filter", text))
    if len(hits) >= 3:
        yield "glassmorphism-overuse", hits[0].start(), f"{len(hits)} backdrop-blur surfaces"

def r_glow(text, ext):
    for m in re.finditer(r"shadow-(?:purple|violet|indigo|fuchsia|pink|blue|cyan|sky)-\d{2,3}(?:/\d+)?|box-shadow\s*:[^;}]*\b0\s+0\s+(\d{2,3})px", text):
        blur = m.group(1)
        if blur is None or int(blur) >= 20:
            yield "colored-glow", m.start(), "Zero-offset coloured glow"
            return

PLACEHOLDERS = r"lorem ipsum|\bjohn doe\b|\bjane (?:doe|smith)\b|placehold\.(?:co|it)|via\.placeholder\.com|picsum\.photos|i\.pravatar\.cc|randomuser\.me/api/portraits|source\.unsplash\.com/random|your company name|\bacme inc\b"
def r_placeholder(text, ext):
    m = re.search(PLACEHOLDERS, text, re.I)
    if m: yield "placeholder-content", m.start(), "Found: " + m.group(0)

PROOF = [r"trusted by (?:thousands|millions|over \d|\d)", r"\b\d{1,3}(?:,\d{3})+\+?\s+(?:happy\s+)?(?:customers|users|teams|companies|developers|businesses)",
         r"\b\d+k\+?\s+(?:happy\s+)?(?:customers|users|teams|companies|developers)", r"\b99\.9\s*%\s*(?:uptime)?", r"★{5}|⭐{3,}"]
def r_proof(text, ext):
    body = re.sub(r"<(script|style)\b.*?</\1>", " ", text, flags=re.S | re.I)
    hits = [m for p in PROOF for m in re.finditer(p, body, re.I)]
    if hits:
        yield "fake-social-proof", min(h.start() for h in hits), "Claims: " + ", ".join(sorted({h.group(0).strip() for h in hits})[:4])

def r_rounded(text, ext):
    n = len(re.findall(r"\brounded-(?:2xl|3xl|full)\b", text)) + len(re.findall(r"border-radius\s*:\s*(?:2[4-9]|[3-9]\d)px", text))
    if n >= 6:
        yield "rounded-everything", 0, f"{n} large-radius uses"

def r_centered(text, ext):
    c = len(re.findall(r"\btext-center\b|text-align\s*:\s*center", text))
    l = len(re.findall(r"\btext-left\b|text-align\s*:\s*(?:left|start)", text))
    if c >= 8 and l == 0:
        yield "centered-everything", 0, f"{c} centred blocks, no left-aligned text"

def r_cta(text, ext):
    if re.search(r">\s*Get Started\s*<", text, re.I) and re.search(r">\s*Learn More\s*<", text, re.I):
        m = re.search(r">\s*Get Started\s*<", text, re.I)
        yield "default-cta-pair", m.start(), "'Get Started' + 'Learn More'"

def r_animate(text, ext):
    n = len(re.findall(r"data-aos\s*=", text)) + len(re.findall(r"\banimate-(?:bounce|pulse|ping|fade[\w-]*)\b", text))
    if n >= 6:
        yield "animate-everything", 0, f"{n} animated elements"

def r_basics(text, ext):
    if ext in (".html", ".htm") and re.search(r"<html\b", text, re.I):
        if not re.search(r"<title>\s*\S", text, re.I): yield "missing-basics", 0, "No <title>"
        if not re.search(r'<meta[^>]+name=["\']viewport', text, re.I): yield "missing-basics", 0, "No viewport meta tag"
        for m in re.finditer(r"<img\b(?![^>]*\balt\s*=)[^>]*>", text, re.I):
            yield "missing-basics", m.start(), "<img> without alt"; break

CHECKS = [r_purple_gradient, r_gradient_text, r_default_fonts, r_emoji_icons, r_card_grid, r_cliche, r_glass, r_glow,
          r_placeholder, r_proof, r_rounded, r_centered, r_cta, r_animate, r_basics]

# ---- driver -------------------------------------------------------------------------------------
def iter_files(paths):
    for p in paths:
        if os.path.isfile(p):
            yield p
        for root, dirs, files in os.walk(p):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for f in sorted(files):
                if os.path.splitext(f)[1].lower() in EXTS and ".min." not in f:
                    yield os.path.join(root, f)

def scan(paths):
    findings, nfiles = [], 0
    for fp in iter_files(paths):
        try:
            if os.path.getsize(fp) > MAX_BYTES: continue
            text = open(fp, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        nfiles += 1
        ext = os.path.splitext(fp)[1].lower()
        for check in CHECKS:
            for rid, pos, msg in check(text, ext):
                if "slop-scan:ignore" in snippet(text, pos, 400): continue
                sev, title, fix = RULES[rid]
                findings.append({"rule": rid, "severity": sev, "title": title, "file": fp, "line": line_of(text, pos), "detail": msg, "snippet": snippet(text, pos), "fix": fix})
    return findings, nfiles

def score(findings):
    per = {}
    for f in findings: per[f["rule"]] = per.get(f["rule"], 0) + 1
    penalty = sum(WEIGHT[RULES[r][0]] * min(n, 3) for r, n in per.items())
    return max(0, 100 - penalty)

def verdict(s):
    return "clean: no strong AI-slop tells found" if s >= 90 else "some tells: worth a pass" if s >= 70 else "reads as AI-generated"

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*"); ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-under", type=int, default=0, help="exit 1 when the score is below N")
    ap.add_argument("--list-rules", action="store_true")
    a = ap.parse_args(argv)
    if a.list_rules:
        for rid, sev, title, _ in rule_list(): print(f"{rid:24} {sev:7} {title}")
        return 0
    if not a.paths: ap.error("give at least one path")
    findings, nfiles = scan(a.paths)
    s = score(findings)
    if a.json:
        print(json.dumps({"tool": "slop_scan", "files": nfiles, "score": s, "verdict": verdict(s), "findings": findings}, indent=2))
    else:
        print(f"slop_scan: {nfiles} files, {len(findings)} findings, score {s}/100 ({verdict(s)})")
        by = {}
        for f in findings: by.setdefault(f["rule"], []).append(f)
        for rid, fs in sorted(by.items(), key=lambda kv: -WEIGHT[RULES[kv[0]][0]]):
            sev, title, fix = RULES[rid]
            print(f"\n[{sev.upper()}] {title}  ({rid}, {len(fs)}x)")
            for f in fs[:3]: print(f"  {f['file']}:{f['line']}  {f['detail']}")
            print(f"  fix: {fix}")
    return 1 if s < a.fail_under else 0

if __name__ == "__main__":
    sys.exit(main())
