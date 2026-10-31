# .github/scripts/generate_content.py
#
# Generates the GitHub profile README:
#   1. Generative banner (topographic field + data graph) -> assets/banner.svg  (new every day)
#   2. AI insight of the day         -> README text (curated track, verified source link)
#   3. Animated career timeline      -> assets/timeline.svg
#
# IMPORTANT:
#   - the workflow must install:  pip install requests numpy matplotlib
#   - and commit the assets folder too:  git add README.md assets/

import html
import io
import json
import os
import random
import re
import textwrap
import time
from datetime import datetime, timezone
from urllib.parse import quote as url_quote, urlparse

import requests

# --- Configuration ---------------------------------------------------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
RETRY_DELAY = 3  # seconds

GITHUB_USER = "rickkk856"
REPO_NAME = "rickkk856"      # profile repo (same name as the user)
BRANCH = "main"
ASSETS_DIR = "assets"
INSIGHT_CACHE = os.path.join(ASSETS_DIR, "insight.json")
INSIGHT_LANGUAGE = "English"  # language of the daily insight (e.g. "Brazilian Portuguese")

NAME = "RICARDO RODRIGUES"
ROLE = "AI ENGINEER · COMPUTATIONAL DESIGN"
LOCATION = "SÃO PAULO, BR"

# --- Palette (style C: dark "tech-architecture") ---------------------------
BG = "#0b0f14"
GRID = "#1b2631"
LINE = "#8b98a5"
WALL = "#e6edf3"
ACCENT = "#00bfff"
MUTED = "#6e7b88"
SUBTEXT = "#9aa7b4"
FONT = "'JetBrains Mono','Fira Code','SF Mono',Consolas,'Courier New',monospace"

# --- Career timeline (edit freely; fill in "when" with years) --------------
TIMELINE = [
    {"when": "2011 – 2021", "title": "Architecture Design",
     "sub": "Architecture & Urbanism: construction techniques and technical projects"},
    {"when": "2020 – 2022", "title": "MSc in AI Applied to Design Process",
     "sub": "Generative models for floor plans; published at IJAC, ACADIA, eCAADe, CAADRIA, SIGraDi"},
    {"when": "2022 – 2026", "title": "BioTech & GeoSpatial Intelligence",
     "sub": "Computer vision, time-series analysis and GenAI for GeoSpatial Sciences"},
    {"when": "2026 – today", "title": "GenAI on Finance & Real Estate",
     "sub": "AI for finance and home-equity solutions"},
]

# --- Insight tracks (rotate by day of the year) ----------------------------
TRACKS = [
    ("GenAI × Real Estate",
     "Generative AI applied to real estate: valuation, document intelligence, property search, underwriting"),
    ("Computational Design",
     "Generative AI and computational design in architecture, urbanism and construction"),
    ("Fintech & Home Equity",
     "AI in fintech and home-equity / real-estate-backed credit, with emphasis on Brazil and Latin America"),
]

SYSTEM_PROMPT = (
    "You are an expert tech journalist specializing in artificial intelligence, computational "
    "architectural design and modern real estate technologies. Always search the web before "
    "answering. Report only facts supported by a source you actually found, preferably published "
    "within the last 60 days. Never invent URLs or sources. No greeting, no filler, no self-reference. "
    "Reply with ONE JSON object and nothing else (no markdown fences) with these keys: "
    '"headline" (max 90 characters), "summary" (max 280 characters, 1-2 sentences), '
    '"source_name", "source_url" (the exact article URL), '
    '"published" (YYYY-MM-DD, or empty string if unknown).'
)


# ===========================================================================
# 1. Generative banner: topographic field + data graph (matplotlib + numpy)
# ===========================================================================
BANNER_CSS = (
    ".flow{stroke-dasharray:7 11;animation:flow 6s linear infinite}"
    "@keyframes flow{to{stroke-dashoffset:-72}}"
    ".pulse{animation:pulse 3.2s ease-in-out infinite}"
    "@keyframes pulse{0%,100%{opacity:.2}50%{opacity:1}}"
    "@media (prefers-reduced-motion:reduce){.flow,.pulse{animation:none}}"
)

