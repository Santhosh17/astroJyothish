# -*- coding: utf-8 -*-
"""
chart_svg.py - South Indian (and North Indian) kundali renderers.

South Indian is the default for South Indian charts and is what most
Kannada/Tamil/Telugu/Malayalam speakers expect. Signs are FIXED in the
grid; the lagna is marked with a diagonal stroke in its box. North Indian
is diamond-shaped with fixed HOUSES and moving signs - use it only if the
person asks for it (typically North Indian / Hindi-belt convention).

    from chart_svg import south_indian
    svg = south_indian({8: ["As"], 11: ["Su", "Ju", "Ra"]}, lagna_sign=8)
"""

# Fixed sign positions in the 4x4 South Indian grid, (row, col).
# Pisces top-left, then clockwise: Aries, Taurus, Gemini across the top.
GRID = {11: (0, 0), 0: (0, 1), 1: (0, 2), 2: (0, 3),
        3: (1, 3), 4: (2, 3), 5: (3, 3),
        6: (3, 2), 7: (3, 1), 8: (3, 0),
        9: (2, 0), 10: (1, 0)}

ABBR3 = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir",
         "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]

PLANET_ABBR = {"Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
               "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa",
               "Rahu": "Ra", "Ketu": "Ke", "Asc": "As", "Lagna": "As"}

# Colour roles. Malefics rust, nodes indigo, lagna ochre, benefics ink.
KIND = {"Su": "mal", "Ma": "mal", "Sa": "mal",
        "Mo": "ben", "Me": "ben", "Ju": "ben", "Ve": "ben",
        "Ra": "nod", "Ke": "nod", "As": "asc"}

DEFAULT_CSS = {
    "chart_bg": "#FBFCFA", "chart_in": "#EDF0EE", "ink": "#12191B",
    "rule": "#A6B4B3", "muted": "#7C8C8D", "mal": "#9E2B1C",
    "nod": "#26356B", "asc": "#8A6A12",
}


def south_indian(placement, lagna_sign, size=300, degrees=None,
                 use_css_vars=True, css=None):
    """Render a South Indian kundali as an SVG string.

    placement    {sign_index: [planet abbreviations or full names]}
    lagna_sign   sign index 0-11 to mark with the diagonal stroke.
                 For a Chandra-lagna chart pass the Moon's sign here and
                 keep "As" in the true ascendant's box.
    degrees      optional {abbr: "12"} to print degrees next to each planet
    use_css_vars emit var(--chart-bg) etc. for embedding in a themed page;
                 set False to bake in literal hex from `css`.
    """
    c = dict(DEFAULT_CSS)
    if css:
        c.update(css)

    def col(name):
        return f"var(--{name.replace('_','-')})" if use_css_vars else c[name]

    W = size
    cell = W / 4.0
    o = [f'<svg viewBox="0 0 {W} {W}" xmlns="http://www.w3.org/2000/svg" '
         f'class="kundali" role="img">']
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{W-1}" '
             f'fill="{col("chart_bg")}" stroke="{col("ink")}" stroke-width="1.4"/>')
    o.append(f'<rect x="{cell}" y="{cell}" width="{2*cell}" height="{2*cell}" '
             f'fill="{col("chart_in")}" stroke="{col("ink")}" stroke-width="1.1"/>')
    for si, (r, cc) in GRID.items():
        x, y = cc * cell, r * cell
        o.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
                 f'fill="none" stroke="{col("rule")}" stroke-width="0.9"/>')
    for si, (r, cc) in GRID.items():
        x, y = cc * cell, r * cell
        if si == lagna_sign:
            o.append(f'<path d="M {x+1} {y+cell*0.40} L {x+cell*0.40} {y+1}" '
                     f'stroke="{col("mal")}" stroke-width="1.8" fill="none"/>')
        o.append(f'<text x="{x+cell-3.5}" y="{y+cell-4}" class="sgl" '
                 f'text-anchor="end" font-size="8" fill="{col("muted")}" '
                 f'font-family="monospace">{ABBR3[si]}</text>')
        items = [PLANET_ABBR.get(p, p) for p in placement.get(si, [])]
        n = len(items)
        if not n:
            continue
        fs = 10.2 if n <= 4 else 9.0
        lh = fs + 2.6
        top = max(y + (cell - n * lh) / 2 + fs * 0.95, y + 12)
        for j, ab in enumerate(items):
            label = ab + (" " + degrees[ab] if degrees and ab in degrees else "")
            k = KIND.get(ab, "ben")
            fill = col("ink") if k == "ben" else col(k)
            wt = "600" if k == "asc" else "500"
            o.append(f'<text x="{x+cell/2}" y="{top+j*lh}" class="pl {k}" '
                     f'text-anchor="middle" font-size="{fs}" fill="{fill}" '
                     f'font-weight="{wt}" font-family="monospace">{label}</text>')
    o.append("</svg>")
    return "".join(o)


