#!/usr/bin/env python3
"""Pre-launch scan: security, SEO, legal-page and a11y basics. Usage: launch_audit.py <dir> [--selftest]

Static checks only. It flags likely problems; anything it can't see (dashboards, RLS, headers
set by the host) is still on the manual checklist in references/launch-checklist.md.
"""
import os
import re
import subprocess
import sys

SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "out", ".vercel", "coverage", "venv", ".venv", "__pycache__"}
CODE_EXT = {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".astro", ".py", ".rb", ".php", ".go", ".html"}

# (regex, message) checked on every code file
CODE_RULES = [
    (r"sk_live_[0-9a-zA-Z]{10,}|sk-ant-[\w-]{20,}|sk-proj-[\w-]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY", "hardcoded secret key"),
    (r"(?:NEXT_PUBLIC|VITE|PUBLIC|REACT_APP|EXPO_PUBLIC)_\w*(?:SECRET|SERVICE_ROLE|PRIVATE|PASSWORD)\w*", "secret exposed through a public env var"),
    (r"localStorage\.setItem\(\s*['\"][^'\"]*(?:token|jwt|session|auth)", "token stored in localStorage; use HttpOnly cookie"),
    (r"dangerouslySetInnerHTML|v-html=|\.innerHTML\s*=(?!\s*['\"]\s*['\"])", "raw HTML sink: check no user/URL input reaches it, else sanitize (XSS)"),
    (r"(?:origin\s*:\s*['\"]\*['\"]|Access-Control-Allow-Origin['\"]?\s*[,:]\s*['\"]\*)", "CORS allows any origin"),
    (r"^\s*DEBUG\s*=\s*True", "DEBUG=True"),
    (r"(?:query|execute|raw|sql)\s*\(\s*`[^`]*\b(?:SELECT|INSERT|UPDATE|DELETE)\b[^`]*\$\{", "SQL built with template string; use parameters"),
    (r"(?:query|execute)\s*\(\s*['\"][^'\"]*\b(?:SELECT|INSERT|UPDATE|DELETE)\b[^'\"]*['\"]\s*(?:\+|%\s)", "SQL built by concatenation; use parameters"),
    (r"(?:md5|sha1)\s*\([^)]*pass", "weak password hash; use argon2id/bcrypt"),
    (r"console\.log\([^)]*(?:password|token|secret|authorization)", "sensitive value logged"),
]
CODE_RULES = [(re.compile(p, re.I | re.M), m) for p, m in CODE_RULES]
CODE_RULES[5] = (re.compile(r"^\s*DEBUG\s*=\s*True", re.M), "DEBUG=True")  # case-sensitive

IMG_NO_ALT = re.compile(r"<img\b(?![^>]*\balt=)[^>]*>", re.I)
H1 = re.compile(r"<h1[\s>]", re.I)


def line_of(text, idx):
    return text.count("\n", 0, idx) + 1


def scan_code(rel, text):
    out = []
    for rx, msg in CODE_RULES:
        for m in rx.finditer(text):
            out.append((rel, line_of(text, m.start()), msg))
    if rel.endswith((".html", ".jsx", ".tsx", ".vue", ".svelte", ".astro")):
        for m in IMG_NO_ALT.finditer(text):
            out.append((rel, line_of(text, m.start()), "<img> without alt"))
        for m in re.finditer(r"""(?:href|src)=["']http://(?!localhost|127\.0\.0\.1)""", text):
            out.append((rel, line_of(text, m.start()), "http:// link; use https"))
    return out


def scan_html_page(rel, text):
    """Full-document checks, only for files that are whole HTML pages."""
    if not re.search(r"<html[\s>]", text, re.I):
        return []
    out, low = [], text.lower()
    need = {
        "<title": "missing <title>",
        'name="description"': "missing meta description",
        'rel="canonical"': "missing canonical tag",
        'property="og:image"': "missing og:image (social preview)",
        'name="viewport"': "missing viewport meta (mobile)",
    }
    for needle, msg in need.items():
        if needle not in low.replace("'", '"'):
            out.append((rel, 0, msg))
    n = len(H1.findall(text))
    if n != 1:
        out.append((rel, 0, f"{n} <h1> tags; need exactly one"))
    if re.search(r"<meta[^>]+noindex", text, re.I):
        out.append((rel, 0, "noindex meta present; remove if this page should rank"))
    return out