NODE_TAGS = [
    "AGENTS", "LLMs", "RAG", "GEOSPATIAL SCIENCES", "TIME-SERIES ANALYSIS", "AWS", "GCP",
    "GOOGLE EARTH ENGINE", "FORECASTING", "MACHINE LEARNING", "COMPUTER VISION",
    "GENERATIVE AI", "REMOTE SENSING", "OBSERVABILITY", "LARGE LANGUAGE MODELS", "PROMPT ENGINEERING",
    "DATA PIPELINES", "CLOUD COMPUTING"
]
MAX_LABELS = 9  # keywords shown per day (shuffled by the daily seed)


def generate_banner_svg(now):
    """Abstract 'terrain of ideas': isolines of a daily-seeded field with a data graph on top.

    Returns the SVG string, or None if numpy/matplotlib are not installed.
    """
    try:
        import numpy as np
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patheffects as pe
        from matplotlib.colors import LinearSegmentedColormap
        from matplotlib.patches import FancyBboxPatch, Rectangle
    except ImportError:
        print("⚠️ numpy/matplotlib not installed — skipping banner (keeping the previous one).")
        return None

    seed = int(now.strftime("%Y%m%d"))
    rng = np.random.default_rng(seed)
    W, H = 1200, 340
    matplotlib.rcParams["svg.hashsalt"] = str(seed)

    # --- Smooth random field (FFT low-pass) + a few "hills" for composition
    gx, gy = 320, 91
    noise = rng.standard_normal((gy, gx))
    fx, fy = np.fft.fftfreq(gx)[None, :], np.fft.fftfreq(gy)[:, None]
    lowpass = np.exp(-(fx ** 2 + fy ** 2) / (2 * 0.03 ** 2))
    field = np.real(np.fft.ifft2(np.fft.fft2(noise) * lowpass))
    field = (field - field.min()) / (field.max() - field.min())
    yy, xx = np.mgrid[0:gy, 0:gx]
    for _ in range(3):
        cx, cy = rng.uniform(0.06, 0.68) * gx, rng.uniform(0.2, 0.8) * gy
        s, a = rng.uniform(14, 28), rng.uniform(0.5, 1.0)
        field += a * np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * s * s)))
    field = (field - field.min()) / (field.max() - field.min())

    X = xx * (W / (gx - 1))
    Y = yy * (H / (gy - 1))
    levels = np.linspace(0.05, 0.95, 24)

    # Isolines (computed on a throwaway figure, drawn as plain lines so we control the SVG groups)
    tmp = plt.figure()
    cs = tmp.add_subplot().contour(X, Y, field, levels=levels)
    all_segs = [list(s) for s in cs.allsegs]
    plt.close(tmp)

    # --- Canvas
    fig = plt.figure(figsize=(12, 3.4), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), W, H, boxstyle="round,pad=0,rounding_size=14",
                                fc=BG, ec="none", zorder=0))
    gxs, gys = np.meshgrid(np.arange(20, W, 30), np.arange(20, H, 30))
    ax.scatter(gxs.ravel(), gys.ravel(), s=0.8, color="#2a3745", linewidths=0, zorder=1)

    cmap = LinearSegmentedColormap.from_list("blueprint", ["#0f2a3f", "#0a6c9c", ACCENT, "#bfeaff"])
    for i, segs in enumerate(all_segs):
        t = (levels[i] - levels[0]) / (levels[-1] - levels[0])
        major = i % 5 == 0
        for seg in segs:
            if len(seg) < 3:
                continue
            ax.plot(seg[:, 0], seg[:, 1], color=cmap(t), lw=1.2 if major else 0.55,
                    alpha=0.95 if major else 0.30 + 0.45 * t, solid_capstyle="round",
                    gid="flow" if major else None, zorder=2)

    # --- Data graph overlay
    pts = np.column_stack([rng.uniform(40, 800, 44), rng.uniform(34, H - 34, 44)])
    dist = np.linalg.norm(pts[:, None] - pts[None], axis=2)
    np.fill_diagonal(dist, np.inf)
    edges = set()
    for i in range(len(pts)):
        for j in np.argsort(dist[i])[:2]:
            if dist[i, j] < 190:
                edges.add(tuple(sorted((i, int(j)))))
    for i, j in edges:
        ax.plot([pts[i, 0], pts[j, 0]], [pts[i, 1], pts[j, 1]], color=ACCENT, lw=0.7, alpha=0.40, zorder=3)
    ax.scatter(pts[:, 0], pts[:, 1], s=9, color=WALL, linewidths=0, alpha=0.9, zorder=4)

    # Labeled nodes: résumé keywords, shuffled daily, placed without overlapping
    tags = [NODE_TAGS[int(i)] for i in rng.permutation(len(NODE_TAGS))]
    boxes, placed = [], []
    for k in (int(i) for i in rng.permutation(len(pts))):
        if len(placed) >= min(MAX_LABELS, len(tags)):
            break
        x, y = pts[k]
        tag = tags[len(placed)]
        box = (x - 8, y - 22, x + 11 + len(tag) * 6.4 + 8, y + 8)
        if box[2] > 840 or box[1] < 8:
            continue
        if any(not (box[2] < o[0] or box[0] > o[2] or box[3] < o[1] or box[1] > o[3]) for o in boxes):
            continue
        boxes.append(box)
        placed.append((x, y, tag))
    halo = [pe.withStroke(linewidth=3, foreground=BG)]
    for x, y, tag in placed:
        ax.plot([x], [y], "o", mfc="none", mec=ACCENT, ms=10, mew=1.2, gid="pulse", zorder=5)
        ax.text(x + 11, y - 9, tag, fontsize=7.5, family="monospace", color=ACCENT,
                path_effects=halo, zorder=6)

    # --- Title block
    bx, by, bw, bh = 860, 30, 310, 280
    ax.add_patch(Rectangle((bx, by), bw, bh, fc=BG, ec=LINE, lw=0.9, alpha=0.9, zorder=10))
    ax.text(bx + 18, by + 42, NAME, fontsize=16, weight="bold", family="monospace", color=WALL, zorder=11)
    ax.text(bx + 18, by + 66, ROLE, fontsize=7.2, family="monospace", color=ACCENT, zorder=11)
    ax.plot([bx, bx + bw], [by + 86, by + 86], color=LINE, lw=0.8, zorder=11)
    rows = [
        ("SHEET", "A-02 / GENERATIVE FIELD"),
        ("ISOLINES", str(len(levels))),
        ("NODES", str(len(pts))),
        ("DATE", now.strftime("%Y-%m-%d")),
        ("SEED", str(seed)),
        ("LOCATION", LOCATION),
    ]
    for n, (k, v) in enumerate(rows):
        ry = by + 118 + n * 31
        ax.text(bx + 18, ry, k, fontsize=7, family="monospace", color=MUTED, zorder=11)
        ax.text(bx + 105, ry, v, fontsize=7.8, family="monospace", color=WALL, zorder=11)

    buf = io.StringIO()
    fig.savefig(buf, format="svg", transparent=True, metadata={"Date": None})
    plt.close(fig)

    svg = buf.getvalue()
    svg = svg.replace('<g id="flow">', '<g class="flow">').replace('<g id="pulse">', '<g class="pulse">')
    svg = re.sub(r"(<svg[^>]*>)", lambda m: m.group(1) + f"<style>{BANNER_CSS}</style>", svg, count=1)
    return svg


