"""Draw the 1200x630 link-preview image for /connected from the exported data.

The ring of statistics and the links that survive once income is held fixed are the
same ones the page draws, so the preview changes when the data does.

    python3 scripts/make_og_image.py [exports/connected_world.json] [exports/connected-og.png]

Needs Pillow. Fonts: Inter Display and DejaVu Sans Mono, found on most Linux images.
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "exports/connected_world.json")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "exports/connected-og.png")

NIGHT, HEAD, BODY, MUTED = (4, 6, 11), (244, 239, 230), (196, 202, 214), (122, 132, 150)
GOLD, BLUE, HAIR = (242, 196, 107), (91, 141, 239), (30, 38, 56)
DOMAINS = ["Wealth", "People", "Health", "Wellbeing", "Technology", "Environment", "Sport", "Mobility"]


def font(names, size):
    for name in names:
        for root in ("/usr/share/fonts/opentype/inter", "/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/liberation"):
            p = Path(root) / name
            if p.exists():
                return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def main():
    d = json.loads(SRC.read_text())
    K = d["kpis"]
    S = 2  # draw at 2x, then downsample for smooth lines
    W, H = 1200 * S, 630 * S
    img = Image.new("RGB", (W, H), NIGHT)
    g = ImageDraw.Draw(img, "RGBA")

    # network on the right, laid out like the page: domains around a ring, income in the middle
    cx, cy, R = 905 * S, 315 * S, 225 * S
    ring = sorted([n for n in d["nodes"] if n["indicator"] != "gdp_pcap"], key=lambda n: DOMAINS.index(n["domain"]))
    slots, k, prev, pos = len(ring) + len(DOMAINS), 0, None, {}
    for n in ring:
        if n["domain"] != prev:
            k += 1
            prev = n["domain"]
        a = -math.pi / 2 + (k / slots) * 2 * math.pi
        pos[n["indicator"]] = (cx + R * math.cos(a), cy + R * math.sin(a))
        k += 1
    pos["gdp_pcap"] = (cx, cy)

    for e in d["edges"]:
        if e.get("income") and e["a"] in pos and e["b"] in pos:
            g.line([pos[e["a"]], pos[e["b"]]], fill=(255, 236, 200, 38), width=2 * S)
    for e in d["edges"]:
        if not e.get("beyond") or e["a"] not in pos or e["b"] not in pos:
            continue
        (ax, ay), (bx, by) = pos[e["a"]], pos[e["b"]]
        mx, my = (ax + bx) / 2, (ay + by) / 2
        qx, qy = mx + (cx - mx) * 0.55, my + (cy - my) * 0.55
        pts = [((1 - t) ** 2 * ax + 2 * (1 - t) * t * qx + t * t * bx, (1 - t) ** 2 * ay + 2 * (1 - t) * t * qy + t * t * by) for t in [i / 40 for i in range(41)]]
        col = GOLD if e["partial_rho"] > 0 else BLUE
        w = int((1.2 + max(0, abs(e["partial_rho"]) - 0.3) * 9) * S)
        g.line(pts, fill=col + (215,), width=max(2, w), joint="curve")
    for n in ring:
        x, y = pos[n["indicator"]]
        r = (4 + min(6, n["links_beyond_income"] * 0.9)) * S
        g.ellipse([x - r - 3 * S, y - r - 3 * S, x + r + 3 * S, y + r + 3 * S], fill=NIGHT)
        g.ellipse([x - r, y - r, x + r, y + r], fill=GOLD)
    r = 14 * S
    g.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 226, 160))

    # text on the left
    mono = font(["DejaVuSansMono.ttf", "LiberationMono-Regular.ttf"], 17 * S)
    title = font(["InterDisplay-Black.otf", "InterDisplay-ExtraBold.otf", "DejaVuSans-Bold.ttf"], 84 * S)
    body = font(["Inter-Medium.otf", "Inter-Regular.otf", "DejaVuSans.ttf"], 25 * S)
    num = font(["InterDisplay-Bold.otf", "DejaVuSans-Bold.ttf"], 46 * S)
    small = font(["Inter-Regular.otf", "DejaVuSans.ttf"], 17 * S)

    x0 = 68 * S
    g.line([(x0, 82 * S), (x0 + 34 * S, 82 * S)], fill=GOLD, width=2 * S)
    g.text((x0 + 48 * S, 71 * S), "PROJECT  ·  CONNECTED WORLD", font=mono, fill=GOLD)
    g.text((x0 - 4 * S, 116 * S), "The world,", font=title, fill=HEAD)
    g.text((x0 - 4 * S, 206 * S), "connected.", font=title, fill=GOLD)
    g.text((x0, 322 * S), f"{K['sources']} open datasets on {K['countries']} countries.", font=body, fill=BODY)
    g.text((x0, 356 * S), "What really moves together once", font=body, fill=BODY)
    g.text((x0, 390 * S), "you account for money?", font=body, fill=BODY)

    stats = [(f"{round(K['share_explained_by_income'] * 100)}%", "of strong links\nare about income"),
             (str(K["links_beyond_income"]), "links survive\nincome held fixed"),
             (f"{int(K['football_matches_rated']) // 1000}K", "football matches\nrated since 1872")]
    for i, (v, lab) in enumerate(stats):
        sx = x0 + i * 178 * S
        g.text((sx, 448 * S), v, font=num, fill=HEAD if i else GOLD)
        g.multiline_text((sx, 504 * S), lab, font=small, fill=MUTED, spacing=4 * S)

    g.line([(x0, 572 * S), (1132 * S, 572 * S)], fill=HAIR, width=S)
    g.text((x0, 586 * S), "hani-alnaber.com/connected", font=mono, fill=MUTED)
    g.text((1132 * S, 586 * S), "Hani Al Naber · Data Engineer", font=mono, fill=MUTED, anchor="ra")

    img.resize((1200, 630), Image.LANCZOS).save(OUT, optimize=True)
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
