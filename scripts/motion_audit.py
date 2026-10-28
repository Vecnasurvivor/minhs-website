#!/usr/bin/env python3
"""Scan a web project for motion/3D problems. Usage: motion_audit.py <dir> [--selftest]"""
import json
import os
import re
import sys

SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "out", ".vercel", "coverage"}
CODE_EXT = {".css", ".scss", ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".html", ".astro"}
HEAVY = {".glb": 3_000_000, ".gltf": 3_000_000, ".riv": 500_000, ".lottie": 300_000}
LOTTIE_JSON_MAX = 150_000

# Layout properties animated/transitioned — cause reflow every frame.
LAYOUT_PROPS = r"(?:top|left|right|bottom|width|height|margin(?:-\w+)?|padding(?:-\w+)?)"
CSS_TRANSITION = re.compile(rf"transition(?:-property)?\s*:[^;{{}}]*\b{LAYOUT_PROPS}\b", re.I)
KEYFRAME_BLOCK = re.compile(r"@keyframes\s+[\w-]+\s*\{((?:[^{}]*\{[^{}]*\})*)[^{}]*\}", re.I)
KEYFRAME_LAYOUT = re.compile(rf"(?<![\w-]){LAYOUT_PROPS}\s*:", re.I)
JS_ANIM_LAYOUT = re.compile(rf"(?:animate|to|from|fromTo|tl\.add)\s*\([^)]*\b{LAYOUT_PROPS}\s*:", re.I | re.S)
MOTION_SIGNS = re.compile(r"@keyframes|transition\s*:|\banimate\(|from ['\"](?:animejs|motion|framer-motion|gsap|@react-spring|aos|vanta|zdog|@lottiefiles|@rive-app|@splinetool)", re.I)
REDUCED = re.compile(r"prefers-reduced-motion|useReducedMotion|reducedMotion", re.I)
EAGER_3D = re.compile(r"^\s*import\s+[^;]*from\s+['\"](three|@react-three/fiber|@splinetool/react-spline|aframe|vanta[^'\"]*)['\"]", re.M)
LIBS = {
    "anime/gsap timelines": ["animejs", "gsap"],
    "react motion": ["motion", "framer-motion", "@react-spring/web", "react-spring"],
    "scroll reveal": ["aos", "scrollreveal", "sal.js"],
    "lottie": ["lottie-web", "lottie-react", "@lottiefiles/dotlottie-react", "@lottiefiles/dotlottie-web", "react-lottie"],
}


def scan_text(path, text):
    issues = []
    for m in CSS_TRANSITION.finditer(text):
        issues.append((path, line_of(text, m.start()), "transition on a layout property; use transform/opacity"))
    for kb in KEYFRAME_BLOCK.finditer(text):
        if KEYFRAME_LAYOUT.search(kb.group(1)):
            issues.append((path, line_of(text, kb.start()), "@keyframes animates a layout property; use transform"))
    if path.endswith((".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte")):
        for m in JS_ANIM_LAYOUT.finditer(text):
            issues.append((path, line_of(text, m.start()), "JS animation of a layout property; use x/y/scale"))
        for m in EAGER_3D.finditer(text):
            issues.append((path, line_of(text, m.start()), f"'{m.group(1)}' imported eagerly; lazy-load 3D (dynamic import)"))
    return issues


def line_of(text, idx):
    return text.count("\n", 0, idx) + 1


def is_lottie_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            head = f.read(400)
        return '"v"' in head and '"layers"' in head or ('"fr"' in head and '"ip"' in head)
    except (OSError, UnicodeDecodeError):
        return False


def audit(root):
    issues, has_motion, has_reduced = [], False, False
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for name in files:
            p = os.path.join(d, name)
            rel = os.path.relpath(p, root)
            ext = os.path.splitext(name)[1].lower()
            size = os.path.getsize(p)
            if ext in HEAVY and size > HEAVY[ext]:
                issues.append((rel, 0, f"{size/1e6:.1f} MB {ext}; over budget {HEAVY[ext]/1e6:.1f} MB, compress it"))
            if ext == ".json" and size > LOTTIE_JSON_MAX and is_lottie_json(p):
                issues.append((rel, 0, f"{size/1e3:.0f} KB Lottie JSON; convert to .lottie"))
            if ext in CODE_EXT and size < 2_000_000:
                try:
                    text = open(p, encoding="utf-8").read()
                except UnicodeDecodeError:
                    continue
                has_motion |= bool(MOTION_SIGNS.search(text))
                has_reduced |= bool(REDUCED.search(text))
                issues += scan_text(rel, text)
    if has_motion and not has_reduced:
        issues.append(("(project)", 0, "motion found but no prefers-reduced-motion handling anywhere"))
    pkg = os.path.join(root, "package.json")
    if os.path.exists(pkg):
        deps = {}
        try:
            data = json.load(open(pkg))
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        except (ValueError, OSError):
            pass
        for job, names in LIBS.items():
            found = [n for n in names if n in deps]
            if len(found) > 1:
                issues.append(("package.json", 0, f"{len(found)} libraries for {job}: {', '.join(found)}; keep one"))
    return issues


def selftest():
    bad = "a{transition: width .3s} @keyframes x{from{left:0}to{left:9px}} b{transition: transform .2s}"
    msgs = [m for _, _, m in scan_text("t.css", bad)]
    assert len(msgs) == 2, msgs
    ok = "@keyframes y{from{transform:none}to{opacity:1}} c{transition: opacity .2s}"
    assert scan_text("t.css", ok) == [], scan_text("t.css", ok)
    js = "import * as THREE from 'three';\nanimate(el, { left: 10 })"
    assert len(scan_text("t.js", js)) == 2
    assert scan_text("t.js", "const S = lazy(() => import('@splinetool/react-spline'))") == []
    print("selftest ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    found = audit(root)
    for path, line, msg in found:
        print(f"{path}:{line}  {msg}" if line else f"{path}  {msg}")
    print(f"\n{len(found)} issue(s)" if found else "No motion issues found.")
    sys.exit(1 if found else 0)
