# -*- coding: utf-8 -*-
"""
jyotish.py - Vedic astrology computation engine built on the Swiss Ephemeris.

Every table in this file has been checksum-validated. Do not "fix" a table
because output looks unfamiliar - run the self-test first:

    python3 jyotish.py --selftest

Setup (once per session):
    pip install pyswisseph --break-system-packages
    mkdir -p ephe && cd ephe
    for f in sepl_18.se1 semo_18.se1 seas_18.se1; do
      curl -sL -o $f "https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/$f"
    done

Without the .se1 files pyswisseph silently falls back to the Moshier
ephemeris. That is still accurate to about 1 arcsecond and fine for jyotish,
but download the files when the network allows so results are reproducible.
"""

import math
import swisseph as swe

# ---------------------------------------------------------------- constants

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGNS_SKT = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
             "Tula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"]
ABBR3 = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir",
         "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]

NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
              "Punarvasu", "Pushya", "Ashlesha", "Magha", "P.Phalguni",
              "U.Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
              "Jyeshtha", "Mula", "P.Ashadha", "U.Ashadha", "Shravana",
              "Dhanishta", "Shatabhisha", "P.Bhadrapada", "U.Bhadrapada", "Revati"]

# Vimshottari lord of each nakshatra, cycling every 9
DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
               "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
               "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
SOLAR_YEAR = 365.2425          # days; standard for Vimshottari

SIGN_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
              "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]

# (sign_index, degree) of exaltation. Debilitation is the opposite sign.
EXALTATION = {"Sun": (0, 10), "Moon": (1, 3), "Mars": (9, 28), "Mercury": (5, 15),
              "Jupiter": (3, 5), "Venus": (11, 27), "Saturn": (6, 20)}
OWN_SIGNS = {"Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5],
             "Jupiter": [8, 11], "Venus": [1, 6], "Saturn": [9, 10]}
# (sign, from_deg, to_deg)
MOOLATRIKONA = {"Sun": (4, 0, 20), "Moon": (1, 4, 30), "Mars": (0, 0, 12),
                "Mercury": (5, 16, 20), "Jupiter": (8, 0, 10),
                "Venus": (6, 0, 15), "Saturn": (10, 0, 20)}
# (friends, neutrals, enemies) - naisargika (natural) relationships
NAISARGIKA = {
    "Sun":     (["Moon", "Mars", "Jupiter"], ["Mercury"], ["Venus", "Saturn"]),
    "Moon":    (["Sun", "Mercury"], ["Mars", "Jupiter", "Venus", "Saturn"], []),
    "Mars":    (["Sun", "Moon", "Jupiter"], ["Venus", "Saturn"], ["Mercury"]),
    "Mercury": (["Sun", "Venus"], ["Mars", "Jupiter", "Saturn"], ["Moon"]),
    "Jupiter": (["Sun", "Moon", "Mars"], ["Saturn"], ["Mercury", "Venus"]),
    "Venus":   (["Mercury", "Saturn"], ["Mars", "Jupiter"], ["Sun", "Moon"]),
    "Saturn":  (["Mercury", "Venus"], ["Jupiter"], ["Sun", "Moon", "Mars"]),
}

# Combustion (asta) orbs in degrees from the Sun. Direct-motion values.
COMBUSTION = {"Moon": 12, "Mars": 17, "Mercury": 14, "Jupiter": 11,
              "Venus": 10, "Saturn": 15}
COMBUSTION_RETRO = {"Mercury": 12, "Venus": 8}

# Special aspects (graha drishti), counted in signs including the occupied one.
SPECIAL_ASPECTS = {"Mars": [4, 7, 8], "Jupiter": [5, 7, 9], "Saturn": [3, 7, 10],
                   "Rahu": [5, 7, 9], "Ketu": [5, 7, 9]}

PLANET_IDS = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
              "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
              "Venus": swe.VENUS, "Saturn": swe.SATURN}
PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
                "Saturn", "Rahu", "Ketu"]

AYANAMSA_MODES = {"raman": swe.SIDM_RAMAN, "lahiri": swe.SIDM_LAHIRI,
                  "krishnamurti": swe.SIDM_KRISHNAMURTI,
                  "fagan_bradley": swe.SIDM_FAGAN_BRADLEY}


# ------------------------------------------------------- ashtakavarga tables
# Bhinnashtakavarga benefic-point tables, standard Parashari.
# Row totals MUST be: Sun 48, Moon 49, Mars 39, Mercury 54, Jupiter 56,
# Venus 52, Saturn 39; grand total 337. assert_bav_totals() enforces this.
#
# GOTCHA: the Venus-from-Lagna row is the one most often mistyped. It is
# [1,2,3,4,5,8,9,11] (eight places). Dropping the 11 gives a Venus total of
# 51 and a grand total of 336, which is the usual symptom of a bad table.