# ===========================================================================
# 2. Career timeline (animated, step by step)
# ===========================================================================
def _kf(name, frames):
    """frames: list of (selector, declarations) -> @keyframes string."""
    return "@keyframes " + name + "{" + "".join(f"{sel}{{{decl}}}" for sel, decl in frames) + "}"


def generate_timeline_svg():
    W, H = 900, 440
    n = len(TIMELINE)
    x_first, x_last = 150, W - 150
    step = (x_last - x_first) / (n - 1) if n > 1 else 0
    ly = 225
    lx0, lx1 = 50, W - 50
    L = lx1 - lx0

    # Animation clock (seconds): one step every `gap` s, hold, fade, restart
    D, t0, gap, reveal = 22.0, 0.9, 2.4, 0.7
    hold_end, fade_end = 19.0, 20.4

    def pct(t):
        return f"{round(t / D * 100, 3)}%"

    def offset_at(x):  # dashoffset that shows the progress line up to x
        return round(L - (x - lx0), 1)

    css = [
        ".step,.node,.prog,.ring{animation-duration:%ss;animation-iteration-count:infinite}" % D,
        ".ring{opacity:0;transform-box:fill-box;transform-origin:center}",
        ".node{transform-box:fill-box;transform-origin:center}",
        ".prog{stroke-dasharray:%s %s}" % (L, L),
        "@media (prefers-reduced-motion:reduce){.step,.node,.prog,.ring{animation:none!important}}",
    ]
    body = []

    # Progress line keyframes
    pf = [("0%", f"stroke-dashoffset:{L};opacity:1")]
    prev_x = lx0
    for i in range(n):
        cx = x_first + i * step
        ts = t0 + i * gap
        dep = 0.1 if i == 0 else ts - 0.9
        pf.append((pct(dep), f"stroke-dashoffset:{offset_at(prev_x)}"))
        pf.append((pct(ts), f"stroke-dashoffset:{offset_at(cx)}"))
        prev_x = cx
    pf.append((pct(t0 + (n - 1) * gap + 1.8), "stroke-dashoffset:0"))
    pf.append((pct(hold_end), "stroke-dashoffset:0;opacity:1"))
    pf.append((pct(fade_end), "stroke-dashoffset:0;opacity:0"))
    pf.append((pct(fade_end + 0.05), f"stroke-dashoffset:{L};opacity:0"))
    pf.append(("100%", f"stroke-dashoffset:{L};opacity:0"))
    css.append(_kf("prog", pf))
    css.append(".prog{animation-name:prog;animation-timing-function:linear}")

    body.append(f'<rect width="{W}" height="{H}" rx="12" fill="{BG}"/>')
    body.append(f'<rect width="{W}" height="{H}" rx="12" fill="url(#grid)"/>')
    body.append(f'<text x="40" y="40" font-size="13" fill="{ACCENT}" letter-spacing="3">FROM SKETCH TO CODE</text>')
    body.append(f'<line x1="{lx0}" y1="{ly}" x2="{lx1}" y2="{ly}" stroke="{LINE}" stroke-width="2"/>')
    for tx in range(lx0, lx1 + 1, 20):
        body.append(f'<line x1="{tx}" y1="{ly - 4}" x2="{tx}" y2="{ly + 4}" stroke="{GRID}" stroke-width="1"/>')
    body.append(
        f'<line class="prog" x1="{lx0}" y1="{ly}" x2="{lx1}" y2="{ly}" stroke="{ACCENT}" stroke-width="3.5" '
        f'stroke-dashoffset="0"/>'
    )

    for i, item in enumerate(TIMELINE):
        cx = x_first + i * step
        ts = t0 + i * gap
        above = i % 2 == 0
        last = i == n - 1
        dy = -6 if above else 6

        # keyframes: text group (fade + slide), node (pop)
        css.append(_kf(f"k{i}", [
            (f"0%,{pct(ts - 0.01)}", f"opacity:0;transform:translateY({dy}px)"),
            (pct(ts + reveal), "opacity:1;transform:translateY(0)"),
            (pct(hold_end), "opacity:1;transform:translateY(0)"),
            (f"{pct(fade_end)},100%", "opacity:0;transform:translateY(0)"),
        ]))
        css.append(_kf(f"p{i}", [
            (f"0%,{pct(ts - 0.01)}", "opacity:0;transform:scale(.2)"),
            (pct(ts + 0.35), "opacity:1;transform:scale(1.4)"),
            (pct(ts + 0.7), "opacity:1;transform:scale(1)"),
            (pct(hold_end), "opacity:1;transform:scale(1)"),
            (f"{pct(fade_end)},100%", "opacity:0;transform:scale(1)"),
        ]))
        css.append(f".s{i}{{animation-name:k{i};animation-timing-function:ease-out}}")
        css.append(f".n{i}{{animation-name:p{i};animation-timing-function:ease-out}}")

        # node
        size = 26 if last else 20
        fill = ACCENT if last else BG
        body.append(
            f'<rect class="node n{i}" x="{cx - size / 2:.1f}" y="{ly - size / 2:.1f}" width="{size}" height="{size}" '
            f'fill="{fill}" stroke="{ACCENT}" stroke-width="2.5"/>'
        )

        # text block
        t_lines = textwrap.wrap(item["title"], 22)
        s_lines = textwrap.wrap(item.get("sub", ""), 34)
        block_h = len(t_lines) * 22 + 8 + len(s_lines) * 17
        if above:
            top = ly - 60 - block_h
            stem = (ly - 14, ly - 46)
            label_y = ly + 38
        else:
            top = ly + 60
            stem = (ly + 14, ly + 46)
            label_y = ly - 28

        g = [f'<g class="step s{i}">']
        g.append(f'<line x1="{cx:.1f}" y1="{stem[0]}" x2="{cx:.1f}" y2="{stem[1]}" stroke="{ACCENT}" stroke-width="1.5" stroke-dasharray="3 3"/>')
        label = item.get("when") or f"STEP {i + 1:02d}"
        g.append(f'<text x="{cx:.1f}" y="{label_y}" font-size="13" fill="{ACCENT}" text-anchor="middle" letter-spacing="2">{html.escape(label)}</text>')
        y = top + 16
        for line in t_lines:
            g.append(f'<text x="{cx:.1f}" y="{y}" font-size="18" font-weight="bold" fill="{WALL}" text-anchor="middle">{html.escape(line)}</text>')
            y += 22
        y += 2
        for line in s_lines:
            g.append(f'<text x="{cx:.1f}" y="{y + 6}" font-size="13" fill="{SUBTEXT}" text-anchor="middle">{html.escape(line)}</text>')
            y += 17
        if last:
            g.append(f'<circle class="ring" cx="{cx:.1f}" cy="{ly}" r="16" fill="none" stroke="{ACCENT}" stroke-width="2"/>')
        g.append("</g>")
        body.extend(g)

    # pulsing ring on the last (current) node, starts once it has appeared
    ts_last = t0 + (n - 1) * gap
    css.append(_kf("ring", [("0%", "opacity:.9;transform:scale(1)"), ("100%", "opacity:0;transform:scale(2.4)")]))
    css.append(f".ring{{animation:ring 2.2s ease-out infinite;animation-delay:{ts_last + reveal:.1f}s}}")

    head = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'font-family="{FONT}" role="img" aria-label="Animated career timeline">',
        "<defs>",
        '<pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">'
        f'<path d="M 20 0 L 0 0 0 20" fill="none" stroke="{GRID}" stroke-width="0.5"/></pattern>',
        "</defs>",
        "<style>" + "".join(css) + "</style>",
    ]
    return "\n".join(head + body + ["</svg>"])


