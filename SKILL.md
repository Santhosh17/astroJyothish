---
name: vedic-astrology
description: Use this skill for any Vedic astrology (jyotish) request - casting a natal chart or horoscope (kundali, jataka, janma patrika), computing rashi, nakshatra, lagna, divisional charts (navamsa, dasamsa, D-1 through D-60), Vimshottari dasha periods, ashtakavarga, yogas, Jaimini karakas, panchanga, or transit/gochara analysis including Sade Sati, Ashtama Shani and monthly forecasts. Also use when asked to interpret an existing chart, check a claimed yoga, compare ayanamsas, or answer questions like "when will I get married / lose my job / recover financially" from a birth chart. Triggers on birth-data-plus-question of any form, and on terms like jyotish, kundali, horoscope, rashi, nakshatra, lagna, dasha, gochara, muhurta, ayanamsa, navamsa, panchanga. Do NOT use for Western tropical astrology, sun-sign columns, or tarot.
---

# Vedic Astrology (Jyotish)

## What this skill is for

Producing **arithmetically correct** jyotish computations and **honestly framed**
interpretations. The two halves matter equally. Most bad astrology output fails
on one of them: either the numbers are wrong (pattern-matched from training data
instead of computed), or the numbers are right and the framing overclaims.

Read `REFERENCE.md` for the full technique tables. Read `INTERPRETATION.md`
before writing any interpretive prose, and always before answering a question
about a life outcome (job, marriage, health, death, money).

## Non-negotiable rules

1. **Never state a planetary position from memory.** Compute it. Every time.
   Recalled positions are wrong often enough that a single unchecked figure
   discredits the whole reading.
2. **Always name the ayanamsa** in the output. Raman and Lahiri differ by about
   1°27′ in the late 20th century, which is enough to move padas and most
   divisional-chart lagnas.
3. **Always run the birth-time sensitivity check** and report it.
4. **Verify the full classical condition** for any yoga before naming it. See
   the false-positive list below.
5. **Never present a life-outcome prediction as a fact.** See `INTERPRETATION.md`.

## Setup

```bash
pip install pyswisseph --break-system-packages
mkdir -p ephe && cd ephe
for f in sepl_18.se1 semo_18.se1 seas_18.se1; do
  curl -sL -o $f "https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/$f"
done
```

Without the `.se1` files pyswisseph falls back to the Moshier ephemeris — still
about 1 arcsecond, fine for jyotish, but download them when the network allows.

Then, before trusting anything:

```bash
python3 scripts/jyotish.py --selftest
```

For a quick summary from the command line (all birth fields are required):

```bash
python3 scripts/jyotish.py --date YYYY-MM-DD --time HH:MM --tz 5.5 \
    --lat 12.97 --lon 77.59 --ayanamsa lahiri --svg chart.svg
```

The self-test is a full regression against a known chart. If it fails, stop and
fix the engine; do not produce a reading.

## Workflow

### 1. Gather and verify the inputs

You need **date, time, place**. Then:

- **Time zone.** India is UTC+5:30 with **no daylight saving since 1945** — never
  apply DST to an Indian birth. For other countries look up the historical DST
  rule for that exact date, not the current one.
- **Coordinates.** Web-search the birthplace rather than recalling coordinates.
  Report the source spread; a few km is immaterial for the ascendant but say so
  rather than implying false precision.
- **Ayanamsa.** Ask, or default to Lahiri (the Indian government standard) and
  say so. Use Raman if the person asks for it or is working in that lineage.
- **Chart style.** South Indian for South Indian users (Karnataka, Tamil Nadu,
  Andhra, Telangana, Kerala) and whenever asked. North Indian otherwise, or when
  requested. When in doubt, ask — it is a one-word question.

### 2. Compute

```python
import sys; sys.path.insert(0, "scripts")
import jyotish as jy

jy.setup(ephe_path="ephe", ayanamsa="raman")
# Replace with the person's birth data: local date and time, the UTC offset
# in force on that date, and the birthplace's latitude / east longitude.
jd  = jy.julday(YEAR, MONTH, DAY, HOUR, MINUTE, 0, tz_offset=TZ_OFFSET)
pos = jy.positions(jd)                       # mean node by default
asc, mc, cusps = jy.ascendant(jd, LATITUDE, LONGITUDE_EAST)
```

Then, in this order — each step can invalidate the previous one's reading:

| Step | Call | Why it matters |
|---|---|---|
| Dignities | `jy.dignity(p, lon)` | exalted / debilitated / own / moolatrikona |
| **Combustion** | `jy.combustion(lons)` | a combust benefic guts every yoga it forms |
| **Bhava chalit** | `jy.bhava_chalit(...)` | a planet near a sandhi changes house |
| Vargas | `jy.varga(lon, 9)` | D-9 and D-10 at minimum |
| Vargottama | `jy.vargottama(lons)` | its absence is itself a finding |
| Ashtakavarga | `jy.ashtakavarga(...)` | separates nominal from real strength |
| Vimshottari | `jy.vimshottari(...)` | the timing layer |
| Karakas | `jy.chara_karakas(...)` | Jaimini overlay |
| Panchanga | `jy.panchanga(jd)` | tithi, yoga, karana |
| **Sensitivity** | `jy.lagna_sensitivity(...)` | how much of this survives a wrong minute |

### 3. Check the four classic false positives

These are wrong in most software output and in most of what is written online.
Check every one before naming any yoga:

- **Pancha-Mahapurusha** (Ruchaka, Bhadra, Hamsa, Malavya, Sasa) needs the planet
  dignified **AND in a kendra** from lagna or Moon. Dignity alone is not enough.
  `jy.check_mahapurusha()`
- **Kala Sarpa** needs **all seven** grahas strictly inside one nodal semicircle.
  Report the margin — "misses by 1°35′" is a real and useful answer.
  `jy.check_kala_sarpa()`
- **Kemadruma** almost always has a **bhanga** (cancellation). Naming the yoga
  without the cancellation is scaremongering. `jy.check_kemadruma()`
- **Gaja Kesari / any Jupiter yoga** must be discounted if Jupiter is combust.
  `jy.check_gaja_kesari()` returns the combustion flag alongside.

### 4. Render charts

```python
from chart_svg import south_indian, placement_from
pm, lag = placement_from({p: pos[p]["lon"] for p in pos},
                         varga_fn=jy.varga, division=9, asc_lon=asc)
svg = south_indian(pm, lag)
```

For a Chandra-lagna chart, pass the Moon's sign as `lagna_sign` and keep `"Asc"`
in the true ascendant's box.

### 5. Deliver

Substantial charts (a full horoscope, a monthly gochara run) are **files**, not
chat messages — a self-contained HTML document with the charts as inline SVG.
Put the headline facts (rashi, nakshatra, lagna) in the chat response, plus
anything the person specifically asked, plus the caveats. See `INTERPRETATION.md`
for what the caveats must cover.

## Gochara (transit) work

Reckon from the **natal Moon**, not the ascendant — that is what classical
gochara means. Report both: house-from-Moon governs the favourable/unfavourable
judgement, house-from-lagna tells you which area of life it lands in.

The bindu count is what separates a nominally good transit from a real one. A
planet transiting a sign where it holds 1 of 8 bindus in that chart is weak there
regardless of which house it occupies.

Compute exact dates by bisection — `find_ingresses`, `find_stations`,
`find_conjunctions`, `chandrashtama`. Never quote a transit date from memory.

**Sade Sati is not Ashtama Shani.** Sade Sati is Saturn in the 12th, 1st or 2nd
from the natal Moon (~7.5 years). Ashtama Shani is the 8th. Kantaka is the 4th.
`jy.sade_sati_state()` returns which, if any. People conflate these constantly;
state plainly which one is actually running.

Mean vs true node: Indian convention is **mean**. Ingress dates differ by weeks
between the two. Say which you used.

Vedha (obstruction) tables vary between texts. `REFERENCE.md` explains why this
skill does not apply them. Say so rather than presenting an unobstructed reading
as a complete one.

## Things that are commonly got wrong

| Trap | The right answer |
|---|---|
| Vara (weekday) for a post-midnight birth | The Vedic day starts at **sunrise**. A 00:40 birth belongs to the previous day's vara. Compute sunrise. |
| Ashtakavarga totals | Must be 48/49/39/54/56/52/39, grand total **337**. If you get 336, the Venus-from-Lagna row is missing the 11. |
| Whole sign vs cusps | Report both when a planet shifts. Do not silently pick one. |
| "No planet is vargottama" | This is a finding, not an absence of one. Say it. |
| Tropical vs sidereal | Jyotish is sidereal. If a position looks a sign off, you forgot `FLG_SIDEREAL`. |
| Retrograde nodes | Rahu and Ketu are always retrograde. Not a finding. |
| Gandanta | Real, but weight it heavily only for the Moon and the lagna. |

## Scope and tested limits

The engine takes arbitrary date, time, place and ayanamsa. Nothing is
hardcoded to a particular chart except the self-test fixture, which exists
precisely so it has known values to assert against.

Verified working: southern hemisphere, west longitudes, arctic latitude
(Tromsø 69.6°N, Longyearbyen 78.2°N), pre-1900 births, and all four
supported ayanamsas. The ashtakavarga checksum holds at 337 throughout.

Three things the caller has to get right, because the engine cannot:

- **Daylight saving.** `tz_offset` is a manual number; there is no timezone
  database. A Chicago birth in July 1985 is UTC−5 (CDT), not −6, and getting
  it wrong moves the lagna a full sign. Look up the historical DST rule for
  that exact date and place. India never needs this; most other countries do.
- **Vimshottari span.** `span_years` is measured from birth, defaulting to
  150. A 19th-century chart needs more. `dasha_at()` returning an empty list
  means the span is too short, not that the chart is odd.
- **House system above 66° latitude.** Placidus and Koch are undefined there
  and swisseph raises. Whole sign and Porphyry work everywhere, and whole
  sign is the jyotish default, so this rarely bites.

Not implemented, by choice — say so rather than improvising: shadbala,
gochara vedha tables, Ashtottari/Yogini/Chara/Kalachakra dashas, Ashtakoot
compatibility matching, muhurta, prashna, ashtakavarga kaksha, and Rahu kaal
and the other panchanga inauspicious periods. `REFERENCE.md` §10 has the list
and the reasoning.

## Files

- `REFERENCE.md` — full technique tables: vargas, ashtakavarga, dasha, gochara,
  dignities, yoga conditions, panchanga, and what this skill deliberately omits.
- `INTERPRETATION.md` — how to write readings, the domain-to-house map, and the
  rules for life-outcome questions. **Read before writing prose.**
- `scripts/jyotish.py` — computation engine with checksum-validated tables and a
  regression self-test.
- `scripts/chart_svg.py` — South Indian and North Indian chart renderers.