def git_tracked_env(root):
    try:
        r = subprocess.run(["git", "-C", root, "ls-files"], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [f for f in r.stdout.splitlines()
            if re.search(r"(^|/)\.env(\.|$)", f) and not f.endswith((".example", ".sample", ".template"))]


def find_gitignore(root):
    """Nearest .gitignore from root up to the repo top (a monorepo app often has none of its own)."""
    d = os.path.abspath(root)
    while True:
        gi = os.path.join(d, ".gitignore")
        if os.path.exists(gi):
            return gi
        if os.path.exists(os.path.join(d, ".git")) or os.path.dirname(d) == d:
            return None
        d = os.path.dirname(d)


def is_bundle(rel):
    """Framework/vendor output: findings there are the framework's, not ours."""
    r = rel.replace("\\", "/")
    return "/_astro/" in "/" + r or "/_next/" in "/" + r or "/chunks/" in r or r.endswith(".min.js")


def audit(root):
    issues, names, blob = [], set(), []
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for name in files:
            p = os.path.join(d, name)
            rel = os.path.relpath(p, root)
            names.add(rel.lower().replace("\\", "/"))
            if name in ("package.json", "astro.config.mjs", "astro.config.ts", "next.config.js", "next.config.mjs", "next.config.ts"):
                blob.append(open(p, encoding="utf-8", errors="ignore").read())
            if is_bundle(rel):
                continue
            if os.path.splitext(name)[1].lower() in CODE_EXT and os.path.getsize(p) < 2_000_000:
                try:
                    text = open(p, encoding="utf-8").read()
                except UnicodeDecodeError:
                    continue
                issues += scan_code(rel, text)
                if re.search(r"rel=[\"'](?:shortcut )?icon[\"']", text):
                    names.add("favicon.declared")
                if name.endswith(".html"):
                    issues += scan_html_page(rel, text)

    config = "\n".join(blob)
    if re.search(r"@astrojs/sitemap|next-sitemap|sitemap\(", config):
        names.add("sitemap-generated.xml")

    gi = find_gitignore(root)
    if not gi or not re.search(r"^\s*\.env", open(gi).read(), re.M):
        issues.append((".gitignore", 0, ".env not ignored; add `.env*` and `!.env.example`"))
    for f in git_tracked_env(root):
        issues.append((f, 0, "env file committed to git; remove and ROTATE its keys"))

    def has(*patterns):
        return any(re.search(p, n) for n in names for p in patterns)

    expected = [
        ((r"(^|/)robots\.txt$", r"(^|/)robots\.(ts|js)$"), "no robots.txt (file or generator)"),
        ((r"(^|/)sitemap[\w-]*\.xml$", r"(^|/)sitemap\.(ts|js)$", r"next-sitemap"), "no sitemap.xml (file or generator)"),
        ((r"(^|/)404\.\w+$", r"not-found\.\w+$", r"\[\.\.\.\w*\]"), "no custom 404 page"),
        ((r"favicon\.\w+$", r"(^|/)icon\.(png|svg|ico)$", r"^favicon\.declared$"), "no favicon"),
        ((r"privacy",), "no privacy policy page"),
        ((r"terms", r"(^|/)tos\b", r"conditions"), "no terms / TOS page"),
        ((r"cookie",), "no cookie policy / consent found"),
    ]
    for pats, msg in expected:
        if not has(*pats):
            issues.append(("(project)", 0, msg))
    return issues


def selftest():
    bad = ("const k='sk_live_abcdefghijklmnop';\nlocalStorage.setItem('authToken', t)\n"
           "db.query(`SELECT * FROM u WHERE id=${id}`)\n<div dangerouslySetInnerHTML={x}/>\n"
           "cors({ origin: '*' })\nconsole.log('token', token)\n<img src=\"a.png\">")
    msgs = {m for _, _, m in scan_code("a.jsx", bad)}
    assert is_bundle("dist/_astro/x.js") and not is_bundle("src/pages/a.astro")
    for want in ("hardcoded secret key", "token stored in localStorage; use HttpOnly cookie",
                 "SQL built with template string; use parameters", "raw HTML sink: check no user/URL input reaches it, else sanitize (XSS)",
                 "CORS allows any origin", "sensitive value logged", "<img> without alt"):
        assert want in msgs, (want, msgs)
    good = "db.query('SELECT * FROM u WHERE id=$1', [id])\n<img src=\"a.png\" alt=\"\">\nel.innerHTML = ''"
    assert scan_code("b.jsx", good) == [], scan_code("b.jsx", good)
    page = ('<html><head><title>T</title><meta name="description" content="d"><link rel="canonical" href="/">'
            '<meta property="og:image" content="x"><meta name="viewport" content="w"></head><body><h1>A</h1></body></html>')
    assert scan_html_page("i.html", page) == []
    assert len(scan_html_page("i.html", page.replace("<h1>A</h1>", ""))) == 1
    print("selftest ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    found = audit(root)
    for path, line, msg in found:
        print(f"{path}:{line}  {msg}" if line else f"{path}  {msg}")
    print(f"\n{len(found)} issue(s). Now do the manual items in references/launch-checklist.md." if found
          else "No automatic issues. Now do the manual items in references/launch-checklist.md.")
    sys.exit(1 if found else 0)