# ===========================================================================
# 3. Insight of the day (curated track + verified source)
# ===========================================================================
def get_google_api_url(model_id):
    return f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent"


def build_generation_config(model_id):
    config = {"maxOutputTokens": 4096}
    if model_id.startswith("gemini-3"):
        config["thinkingConfig"] = {"thinkingLevel": "medium"}
    else:
        config["thinkingConfig"] = {"thinkingBudget": -1}
    return config


def call_google_ai_studio(prompt, model_id, model_name):
    """Returns (text, model_name, grounding_sources)."""
    headers = {"Content-Type": "application/json", "x-goog-api-key": GOOGLE_API_KEY}
    data = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "tools": [{"google_search": {}}],
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": build_generation_config(model_id),
    }
    print(f"Calling Google AI Studio for {model_name}...")
    response = requests.post(get_google_api_url(model_id), headers=headers, json=data, timeout=120)
    if response.status_code == 429:
        raise requests.exceptions.RequestException("Quota exceeded (429)")
    response.raise_for_status()
    body = response.json()

    if not body.get("candidates"):
        raise ValueError("No candidates returned")
    cand = body["candidates"][0]
    finish = cand.get("finishReason", "UNKNOWN")
    if finish in ("SAFETY", "RECITATION", "OTHER"):
        raise ValueError(f"Blocked due to: {finish}")
    if "content" not in cand or "parts" not in cand["content"]:
        raise ValueError("Malformed response")

    grounding = []
    for chunk in cand.get("groundingMetadata", {}).get("groundingChunks", []):
        web = chunk.get("web", {})
        if web.get("uri"):
            grounding.append({"title": web.get("title", ""), "url": web["uri"]})

    for part in cand["content"]["parts"]:
        if part.get("text", "").strip() and not part.get("thought"):
            return part["text"].strip(), model_name, grounding
    raise ValueError("No text found in parts")