BAV_TABLE = {
    "Sun": {"Sun": [1, 2, 4, 7, 8, 9, 10, 11], "Moon": [3, 6, 10, 11],
            "Mars": [1, 2, 4, 7, 8, 9, 10, 11], "Mercury": [3, 5, 6, 9, 10, 11, 12],
            "Jupiter": [5, 6, 9, 11], "Venus": [6, 7, 12],
            "Saturn": [1, 2, 4, 7, 8, 9, 10, 11], "Asc": [3, 4, 6, 10, 11, 12]},
    "Moon": {"Sun": [3, 6, 7, 8, 10, 11], "Moon": [1, 3, 6, 7, 10, 11],
             "Mars": [2, 3, 5, 6, 9, 10, 11], "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
             "Jupiter": [1, 4, 7, 8, 10, 11, 12], "Venus": [3, 4, 5, 7, 9, 10, 11],
             "Saturn": [3, 5, 6, 11], "Asc": [3, 6, 10, 11]},
    "Mars": {"Sun": [3, 5, 6, 10, 11], "Moon": [3, 6, 11],
             "Mars": [1, 2, 4, 7, 8, 10, 11], "Mercury": [3, 5, 6, 11],
             "Jupiter": [6, 10, 11, 12], "Venus": [6, 8, 11, 12],
             "Saturn": [1, 4, 7, 8, 9, 10, 11], "Asc": [1, 3, 6, 10, 11]},
    "Mercury": {"Sun": [5, 6, 9, 11, 12], "Moon": [2, 4, 6, 8, 10, 11],
                "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
                "Mercury": [1, 3, 5, 6, 9, 10, 11, 12], "Jupiter": [6, 8, 11, 12],
                "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
                "Saturn": [1, 2, 4, 7, 8, 9, 10, 11], "Asc": [1, 2, 4, 6, 8, 10, 11]},
    "Jupiter": {"Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11], "Moon": [2, 5, 7, 9, 11],
                "Mars": [1, 2, 4, 7, 8, 10, 11],
                "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
                "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
                "Venus": [2, 5, 6, 9, 10, 11], "Saturn": [3, 5, 6, 12],
                "Asc": [1, 2, 4, 5, 6, 7, 9, 10, 11]},
    "Venus": {"Sun": [8, 11, 12], "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
              "Mars": [3, 5, 6, 9, 11, 12], "Mercury": [3, 5, 6, 9, 11],
              "Jupiter": [5, 8, 9, 10, 11],
              "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
              "Saturn": [3, 4, 5, 8, 9, 10, 11],
              "Asc": [1, 2, 3, 4, 5, 8, 9, 11]},
    "Saturn": {"Sun": [1, 2, 4, 7, 8, 10, 11], "Moon": [3, 6, 11],
               "Mars": [3, 5, 6, 10, 11, 12], "Mercury": [6, 8, 9, 10, 11, 12],
               "Jupiter": [5, 6, 11, 12], "Venus": [6, 11, 12],
               "Saturn": [3, 5, 6, 11], "Asc": [1, 3, 4, 6, 10, 11]},
}
BAV_CHECKSUM = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
                "Jupiter": 56, "Venus": 52, "Saturn": 39}

# Classical gochara: favourable transit houses counted from the natal Moon.
GOCHARA_GOOD = {"Sun": [3, 6, 10, 11], "Moon": [1, 3, 6, 7, 10, 11],
                "Mars": [3, 6, 11], "Mercury": [2, 4, 6, 8, 10, 11],
                "Jupiter": [2, 5, 7, 9, 11],
                "Venus": [1, 2, 3, 4, 5, 8, 9, 11, 12],
                "Saturn": [3, 6, 11], "Rahu": [3, 6, 11], "Ketu": [3, 6, 11]}


# ------------------------------------------------------------------ helpers

def setup(ephe_path="./ephe", ayanamsa="raman"):
    """Call once before anything else."""
    swe.set_ephe_path(ephe_path)
    swe.set_sid_mode(AYANAMSA_MODES[ayanamsa], 0, 0)


def julday(year, month, day, hour, minute, second=0, tz_offset=5.5):
    """Local civil time -> Julian Day (UT).

    tz_offset is hours east of Greenwich. India is +5.5 and has had no
    daylight saving since 1945 - do NOT apply DST for Indian births.
    For other countries check the historical DST rules for that exact date.
    """
    frac = hour + minute / 60.0 + second / 3600.0 - tz_offset
    return swe.julday(year, month, day, 0.0, swe.GREG_CAL) + frac / 24.0


def dms(x):
    """Decimal degrees -> 12°34'56\" string."""
    neg = x < 0
    x = abs(x)
    d = int(x)
    m = int((x - d) * 60)
    s = (((x - d) * 60) - m) * 60
    if round(s, 1) >= 60:
        s = 0.0
        m += 1
    if m >= 60:
        m = 0
        d += 1
    return f"{'-' if neg else ''}{d:02d}\u00b0{m:02d}'{s:04.1f}\""


