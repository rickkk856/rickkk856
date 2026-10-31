# .github/scripts/generate_content.py
#
# Generates the GitHub profile README:
#   1. Generative floor-plan banner  -> assets/banner.svg   (new plan every day, seeded by the date)
#   2. AI insight of the day         -> README text (curated track, verified source link)
#   3. Career timeline               -> assets/timeline.svg
#
# IMPORTANT: your workflow must commit the assets folder too, e.g.
#   git add README.md assets/

import html
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
FONT = "'JetBrains Mono','Fira Code','SF Mono',Consolas,'Courier New',monospace"

# --- Career timeline (edit freely; fill in "when" with years) --------------
TIMELINE = [
    {"when": "", "title": "Architecture", "sub": "Space, design and the built environment"},
    {"when": "", "title": "Computational Design", "sub": "Parametric and generative workflows"},
    {"when": "", "title": "MSc · Architectural Design with AI", "sub": "Where AI meets architecture"},
    {"when": "", "title": "AI Models in Production", "sub": "5+ years building with AI"},
    {"when": "", "title": "Senior AI Engineer", "sub": "Fintech, home equity and real estate-backed credit"},
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
# 1. Generative floor-plan banner
# ===========================================================================
def bsp_split(rect, depth, rng, leaves, splits, min_w=110, min_h=80, max_depth=4):
    """Recursively subdivides a rectangle into rooms (binary space partition)."""
    x, y, w, h = rect
    can_v = w >= 2 * min_w
    can_h = h >= 2 * min_h
    if depth >= max_depth or not (can_v or can_h) or (depth >= 2 and rng.random() < 0.22):
        leaves.append(rect)
        return
    if can_v and can_h:
        vertical = (w / h) * rng.uniform(0.8, 1.25) > 1
    else:
        vertical = can_v
    ratio = rng.uniform(0.38, 0.62)
    if vertical:
        sx = x + w * ratio
        splits.append(("v", sx, y, y + h))
        bsp_split((x, y, sx - x, h), depth + 1, rng, leaves, splits, min_w, min_h, max_depth)
        bsp_split((sx, y, x + w - sx, h), depth + 1, rng, leaves, splits, min_w, min_h, max_depth)
    else:
        sy = y + h * ratio
        splits.append(("h", sy, x, x + w))
        bsp_split((x, y, w, sy - y), depth + 1, rng, leaves, splits, min_w, min_h, max_depth)
        bsp_split((x, sy, w, y + h - sy), depth + 1, rng, leaves, splits, min_w, min_h, max_depth)


def _wall_with_door(orient, pos, a, b, rng):
    """Returns SVG for one interior wall with a door gap and a swing arc."""
    dw = 26
    lo, hi = a + 12, b - 12 - dw
    d = rng.uniform(lo, hi) if hi > lo else a + (b - a - dw) / 2
    s = rng.choice([-1, 1])
    wall = f'stroke="{LINE}" stroke-width="1.6"'
    door = f'stroke="{ACCENT}" stroke-width="1" fill="none"'
    if orient == "v":
        return (
            f'<line x1="{pos:.1f}" y1="{a:.1f}" x2="{pos:.1f}" y2="{d:.1f}" {wall}/>'
            f'<line x1="{pos:.1f}" y1="{d + dw:.1f}" x2="{pos:.1f}" y2="{b:.1f}" {wall}/>'
            f'<line x1="{pos:.1f}" y1="{d:.1f}" x2="{pos + s * dw:.1f}" y2="{d:.1f}" {door}/>'
            f'<path d="M {pos + s * dw:.1f} {d:.1f} A {dw} {dw} 0 0 {1 if s > 0 else 0} {pos:.1f} {d + dw:.1f}" {door}/>'
        )
    return (
        f'<line x1="{a:.1f}" y1="{pos:.1f}" x2="{d:.1f}" y2="{pos:.1f}" {wall}/>'
        f'<line x1="{d + dw:.1f}" y1="{pos:.1f}" x2="{b:.1f}" y2="{pos:.1f}" {wall}/>'
        f'<line x1="{d:.1f}" y1="{pos:.1f}" x2="{d:.1f}" y2="{pos + s * dw:.1f}" {door}/>'
        f'<path d="M {d:.1f} {pos + s * dw:.1f} A {dw} {dw} 0 0 {0 if s > 0 else 1} {d + dw:.1f} {pos:.1f}" {door}/>'
    )


def generate_banner_svg(now):
    """A procedural floor plan, different every day (seeded by the date)."""
    seed = int(now.strftime("%Y%m%d"))
    rng = random.Random(seed)

    W, H = 1200, 290
    PX, PY, PW, PH = 40, 30, 760, 200
    METERS_ACROSS = 20.0
    m_per_px = METERS_ACROSS / PW

    leaves, splits = [], []
    bsp_split((PX, PY, PW, PH), 0, rng, leaves, splits)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'font-family="{FONT}" role="img" aria-label="Generative floor plan banner">',
        "<defs>",
        '<pattern id="minor" width="20" height="20" patternUnits="userSpaceOnUse">'
        f'<path d="M 20 0 L 0 0 0 20" fill="none" stroke="{GRID}" stroke-width="0.5"/></pattern>',
        '<pattern id="major" width="100" height="100" patternUnits="userSpaceOnUse">'
        f'<rect width="100" height="100" fill="url(#minor)"/>'
        f'<path d="M 100 0 L 0 0 0 100" fill="none" stroke="{GRID}" stroke-width="1.2"/></pattern>',
        '<pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<line x1="0" y1="0" x2="0" y2="8" stroke="{ACCENT}" stroke-width="1" opacity="0.45"/></pattern>',
        "</defs>",
        f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>',
        f'<rect width="{W}" height="{H}" rx="10" fill="url(#major)"/>',
    ]

    # Accent rooms (hatched / tinted)
    accent_idx = rng.sample(range(len(leaves)), k=min(3, len(leaves)))
    for n, i in enumerate(accent_idx):
        x, y, w, h = leaves[i]
        fill = "url(#hatch)" if n == 0 else ACCENT
        opacity = "1" if n == 0 else "0.10"
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" opacity="{opacity}"/>')

    # Interior walls with doors
    for orient, pos, a, b in splits:
        out.append(_wall_with_door(orient, pos, a, b, rng))

    # Outer wall
    out.append(f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" fill="none" stroke="{WALL}" stroke-width="3.5"/>')

    # Room labels
    for idx, (x, y, w, h) in enumerate(leaves, start=1):
        area = w * h * (m_per_px ** 2)
        label = f"R{idx:02d}" if w < 84 else f"R{idx:02d} · {area:.1f} m²"
        out.append(
            f'<text x="{x + w / 2:.1f}" y="{y + h / 2 + 3:.1f}" font-size="10" fill="{MUTED}" '
            f'text-anchor="middle">{html.escape(label)}</text>'
        )

    # Dimension line
    dy = PY + PH + 24
    out.append(f'<line x1="{PX}" y1="{dy}" x2="{PX + PW}" y2="{dy}" stroke="{ACCENT}" stroke-width="1"/>')
    for tx in (PX, PX + PW):
        out.append(f'<line x1="{tx}" y1="{dy - 6}" x2="{tx}" y2="{dy + 6}" stroke="{ACCENT}" stroke-width="1"/>')
        out.append(f'<line x1="{tx - 4}" y1="{dy + 4}" x2="{tx + 4}" y2="{dy - 4}" stroke="{ACCENT}" stroke-width="1"/>')
    out.append(
        f'<rect x="{PX + PW / 2 - 40}" y="{dy - 8}" width="80" height="16" fill="{BG}"/>'
        f'<text x="{PX + PW / 2}" y="{dy + 4}" font-size="11" fill="{ACCENT}" text-anchor="middle">'
        f"{METERS_ACROSS:.2f} m</text>"
    )

    # Title block
    bx, by, bw, bh = 830, 30, 330, 220
    out.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{BG}" fill-opacity="0.85" stroke="{LINE}" stroke-width="1.2"/>')
    out.append(f'<text x="{bx + 18}" y="{by + 40}" font-size="21" font-weight="bold" fill="{WALL}" letter-spacing="0.5">{html.escape(NAME)}</text>')
    out.append(f'<text x="{bx + 18}" y="{by + 62}" font-size="11" fill="{ACCENT}" letter-spacing="0.5">{html.escape(ROLE)}</text>')
    out.append(f'<line x1="{bx}" y1="{by + 80}" x2="{bx + bw}" y2="{by + 80}" stroke="{LINE}" stroke-width="1"/>')
    rows = [
        ("SHEET", "A-01 / GENERATIVE PLAN"),
        ("SCALE", "1:100"),
        ("DATE", now.strftime("%Y-%m-%d")),
        ("SEED", str(seed)),
        ("LOCATION", LOCATION),
    ]
    for i, (k, v) in enumerate(rows):
        ry = by + 106 + i * 26
        out.append(f'<text x="{bx + 18}" y="{ry}" font-size="10" fill="{MUTED}">{k}</text>')
        out.append(f'<text x="{bx + 100}" y="{ry}" font-size="11" fill="{WALL}">{html.escape(v)}</text>')

    out.append("</svg>")
    return "\n".join(out)


# ===========================================================================
# 2. Career timeline
# ===========================================================================
def generate_timeline_svg():
    W, H = 1200, 230
    n = len(TIMELINE)
    x0, x1 = 120, W - 120
    line_y = 100
    step = (x1 - x0) / (n - 1) if n > 1 else 0

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'font-family="{FONT}" role="img" aria-label="Career timeline">',
        f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>',
        f'<text x="40" y="34" font-size="11" fill="{ACCENT}" letter-spacing="2">FROM SKETCH TO CODE</text>',
        f'<line x1="60" y1="{line_y}" x2="{W - 60}" y2="{line_y}" stroke="{LINE}" stroke-width="1.5"/>',
    ]
    # ruler ticks
    for tx in range(60, W - 59, 24):
        out.append(f'<line x1="{tx}" y1="{line_y - 4}" x2="{tx}" y2="{line_y + 4}" stroke="{GRID}" stroke-width="1"/>')

    for i, item in enumerate(TIMELINE):
        cx = x0 + i * step
        last = i == n - 1
        size = 16 if last else 12
        fill = ACCENT if last else BG
        out.append(
            f'<rect x="{cx - size / 2:.1f}" y="{line_y - size / 2:.1f}" width="{size}" height="{size}" '
            f'fill="{fill}" stroke="{ACCENT}" stroke-width="2"/>'
        )
        if item.get("when"):
            out.append(f'<text x="{cx:.1f}" y="{line_y - 24}" font-size="12" fill="{MUTED}" text-anchor="middle">{html.escape(item["when"])}</text>')

        y = line_y + 34
        for line in textwrap.wrap(item["title"], 22):
            out.append(f'<text x="{cx:.1f}" y="{y}" font-size="13" font-weight="bold" fill="{WALL}" text-anchor="middle">{html.escape(line)}</text>')
            y += 17
        y += 3
        for line in textwrap.wrap(item.get("sub", ""), 28):
            out.append(f'<text x="{cx:.1f}" y="{y}" font-size="11" fill="{MUTED}" text-anchor="middle">{html.escape(line)}</text>')
            y += 15

    out.append("</svg>")
    return "\n".join(out)


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
        f'<img width="100%" src="{banner_url}" alt="Generative floor plan — {html.escape(NAME.title())}"/>',
        "<br/><br/>",
        render_insight_html(insight),
        "<br/>",
        f'<img width="100%" src="{timeline_url}" alt="Career timeline: from architecture to AI engineering"/>',
        "<br/><br/>",
        "### 🛠️ Tech Stack",
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
    parts += ["  </tr>", "</table>", "<br/>", "### 🤝 Let's Connect", '<p align="center">']
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

    with open(os.path.join(ASSETS_DIR, "banner.svg"), "w", encoding="utf-8") as f:
        f.write(generate_banner_svg(now))
    with open(os.path.join(ASSETS_DIR, "timeline.svg"), "w", encoding="utf-8") as f:
        f.write(generate_timeline_svg())
    print("🏛️ Banner and timeline generated")

    insight = get_insight(now)
    print(f"✅ Insight: {insight['headline']} ({insight['model']})")

    update_readme(generate_profile_html(insight, now))
    print("✨ Profile generation complete!")