def call_openrouter(prompt, model_id):
    """Returns (text, model_name, grounding_sources)."""
    key = os.getenv("OPEN_ROUTER_API_KEY")
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": f"https://github.com/{GITHUB_USER}",
        "X-Title": "GitHub Readme Updater",
    }
    data = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "tools": [{"type": "openrouter:web_search"}],
        "max_tokens": 2048,
    }
    print(f"Calling OpenRouter for model {model_id}...")
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=60)
    if response.status_code == 429:
        raise requests.exceptions.RequestException("OpenRouter rate-limited (429)")
    response.raise_for_status()
    res = response.json()

    choices = res.get("choices") or []
    if not choices:
        raise ValueError("Invalid response structure from OpenRouter")
    msg = choices[0].get("message", {})
    text = (msg.get("content") or "").strip()
    if not text:
        raise ValueError("Empty content from OpenRouter")

    grounding = []
    for ann in msg.get("annotations", []) or []:
        cit = ann.get("url_citation") or {}
        if cit.get("url"):
            grounding.append({"title": cit.get("title", ""), "url": cit["url"]})
    return text, f"OpenRouter ({res.get('model', model_id)})", grounding


def parse_insight_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object in response")
    data = json.loads(match.group(0))
    keys = ("headline", "summary", "source_name", "source_url", "published")
    insight = {k: str(data.get(k) or "").strip() for k in keys}
    if not insight["headline"] or not insight["summary"]:
        raise ValueError("Missing headline or summary")
    return insight