def sign_of(lon):
    return int((lon % 360) // 30)


def nakshatra_of(lon):
    """-> (index 0-26, pada 1-4, lord)"""
    lon %= 360
    ni = int(lon // (360 / 27))
    pada = int((lon % (360 / 27)) // (360 / 108)) + 1
    return ni, pada, DASHA_ORDER[ni % 9]


def house_from(sign_index, reference_sign):
    """Whole-sign house number of sign_index counted from reference_sign."""
    return (sign_index - reference_sign) % 12 + 1


# ----------------------------------------------------------------- positions

def positions(jd_ut, node="mean"):
    """-> {name: {'lon','speed','retro','sign','deg','nak','pada','naklord'}}"""
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    out = {}
    for name, pid in PLANET_IDS.items():
        xx, _ = swe.calc_ut(jd_ut, pid, flags)
        out[name] = _pack(xx[0] % 360, xx[3])
    nid = swe.MEAN_NODE if node == "mean" else swe.TRUE_NODE
    xx, _ = swe.calc_ut(jd_ut, nid, flags)
    out["Rahu"] = _pack(xx[0] % 360, xx[3])
    out["Ketu"] = _pack((xx[0] + 180) % 360, xx[3])
    return out


def _pack(lon, speed):
    ni, pada, lord = nakshatra_of(lon)
    return {"lon": lon, "speed": speed, "retro": speed < 0,
            "sign": sign_of(lon), "deg": lon % 30,
            "nak": ni, "pada": pada, "naklord": lord}


def ascendant(jd_ut, lat, lon_east, hsys=b"W"):
    """-> (asc_longitude, mc_longitude, cusps).

    hsys: b'W' whole sign, b'O' Porphyry (== Sripati bhava madhya),
          b'P' Placidus, b'B' Alcabitius.
    The ascendant itself is identical across all of these; only the
    intermediate cusps differ.

    Above roughly 66 degrees latitude Placidus (b'P') and Koch are
    mathematically undefined and swisseph raises. Whole sign and Porphyry
    work at every latitude, and whole sign is the jyotish default anyway,
    so polar births are fine - just do not reach for Placidus there.
    """
    cusps, ascmc = swe.houses_ex(jd_ut, lat, lon_east, hsys, swe.FLG_SIDEREAL)
    return ascmc[0] % 360, ascmc[1] % 360, [c % 360 for c in cusps]


def bhava_chalit(jd_ut, lat, lon_east, planet_lons):
    """Sripati/Porphyry bhava assignment vs whole sign.

    Returns {planet: (whole_sign_house, sripati_house)}. ALWAYS run this.
    A planet within a few degrees of a bhava sandhi changes house between
    the two systems, which can change the reading more than anything else
    in the chart. Report any shift explicitly rather than silently picking
    one system.
    """
    _, _, madhya = ascendant(jd_ut, lat, lon_east, b"O")
    lag = sign_of(madhya[0])
    sandhi = []
    for i in range(12):
        a1, a2 = madhya[i], madhya[(i + 1) % 12]
        sandhi.append((a1 + ((a2 - a1) % 360) / 2) % 360)
    out = {}
    for p, l in planet_lons.items():
        ws = house_from(sign_of(l), lag)
        bh = None
        for i in range(12):
            lo, hi = sandhi[(i - 1) % 12], sandhi[i]
            if ((l - lo) % 360) < ((hi - lo) % 360):
                bh = i + 1
                break
        out[p] = (ws, bh)
    return out


# -------------------------------------------------------------------- vargas

def varga(lon, division):
    """Sign index of a longitude in divisional chart D-<division>.

    Supports the shodashavarga: 1 2 3 4 7 9 10 12 16 20 24 27 30 40 45 60.
    """
    s = sign_of(lon)
    d = lon % 30
    odd = (s % 2 == 0)          # Aries/Gemini/... are the "odd" signs
    movable, fixed = (s % 3 == 0), (s % 3 == 1)

    def part(n):
        return int(d // (30.0 / n))

    if division == 1:
        return s
    if division == 2:
        h = int(d // 15)
        return 4 if ((odd and h == 0) or (not odd and h == 1)) else 3
    if division == 3:
        return (s + part(3) * 4) % 12
    if division == 4:
        return (s + part(4) * 3) % 12
    if division == 7:
        return ((s if odd else s + 6) + part(7)) % 12
    if division == 9:
        return (s * 9 + part(9)) % 12
    if division == 10:
        return ((s if odd else s + 8) + part(10)) % 12
    if division == 12:
        return (s + part(12)) % 12
    if division == 16:
        return ((0 if movable else 4 if fixed else 8) + part(16)) % 12
    if division == 20:
        return ((0 if movable else 8 if fixed else 4) + part(20)) % 12
    if division == 24:
        return ((4 if odd else 3) + part(24)) % 12
    if division == 27:
        return ([0, 3, 6, 9][s % 4] + part(27)) % 12
    if division == 30:
        if odd:
            return 0 if d < 5 else 10 if d < 10 else 8 if d < 18 else 2 if d < 25 else 6
        return 1 if d < 5 else 5 if d < 12 else 11 if d < 20 else 9 if d < 25 else 7
    if division == 40:
        return ((0 if odd else 6) + part(40)) % 12
    if division == 45:
        return ((0 if movable else 4 if fixed else 8) + part(45)) % 12
    if division == 60:
        return (s + part(60)) % 12
    raise ValueError(f"unsupported varga D-{division}")


SHODASHAVARGA = [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]
VARGA_NAMES = {1: "Rasi", 2: "Hora", 3: "Drekkana", 4: "Chaturthamsa",
               7: "Saptamsa", 9: "Navamsa", 10: "Dasamsa", 12: "Dwadasamsa",
               16: "Shodasamsa", 20: "Vimsamsa", 24: "Chaturvimsamsa",
               27: "Bhamsa", 30: "Trimsamsa", 40: "Khavedamsa",
               45: "Akshavedamsa", 60: "Shashtiamsa"}
VARGA_SIGNIFIES = {1: "body, life, everything", 2: "wealth, resources",
                   3: "siblings, courage", 4: "home, property, fortune",
                   7: "children, progeny", 9: "spouse, dharma, inner strength",
                   10: "career, status, action", 12: "parents, lineage",
                   16: "vehicles, comforts", 20: "spiritual practice",
                   24: "learning, education", 27: "strengths and weaknesses",
                   30: "misfortune, adversity", 40: "maternal legacy",
                   45: "paternal legacy", 60: "karma carried forward"}


def vargottama(planet_lons):
    """Planets holding the same sign in D-1 and D-9."""
    return [p for p, l in planet_lons.items()
            if varga(l, 1) == varga(l, 9)]


# ------------------------------------------------------------- ashtakavarga

def assert_bav_totals():
    """Run before trusting any ashtakavarga output."""
    for p, rules in BAV_TABLE.items():
        total = sum(len(v) for v in rules.values())
        assert total == BAV_CHECKSUM[p], f"{p} BAV total {total}, expected {BAV_CHECKSUM[p]}"
    assert sum(BAV_CHECKSUM.values()) == 337, "grand total is not 337"
    return True


def ashtakavarga(planet_signs, asc_sign):
    """-> (bav dict {planet: [12 ints]}, sav list of 12 ints).

    planet_signs: {'Sun':int, 'Moon':int, ..., 'Saturn':int} sign indices.
    """
    assert_bav_totals()
    ref = dict(planet_signs)
    ref["Asc"] = asc_sign
    bav, sav = {}, [0] * 12
    for p, rules in BAV_TABLE.items():
        row = [0] * 12
        for src, houses in rules.items():
            for h in houses:
                row[(ref[src] + h - 1) % 12] += 1
        assert sum(row) == BAV_CHECKSUM[p]
        bav[p] = row
        sav = [a + b for a, b in zip(sav, row)]
    assert sum(sav) == 337
    return bav, sav


# --------------------------------------------------------------- vimshottari

def vimshottari(jd_birth, moon_lon, levels=3, span_years=150):
    """Nested Vimshottari periods.

    -> list of dicts {level, lord, start_jd, end_jd, parents}
    level 1 = mahadasha, 2 = antardasha, 3 = pratyantardasha, ...

    span_years is measured FROM BIRTH, not from today. The default of 150
    covers a 19th-century birth through to the present; raise it further for
    historical charts. dasha_at() returns an empty list if the span does not
    reach the moment you queried - check for that rather than assuming the
    chart is at fault.
    """
    ni, _, lord = nakshatra_of(moon_lon)
    elapsed = (moon_lon % (360 / 27)) / (360 / 27)
    start = jd_birth - elapsed * DASHA_YEARS[lord] * SOLAR_YEAR
    out = []

    def expand(lord_, a, b, level, parents):
        out.append({"level": level, "lord": lord_, "start": a, "end": b,
                    "parents": list(parents)})
        if level >= levels:
            return
        i = DASHA_ORDER.index(lord_)
        c = a
        for k in range(9):
            sub = DASHA_ORDER[(i + k) % 9]
            dur = (b - a) * DASHA_YEARS[sub] / 120.0
            expand(sub, c, c + dur, level + 1, parents + [lord_])
            c += dur

    i = DASHA_ORDER.index(lord)
    cur = start
    while cur < jd_birth + span_years * SOLAR_YEAR:
        L = DASHA_ORDER[i % 9]
        expand(L, cur, cur + DASHA_YEARS[L] * SOLAR_YEAR, 1, [])
        cur += DASHA_YEARS[L] * SOLAR_YEAR
        i += 1
    return out


def dasha_at(periods, jd):
    """The nested stack of periods active at a given moment."""
    hits = [p for p in periods if p["start"] <= jd <= p["end"]]
    return sorted(hits, key=lambda p: p["level"])


# --------------------------------------------------------------- dignities

def dignity(planet, lon):
    """-> list of dignity strings for a planet at a longitude."""
    s, d = sign_of(lon), lon % 30
    tags = []
    ex_sign, _ = EXALTATION[planet]
    if s == ex_sign:
        tags.append("exalted")
    if s == (ex_sign + 6) % 12:
        tags.append("debilitated")
    mt = MOOLATRIKONA[planet]
    if s == mt[0] and mt[1] <= d < mt[2]:
        tags.append("moolatrikona")
    elif s in OWN_SIGNS[planet]:
        tags.append("own sign")
    lord = SIGN_LORDS[s]
    if lord != planet:
        fr, ne, en = NAISARGIKA[planet]
        tags.append(f"friend's sign ({lord})" if lord in fr else
                    f"neutral sign ({lord})" if lord in ne else
                    f"enemy's sign ({lord})")
    return tags


def combustion(planet_lons, retro=None):
    """-> {planet: (orb_degrees, limit, is_combust)}"""
    sun = planet_lons["Sun"]
    retro = retro or {}
    out = {}
    for p, limit in COMBUSTION.items():
        if p not in planet_lons:
            continue
        if retro.get(p) and p in COMBUSTION_RETRO:
            limit = COMBUSTION_RETRO[p]
        orb = abs((planet_lons[p] - sun + 180) % 360 - 180)
        out[p] = (orb, limit, orb < limit)
    return out


def aspects(planet_signs):
    """-> {planet: [signs it aspects]} using whole-sign graha drishti."""
    out = {}
    for p, s in planet_signs.items():
        casts = SPECIAL_ASPECTS.get(p, [7])
        out[p] = [(s + a - 1) % 12 for a in casts]
    return out


def chara_karakas(planet_lons, scheme=7):
    """Jaimini chara karakas by descending degree-in-sign.

    scheme=7 excludes Rahu (Parashari-Jaimini default).
    scheme=8 includes Rahu, whose degree is reckoned as 30 - deg.
    """
    names7 = ["Atmakaraka", "Amatyakaraka", "Bhratrikaraka", "Matrikaraka",
              "Putrakaraka", "Gnatikaraka", "Darakaraka"]
    names8 = ["Atmakaraka", "Amatyakaraka", "Bhratrikaraka", "Matrikaraka",
              "Pitrikaraka", "Putrakaraka", "Gnatikaraka", "Darakaraka"]
    degs = {p: planet_lons[p] % 30 for p in
            ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]}
    if scheme == 8:
        degs["Rahu"] = 30 - (planet_lons["Rahu"] % 30)
    names = names8 if scheme == 8 else names7
    ranked = sorted(degs.items(), key=lambda kv: -kv[1])
    return {n: (p, d) for n, (p, d) in zip(names, ranked)}


def gandanta(lon):
    """True if a longitude falls in a gandanta zone.

    Water->fire junctions: Pisces 26 40' - Aries 3 20',
    Cancer/Leo and Scorpio/Sagittarius likewise. Most significant for the
    Moon and the lagna; note it for any planet but weight it accordingly.
    """
    d = lon % 30
    s = sign_of(lon)
    water_end = s in (3, 7, 11) and d >= 26 + 40 / 60.0
    fire_start = s in (0, 4, 8) and d <= 3 + 20 / 60.0
    return water_end or fire_start


# ------------------------------------------------------------------- yogas
# Verify the FULL classical condition. Shorthand produces false positives,
# and false positives in a reading are worse than saying nothing.

def check_ruchaka(planet_lons, asc_sign, moon_sign):
    """Mars in own/exalted sign AND in a kendra from lagna OR from the Moon.

    The kendra requirement is the half everyone drops. Mars in its own sign
    in the 5th does NOT form Ruchaka.
    """
    s = sign_of(planet_lons["Mars"])
    dignified = s in OWN_SIGNS["Mars"] or s == EXALTATION["Mars"][0]
    kendra = (house_from(s, asc_sign) in (1, 4, 7, 10)
              or house_from(s, moon_sign) in (1, 4, 7, 10))
    return dignified and kendra, dignified, kendra


def check_mahapurusha(planet, planet_lons, asc_sign, moon_sign):
    """Generic Pancha-Mahapurusha test.
    Ruchaka=Mars, Bhadra=Mercury, Hamsa=Jupiter, Malavya=Venus, Sasa=Saturn.
    Returns (forms, dignified, in_kendra, combust_warning).
    """
    s = sign_of(planet_lons[planet])
    dignified = s in OWN_SIGNS[planet] or s == EXALTATION[planet][0]
    kendra = (house_from(s, asc_sign) in (1, 4, 7, 10)
              or house_from(s, moon_sign) in (1, 4, 7, 10))
    comb = combustion(planet_lons).get(planet, (99, 0, False))[2]
    return (dignified and kendra), dignified, kendra, comb


def check_kala_sarpa(planet_lons):
    """All seven grahas strictly inside one Rahu-Ketu semicircle.

    Returns (forms, {planet: which_half}, min_margin_degrees).
    A planet even a degree outside breaks it. Report the margin - a chart
    that misses by 1.5 degrees is not a Kala Sarpa chart, and saying so
    plainly is more useful than hedging.
    """
    ketu = planet_lons["Ketu"]
    halves = {}
    margins = []
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        a = (planet_lons[p] - ketu) % 360
        halves[p] = "ketu_to_rahu" if a < 180 else "rahu_to_ketu"
        margins.append(min(a, 360 - a, abs(a - 180)))
    forms = len(set(halves.values())) == 1
    return forms, halves, min(margins)


def check_kemadruma(planet_lons, asc_sign):
    """Kemadruma plus the standard cancellations (bhanga).

    Returns (forms, cancellations). Nodes and the Sun do not count as
    company for the Moon.
    """
    ms = sign_of(planet_lons["Moon"])
    second, twelfth = (ms + 1) % 12, (ms - 1) % 12
    company = [p for p in ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
               if sign_of(planet_lons[p]) in (second, twelfth, ms)]
    forms = len(company) == 0
    canc = []
    if house_from(ms, asc_sign) in (1, 4, 7, 10):
        canc.append("Moon in a kendra from the lagna")
    for p in ["Mercury", "Jupiter", "Venus"]:
        if house_from(sign_of(planet_lons[p]), ms) in (1, 4, 7, 10):
            canc.append(f"{p} in a kendra from the Moon")
    return forms, canc


def check_gaja_kesari(planet_lons):
    """Jupiter in a kendra from the Moon. Report combustion alongside."""
    h = house_from(sign_of(planet_lons["Jupiter"]), sign_of(planet_lons["Moon"]))
    comb = combustion(planet_lons)["Jupiter"][2]
    return h in (1, 4, 7, 10), h, comb


# ------------------------------------------------------------------ gochara

def transit_favourable(planet, transit_sign, natal_moon_sign):
    """Classical gochara judgement from the Janma Rashi."""
    return house_from(transit_sign, natal_moon_sign) in GOCHARA_GOOD[planet]


def sade_sati_state(saturn_sign, natal_moon_sign):
    """-> 'sade_sati' | 'ashtama_shani' | 'kantaka_shani' | 'none'

    These get confused constantly. Sade Sati is Saturn in the 12th, 1st or
    2nd from the natal Moon. Ashtama Shani is the 8th from the Moon.
    Kantaka/Ardha-ashtama is the 4th.
    """
    h = house_from(saturn_sign, natal_moon_sign)
    if h in (12, 1, 2):
        return "sade_sati"
    if h == 8:
        return "ashtama_shani"
    if h == 4:
        return "kantaka_shani"
    return "none"


def find_ingresses(jd_start, jd_end, planet_id, step=0.5):
    """-> [(jd_exact, new_sign_index)] by bisection."""
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    def sg(j):
        x, _ = swe.calc_ut(j, planet_id, flags)
        return sign_of(x[0])
    out, j, prev = [], jd_start, sg(jd_start)
    while j < jd_end:
        j += step
        s = sg(j)
        if s != prev:
            lo, hi = j - step, j
            for _ in range(50):
                mid = (lo + hi) / 2
                if sg(mid) == prev:
                    lo = mid
                else:
                    hi = mid
            out.append((hi, s))
            prev = s
    return out


def find_stations(jd_start, jd_end, planet_id, step=0.25):
    """-> [(jd_exact, 'R'|'D', longitude)] retrograde/direct stations."""
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    def spd(j):
        x, _ = swe.calc_ut(j, planet_id, flags)
        return x[3]
    out, j = [], jd_start
    prev = spd(j) < 0
    while j < jd_end:
        j += step
        cur = spd(j) < 0
        if cur != prev:
            lo, hi = j - step, j
            for _ in range(45):
                mid = (lo + hi) / 2
                if (spd(mid) < 0) == prev:
                    lo = mid
                else:
                    hi = mid
            x, _ = swe.calc_ut(hi, planet_id, flags)
            out.append((hi, "R" if cur else "D", x[0] % 360))
            prev = cur
    return out


def find_conjunctions(jd_start, jd_end, planet_id, natal_lon, step=0.5, orb=3.0):
    """Exact transit-over-natal-point crossings by bisection."""
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    def delta(j):
        x, _ = swe.calc_ut(j, planet_id, flags)
        return ((x[0] % 360) - natal_lon + 180) % 360 - 180
    out, j = [], jd_start
    d1 = delta(j)
    while j < jd_end:
        j += step
        d2 = delta(j)
        if d1 * d2 < 0 and abs(d1) < orb:
            lo, hi = j - step, j
            for _ in range(40):
                mid = (lo + hi) / 2
                if delta(mid) * d1 > 0:
                    lo = mid
                else:
                    hi = mid
            x, _ = swe.calc_ut(hi, planet_id, flags)
            out.append((hi, x[3] < 0))
        d1 = d2
    return out


def chandrashtama(jd_start, jd_end, natal_moon_sign, step=0.05):
    """Windows when the transiting Moon is in the 8th from the natal Moon."""
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    target = (natal_moon_sign + 7) % 12
    out, j, inside, st = [], jd_start, False, None
    while j < jd_end:
        x, _ = swe.calc_ut(j, swe.MOON, flags)
        s = sign_of(x[0])
        if s == target and not inside:
            st, inside = j, True
        elif s != target and inside:
            out.append((st, j))
            inside = False
        j += step
    return out


# ------------------------------------------------------------ panchanga

TITHI_NAMES = ["Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
               "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
               "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi",
               "Purnima/Amavasya"]
YOGA_NAMES = ["Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
              "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi",
              "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata",
              "Variyana", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha",
              "Shukla", "Brahma", "Indra", "Vaidhriti"]
KARANA_NAMES = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]


def panchanga(jd_ut):
    """-> dict with tithi, paksha, nitya yoga, karana.

    Vara (weekday) is NOT computed here because the Vedic day begins at
    sunrise, not midnight. A birth at 00:40 belongs to the PREVIOUS
    calendar day's vara. Compute sunrise separately and compare.
    """
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    su = swe.calc_ut(jd_ut, swe.SUN, flags)[0][0]
    mo = swe.calc_ut(jd_ut, swe.MOON, flags)[0][0]
    diff = (mo - su) % 360
    ti = int(diff // 12)
    kn = int(diff // 6)
    if kn == 0:
        karana = "Kimstughna"
    elif kn >= 57:
        karana = ["Shakuni", "Chatushpada", "Naga"][kn - 57]
    else:
        karana = KARANA_NAMES[(kn - 1) % 7]
    return {"elongation": diff,
            "tithi_num": ti + 1,
            "tithi": TITHI_NAMES[ti % 15],
            "paksha": "Shukla" if ti < 15 else "Krishna",
            "tithi_elapsed_pct": (diff % 12) / 12 * 100,
            "yoga": YOGA_NAMES[int(((su + mo) % 360) // (360 / 27))],
            "karana": karana}


def sunrise(jd_ut, lat, lon_east, alt=0):
    """Julian Day of the sunrise preceding or at jd_ut, for vara reckoning."""
    r = swe.rise_trans(jd_ut - 1, swe.SUN, swe.CALC_RISE, (lon_east, lat, alt), 0, 0)
    return r[1][0]


# ------------------------------------------------------- birth-time sanity

def lagna_sensitivity(jd_ut, lat, lon_east, minutes=(-30, -15, -5, 0, 5, 15, 30)):
    """MANDATORY before presenting any reading.

    Returns [(offset_minutes, asc_lon, sign_index)]. Report to the user
    how wide the birth-time window is that keeps the lagna in the same
    sign, and warn that divisional-chart lagnas move far faster - roughly
    4.3 arcminutes of ascendant per minute of clock time at mid latitudes.
    """
    out = []
    for m in minutes:
        a, _, _ = ascendant(jd_ut + m / 1440.0, lat, lon_east)
        out.append((m, a, sign_of(a)))
    return out


def ayanamsa_delta(jd_ut):
    """Raman vs Lahiri difference at a date, in degrees.

    Roughly 1 26' in the late 20th century. Rashi/nakshatra/lagna usually
    survive the switch; navamsa and pada assignments often do not. State
    which ayanamsa you used, every time.
    """
    swe.set_sid_mode(swe.SIDM_RAMAN, 0, 0)
    r = swe.get_ayanamsa_ut(jd_ut)
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    l = swe.get_ayanamsa_ut(jd_ut)
    swe.set_sid_mode(swe.SIDM_RAMAN, 0, 0)
    return {"raman": r, "lahiri": l, "delta": l - r}


# -------------------------------------------------------------- self-test

def _selftest():
    """Regression case: the J2000.0 epoch, 1 Jan 2000 12:00 UT, at Greenwich
    (51.4769N 0.0E), Lahiri ayanamsa. This is an astronomical reference
    moment, not anyone's birth chart.

    The Julian Day (2451545.0) is the standard J2000.0 value. The Sun's
    sidereal longitude matches the published apparent tropical longitude
    (~280.37 deg) minus the Lahiri ayanamsa. All other expected values are a
    regression snapshot produced by this engine with the Swiss Ephemeris
    .se1 files; they guard against unintended changes, and should be
    cross-checked against an independent jyotish program before being
    quoted as reference values.
    """
    setup(ayanamsa="lahiri")
    lat, lon_e = 51.4769, 0.0
    jd = julday(2000, 1, 1, 12, 0, 0, tz_offset=0)
    assert abs(jd - 2451545.0) < 1e-9, f"JD wrong: {jd}"
    ay = swe.get_ayanamsa_ut(jd)
    assert abs(ay - 23.857092) < 1e-3, f"Lahiri ayanamsa wrong: {ay}"
    pos = positions(jd)
    expect = {"Sun": 256.5157, "Moon": 199.4705, "Mars": 304.1101,
              "Mercury": 248.0361, "Jupiter": 1.3999, "Venus": 217.7126,
              "Saturn": 16.5424, "Rahu": 101.1874}
    for p, v in expect.items():
        got = pos[p]["lon"]
        assert abs(got - v) < 0.01, f"{p} {got:.4f} != {v}"
    assert pos["Saturn"]["retro"], "Saturn should be retrograde"
    asc, mc, _ = ascendant(jd, lat, lon_e)
    assert abs(asc - 0.4120) < 0.01, f"asc {asc}"
    assert sign_of(asc) == 0, "lagna should be Aries"
    ni, pada, lord = nakshatra_of(pos["Moon"]["lon"])
    assert (ni, pada, lord) == (14, 4, "Rahu"), f"Moon nakshatra {ni},{pada},{lord}"
    assert_bav_totals()
    psigns = {p: pos[p]["sign"] for p in
              ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]}
    bav, sav = ashtakavarga(psigns, sign_of(asc))
    assert sav == [27, 23, 23, 28, 31, 34, 29, 26, 29, 25, 37, 25], sav
    assert varga(pos["Moon"]["lon"], 9) == 11, "Moon navamsa should be Pisces"
    assert varga(asc, 9) == 0, "lagna navamsa should be Aries"
    lons = {p: pos[p]["lon"] for p in pos}
    forms, half, margin = check_kala_sarpa(lons)
    assert not forms, "Kala Sarpa should NOT form in this chart"
    comb = combustion(lons)
    assert comb["Mercury"][2], "Mercury should be combust"
    assert not comb["Venus"][2], "Venus should not be combust"
    ch = bhava_chalit(jd, lat, lon_e, lons)
    assert ch["Saturn"] == (1, 2), f"Saturn should shift 1->2, got {ch['Saturn']}"
    per = vimshottari(jd, pos["Moon"]["lon"], levels=2)
    stack = dasha_at(per, jd)
    assert stack[0]["lord"] == "Rahu" and stack[1]["lord"] == "Mars", \
        [s["lord"] for s in stack]
    pa = panchanga(jd)
    assert pa["tithi_num"] == 26 and pa["paksha"] == "Krishna", pa
    print("selftest: all checks passed")
    return True


# -------------------------------------------------------------------- CLI

def _cli(argv=None):
    """Print a chart summary for birth data supplied on the command line."""
    import argparse
    import datetime as dt

    ap = argparse.ArgumentParser(
        prog="jyotish.py",
        description="Compute a sidereal (Vedic) chart from birth data.")
    ap.add_argument("--selftest", action="store_true",
                    help="run the regression self-test and exit")
    ap.add_argument("--date", help="birth date, YYYY-MM-DD")
    ap.add_argument("--time", help="local birth time, HH:MM or HH:MM:SS")
    ap.add_argument("--tz", type=float,
                    help="UTC offset in hours at the birth date, including "
                         "daylight saving if it applied (India: 5.5)")
    ap.add_argument("--lat", type=float, help="latitude, north positive")
    ap.add_argument("--lon", type=float, help="longitude, east positive")
    ap.add_argument("--ayanamsa", default="lahiri",
                    choices=sorted(AYANAMSA_MODES))
    ap.add_argument("--node", default="mean", choices=["mean", "true"])
    ap.add_argument("--ephe", default="./ephe",
                    help="directory holding the Swiss Ephemeris .se1 files")
    ap.add_argument("--svg", help="write the chart to this SVG file")
    ap.add_argument("--varga", type=int, default=1, choices=SHODASHAVARGA,
                    help="divisional chart for --svg (default 1 = rasi)")
    ap.add_argument("--style", default="south", choices=["south", "north"],
                    help="chart style for --svg")
    a = ap.parse_args(argv)

    if a.selftest:
        return _selftest()

    missing = [f"--{k}" for k in ("date", "time", "tz", "lat", "lon")
               if getattr(a, k) is None]
    if missing:
        ap.error("birth data required: " + " ".join(missing))
    try:
        d = dt.date.fromisoformat(a.date)
        parts = [int(x) for x in a.time.split(":")]
        hh, mm, ss = (parts + [0])[:3]
        dt.time(hh, mm, ss)
    except ValueError as e:
        ap.error(f"bad --date or --time: {e}")
    if not -90 <= a.lat <= 90 or not -180 <= a.lon <= 180:
        ap.error("--lat must be -90..90 and --lon -180..180")
    if not -12 <= a.tz <= 14:
        ap.error("--tz must be between -12 and +14")

    setup(ephe_path=a.ephe, ayanamsa=a.ayanamsa)
    jd = julday(d.year, d.month, d.day, hh, mm, ss, tz_offset=a.tz)
    pos = positions(jd, node=a.node)
    lons = {p: pos[p]["lon"] for p in pos}
    asc, _, _ = ascendant(jd, a.lat, a.lon)

    print(f"Birth: {a.date} {a.time} (UTC{a.tz:+g}), "
          f"lat {a.lat}, lon {a.lon}")
    print(f"Ayanamsa: {a.ayanamsa} {dms(swe.get_ayanamsa_ut(jd))}   "
          f"Nodes: {a.node}   JD(UT): {jd:.6f}")
    ni, pada, _ = nakshatra_of(asc)
    print(f"\nLagna: {SIGNS[sign_of(asc)]} {dms(asc % 30)}  "
          f"{NAKSHATRAS[ni]} pada {pada}")

    comb = combustion(lons, {p: pos[p]["retro"] for p in pos})
    print(f"\n{'Planet':<8} {'Sign':<12} {'Degree':<12} "
          f"{'Nakshatra':<13} Pada  Notes")
    for p in PLANET_ORDER:
        v = pos[p]
        notes = []
        if v["retro"] and p not in ("Rahu", "Ketu"):
            notes.append("retrograde")
        if p in EXALTATION:
            notes += dignity(p, v["lon"])
        if p in comb and comb[p][2]:
            notes.append("combust")
        print(f"{p:<8} {SIGNS[v['sign']]:<12} {dms(v['deg']):<12} "
              f"{NAKSHATRAS[v['nak']]:<13} {v['pada']:<5} {', '.join(notes)}")

    pa = panchanga(jd)
    print(f"\nPanchanga: tithi {pa['tithi_num']} {pa['tithi']} "
          f"({pa['paksha']} paksha), yoga {pa['yoga']}, "
          f"karana {pa['karana']}")

    per = vimshottari(jd, pos["Moon"]["lon"], levels=2)
    birth = [s["lord"] for s in dasha_at(per, jd)]
    now = dt.datetime.now(dt.timezone.utc)
    jd_now = swe.julday(now.year, now.month, now.day,
                        now.hour + now.minute / 60.0)
    running = [s["lord"] for s in dasha_at(per, jd_now)]
    print(f"Vimshottari at birth: {'/'.join(birth)}; "
          f"running now: {'/'.join(running) or 'outside span'}")

    shifts = {p: h for p, h in bhava_chalit(jd, a.lat, a.lon, lons).items()
              if h[0] != h[1]}
    if shifts:
        print("Bhava chalit shifts (whole sign -> Sripati): " +
              ", ".join(f"{p} {w}->{b}" for p, (w, b) in shifts.items()))

    sens = lagna_sensitivity(jd, a.lat, a.lon)
    same = [m for m, _, s in sens if s == sign_of(asc)]
    print(f"Lagna sensitivity: sign unchanged for offsets "
          f"{min(same):+d} to {max(same):+d} min of those tested "
          f"({', '.join(f'{m:+d}' for m, _, _ in sens)})")

    if a.svg:
        from chart_svg import south_indian, north_indian, placement_from
        pm, lag = placement_from(lons, varga_fn=varga, division=a.varga,
                                 asc_lon=asc)
        render = south_indian if a.style == "south" else north_indian
        with open(a.svg, "w", encoding="utf-8") as f:
            f.write(render(pm, lag, use_css_vars=False))
        print(f"\nWrote D-{a.varga} {a.style} Indian chart to {a.svg}")
    return True


if __name__ == "__main__":
    _cli()