def north_indian(placement, lagna_sign, size=300, use_css_vars=True, css=None):
    """Diamond chart with fixed houses. House 1 is the top centre diamond.

    placement is still keyed by SIGN index; the renderer converts to houses
    using lagna_sign, so callers pass the same dict either way.
    """
    c = dict(DEFAULT_CSS)
    if css:
        c.update(css)

    def col(name):
        return f"var(--{name.replace('_','-')})" if use_css_vars else c[name]

    W = size
    h = W / 2.0
    q = W / 4.0
    # centroid of each house region, house 1 .. 12
    pts = [(h, q * 0.62), (q * 0.62, q * 0.42), (q * 0.42, q * 0.62),
           (q * 0.72, h), (q * 0.42, W - q * 0.62), (q * 0.62, W - q * 0.42),
           (h, W - q * 0.62), (W - q * 0.62, W - q * 0.42),
           (W - q * 0.42, W - q * 0.62), (W - q * 0.72, h),
           (W - q * 0.42, q * 0.62), (W - q * 0.62, q * 0.42)]
    o = [f'<svg viewBox="0 0 {W} {W}" xmlns="http://www.w3.org/2000/svg" role="img">']
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{W-1}" '
             f'fill="{col("chart_bg")}" stroke="{col("ink")}" stroke-width="1.4"/>')
    st = f'stroke="{col("rule")}" stroke-width="0.9" fill="none"'
    o.append(f'<path d="M 0 0 L {W} {W} M {W} 0 L 0 {W}" {st}/>')
    o.append(f'<path d="M {h} 0 L {W} {h} L {h} {W} L 0 {h} Z" {st}/>')
    for hi in range(1, 13):
        si = (lagna_sign + hi - 1) % 12
        x, y = pts[hi - 1]
        o.append(f'<text x="{x}" y="{y-9}" text-anchor="middle" font-size="8" '
                 f'fill="{col("muted")}" font-family="monospace">{ABBR3[si]}</text>')
        items = [PLANET_ABBR.get(p, p) for p in placement.get(si, [])]
        for j, ab in enumerate(items):
            k = KIND.get(ab, "ben")
            fill = col("ink") if k == "ben" else col(k)
            o.append(f'<text x="{x}" y="{y+4+j*11}" text-anchor="middle" '
                     f'font-size="10" fill="{fill}" font-weight="500" '
                     f'font-family="monospace">{ab}</text>')
    o.append("</svg>")
    return "".join(o)


def placement_from(planet_lons, varga_fn=None, division=1, asc_lon=None):
    """Build the placement dict for a given divisional chart.

    -> (placement, lagna_sign_in_that_varga)
    """
    pm = {}
    lag = None
    if asc_lon is not None:
        lag = varga_fn(asc_lon, division) if varga_fn else int(asc_lon // 30)
        pm.setdefault(lag, []).append("Asc")
    for p, l in planet_lons.items():
        s = varga_fn(l, division) if varga_fn else int(l // 30)
        pm.setdefault(s, []).append(p)
    return pm, lag


if __name__ == "__main__":
    demo = {0: ["Asc", "Jupiter", "Saturn"], 3: ["Rahu"], 6: ["Moon"],
            7: ["Venus"], 8: ["Sun", "Mercury"], 9: ["Ketu"], 10: ["Mars"]}
    print(south_indian(demo, 0, use_css_vars=False))