def url_is_alive(url):
    if not url.startswith(("http://", "https://")):
        return False
    try:
        r = requests.get(
            url, timeout=10, stream=True, allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"},
        )
        status = r.status_code
        r.close()
        # 403/429 = site blocks bots but the page exists; 404 etc. = likely hallucinated
        return status < 400 or status in (403, 429)
    except requests.RequestException:
        return False


def resolve_source(insight, grounding):
    """Prefers the model's cited URL; falls back to grounding sources. Only returns verified links."""
    candidates = [(insight["source_name"], insight["source_url"])]
    candidates += [(g["title"], g["url"]) for g in grounding]
    for name, url in candidates:
        if url and url_is_alive(url):
            return (name or urlparse(url).netloc), url
    return None, None


def build_strategies():
    return [
        {"type": "google", "model_id": "gemini-2.5-flash", "name": "Google Gemini 2.5 Flash"},
        {"type": "google", "model_id": "gemini-2.5-flash-lite", "name": "Google Gemini 2.5 Flash-Lite"},
        {"type": "google", "model_id": "gemini-3.5-flash", "name": "Google Gemini 3.5 Flash"},
        {"type": "google", "model_id": "gemini-3.1-flash-lite", "name": "Google Gemini 3.1 Flash-Lite"},
        {"type": "google", "model_id": "gemini-3.1-pro-preview", "name": "Google Gemini 3.1 Pro Preview"},
        {"type": "openrouter", "model_id": "google/gemini-2.5-flash", "name": "OpenRouter (Gemini 2.5 Flash)"},
        {"type": "openrouter", "model_id": "google/gemini-2.5-flash-lite", "name": "OpenRouter (Gemini 2.5 Flash-Lite)"},
        {"type": "openrouter", "model_id": "google/gemini-3.5-flash", "name": "OpenRouter (Gemini 3.5 Flash)"},
        {"type": "openrouter", "model_id": "google/gemini-3.1-flash-lite", "name": "OpenRouter (Gemini 3.1 Flash-Lite)"},
        {"type": "openrouter", "model_id": "google/gemini-3.1-pro-preview", "name": "OpenRouter (Gemini 3.1 Pro Preview)"},
        {"type": "openrouter", "model_id": "openrouter/free", "name": "OpenRouter Free Model Router"},
    ]


def get_insight(now):
    track_name, track_desc = TRACKS[now.timetuple().tm_yday % len(TRACKS)]
    prompt = (
        f"Today is {now:%Y-%m-%d}. Track: {track_name} — {track_desc}. "
        f"Find ONE recent, verifiable development, product launch, study or data point for this track. "
        f"Write the headline and summary in {INSIGHT_LANGUAGE}. Search the web first."
    )

    for s in build_strategies():
        try:
            if s["type"] == "google":
                if not GOOGLE_API_KEY:
                    print(f"Skipping {s['name']} (GOOGLE_API_KEY not set)")
                    continue
                text, model, grounding = call_google_ai_studio(prompt, s["model_id"], s["name"])
            else:
                if not os.getenv("OPEN_ROUTER_API_KEY"):
                    print(f"Skipping {s['name']} (OPEN_ROUTER_API_KEY not set)")
                    continue
                text, model, grounding = call_openrouter(prompt, s["model_id"])

            insight = parse_insight_json(text)
            name, url = resolve_source(insight, grounding)
            if not url:
                raise ValueError("No verifiable source link")

            insight.update({
                "source_name": name, "source_url": url, "track": track_name,
                "model": model, "generated": now.strftime("%Y-%m-%d"), "stale": False,
            })
            os.makedirs(ASSETS_DIR, exist_ok=True)
            with open(INSIGHT_CACHE, "w", encoding="utf-8") as f:
                json.dump(insight, f, ensure_ascii=False, indent=2)
            return insight

        except Exception as e:
            print(f"❌ Strategy {s['name']} failed: {e}")
            print(f"Waiting {RETRY_DELAY} seconds before trying next fallback...")
            time.sleep(RETRY_DELAY)

    # Everything failed: reuse the last good insight instead of a generic quote
    if os.path.exists(INSIGHT_CACHE):
        try:
            with open(INSIGHT_CACHE, encoding="utf-8") as f:
                cached = json.load(f)
            cached["stale"] = True
            print("All strategies failed. Reusing last cached insight.")
            return cached
        except (OSError, json.JSONDecodeError):
            pass

    print("All fallback options exhausted. Using static default.")
    return {
        "headline": "Generative AI keeps reshaping architecture and real estate",
        "summary": "From automated valuation to generative design, AI is moving from pilots to production.",
        "source_name": "", "source_url": "", "published": "", "track": "Generative AI",
        "model": "Static fallback", "generated": now.strftime("%Y-%m-%d"), "stale": True,
    }


def render_insight_html(ins):
    e = html.escape
    meta = []
    if ins.get("source_url"):
        meta.append(f'Source: <a href="{e(ins["source_url"], quote=True)}">{e(ins["source_name"] or "link")}</a>')
    if ins.get("published"):
        meta.append(e(ins["published"]))
    meta.append(f'via {e(ins["model"])}')
    meta.append(f'{"last good run" if ins.get("stale") else "updated"} {e(ins["generated"])}')
    return "\n".join([
        '<table width="100%">',
        "  <tr><td>",
        f'    <sub><b>INSIGHT OF THE DAY</b> · {e(ins["track"]).upper()}</sub><br/><br/>',
        f'    <b>{e(ins["headline"])}</b><br/>',
        f'    {e(ins["summary"])}<br/><br/>',
        f'    <sub>{" · ".join(meta)}</sub>',
        "  </td></tr>",
        "</table>",
    ])


# ===========================================================================
# README assembly
# ===========================================================================
STACK = [
    ("AI & ML", "tensorflow", ["TensorFlow • PyTorch", "Scikit-learn • OpenCV", "SciPy"]),
    ("GenAI & LLM", "openai", ["LangChain • Google ADK", "Amazon Bedrock • n8n", "Strands-Agents • Agno"]),
    ("Cloud & DevOps", "amazonaws", ["AWS • Lambda", "GCP • GitHub Actions", "Docker • CI/CD"]),
    ("Data Viz", "powerbi", ["PowerBi • Plotly", "Matplotlib • Seaborn", "Numpy • Pandas"]),
]

LINKS = [
    ("LinkedIn", "linkedin", "https://linkedin.com/in/rcrarq"),
    ("Behance", "behance", "https://www.behance.net/ricardorodrigu17"),
    ("YouTube", "youtube", "https://www.youtube.com/@ricardocesarrodrigues837"),
    ("ResearchGate", "researchgate", "https://www.researchgate.net/profile/Ricardo-Rodrigues-26"),
    ("Google_Scholar", "google-scholar", "https://scholar.google.com.br/citations?user=mVCXbNIAAAAJ"),
]


def badge(label, logo):
    return (
        f"https://img.shields.io/badge/{url_quote(label, safe='')}-0b0f14"
        f"?style=for-the-badge&logo={logo}&logoColor=00BFFF"
    )


def generate_profile_html(insight, now):
    stamp = now.strftime("%Y%m%d")  # cache-buster for GitHub's image proxy
    base = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{ASSETS_DIR}"
    banner_url = f"{base}/banner.svg?v={stamp}"
    timeline_url = f"{base}/timeline.svg?v={stamp}"

    parts = [
        '<div align="center">',
        f'<img width="100%" src="{banner_url}" alt="Generative topographic banner — {html.escape(NAME.title())}"/>',
        "<br/><br/>",
        render_insight_html(insight),
        "<br/>",
        f'<img width="100%" src="{timeline_url}" alt="Career timeline: from architecture to AI engineering"/>',
        "<br/><br/>",
        '<h3 align="center">🛠️ Tech Stack</h3>',
        '<table align="center">',
        "  <tr>",
    ]
    for label, logo, lines in STACK:
        sub = "<br/>".join(f"<b>{html.escape(l)}</b>" for l in lines)
        parts += [
            '    <td align="center" width="25%">',
            f'      <img src="{badge(label, logo)}"/>',
            f"      <br/><sub>{sub}</sub>",
            "    </td>",
        ]
    parts += ["  </tr>", "</table>", "<br/>", '<h3 align="center">🤝 Let\'s Connect</h3>', '<p align="center">']
    for label, logo, href in LINKS:
        parts.append(f'  <a href="{href}"><img src="{badge(label, logo)}"/></a>')
    parts += [
        "</p>",
        '<p align="center">',
        f'  <img src="https://komarev.com/ghpvc/?username={GITHUB_USER}&color=00BFFF&style=for-the-badge&label=Profile+Views" />',
        "</p>",
        "<sub>Banner generated from a daily seed · updated with GitHub Actions &amp; Google AI Studio</sub>",
        "</div>",
    ]
    return "\n".join(parts)


def update_readme(html_content):
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write("<!-- GENERATED_CONTENT_START -->\n<!-- GENERATED_CONTENT_END -->\n")

    with open(readme_path, "r", encoding="utf-8") as f:
        readme = f.read()

    start, end = "<!-- GENERATED_CONTENT_START -->", "<!-- GENERATED_CONTENT_END -->"
    block = f"{start}\n\n{html_content}\n\n{end}"

    if start in readme and end in readme:
        readme = readme.split(start)[0] + block + readme.split(end)[1]
    else:
        print("Warning: Markers not found. Appending content.")
        readme = f"{readme}\n\n{block}"

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme)
    print("README.md updated successfully!")


if __name__ == "__main__":
    print("🚀 Starting profile generation...")
    now = datetime.now(timezone.utc)
    os.makedirs(ASSETS_DIR, exist_ok=True)

    banner_svg = generate_banner_svg(now)
    if banner_svg:
        with open(os.path.join(ASSETS_DIR, "banner.svg"), "w", encoding="utf-8") as f:
            f.write(banner_svg)
    with open(os.path.join(ASSETS_DIR, "timeline.svg"), "w", encoding="utf-8") as f:
        f.write(generate_timeline_svg())
    print("🏛️ Banner and timeline generated")

    insight = get_insight(now)
    print(f"✅ Insight: {insight['headline']} ({insight['model']})")

    update_readme(generate_profile_html(insight, now))
    print("✨ Profile generation complete!")