# vedic-astrology

A sidereal (Vedic) astrology computation engine built on the Swiss Ephemeris, packaged as a Claude skill. It can also be used on its own as a Python module or from the command line.

The project exists because language models asked for a horoscope tend to recall planetary positions from training data instead of computing them, and those recalled positions are often wrong. The skill instructs Claude to compute every position with this engine, name the ayanamsa it used, check how sensitive the chart is to birth-time error, and verify the full classical condition of a yoga before naming it.

## What it computes

The engine (`scripts/jyotish.py`) takes a date, local time, UTC offset, latitude and longitude, and computes:

- planetary positions for the nine grahas, with sign, degree, nakshatra, pada and retrograde status, using mean or true nodes
- the ascendant, with whole-sign houses by default and Sripati (Porphyry) bhava chalit to show planets that change house between the two systems
- all sixteen shodashavarga divisional charts, D-1 through D-60, and vargottama planets
- dignities (exaltation, debilitation, moolatrikona, own sign, natural friendship) and combustion, with the smaller retrograde orbs for Mercury and Venus
- bhinnashtakavarga and sarvashtakavarga, with the tables checked against the standard row totals (48, 49, 39, 54, 56, 52, 39; grand total 337) on every call
- Vimshottari dasha to any depth, and the dasha stack active at a given moment
- Jaimini chara karakas, gandanta, panchanga (tithi, nitya yoga, karana) and sunrise for vara
- checks for Pancha-Mahapurusha yogas, Kala Sarpa (with the margin by which it forms or fails), Kemadruma with its cancellations, and Gaja Kesari with Jupiter's combustion status
- transit tools: sign ingresses, retrograde stations, conjunctions with natal points, chandrashtama periods, and the Sade Sati / Ashtama Shani / Kantaka state
- lagna sensitivity: the ascendant recomputed at offsets from -30 to +30 minutes

Supported ayanamsas are Lahiri, Raman, Krishnamurti and Fagan-Bradley.

`scripts/chart_svg.py` renders South Indian and North Indian charts as SVG.

Shadbala, vedha tables, dasha systems other than Vimshottari, compatibility matching, muhurta and prashna are not implemented. `REFERENCE.md` section 10 gives the reasons.

## Setup

Tested with Python 3.12 and pyswisseph 2.10.

```bash
git clone <your-repo-url> vedic-astrology
cd vedic-astrology
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
sh scripts/fetch_ephemeris.sh
python3 scripts/jyotish.py --selftest
```

`fetch_ephemeris.sh` downloads the Swiss Ephemeris data files for 1800 to 2400 CE into `ephe/`. Without them pyswisseph falls back to the Moshier ephemeris, which is accurate to about one arcsecond. The self-test passes with either.

## Command line

All birth fields are required; nothing defaults to a particular place or time zone.

```bash
python3 scripts/jyotish.py \
  --date 1995-08-15 --time 06:30 --tz 5.5 \
  --lat 12.97 --lon 77.59 \
  --ayanamsa lahiri --svg chart.svg
```

This prints the lagna, a table of planets with sign, degree, nakshatra, pada, dignity and combustion, the panchanga, the Vimshottari periods at birth and today, any bhava chalit shifts, and the lagna sensitivity window. `--svg` writes a chart; add `--varga 9` for the navamsa or `--style north` for a North Indian chart. Run `python3 scripts/jyotish.py --help` for all options.

`--tz` is the UTC offset in force at the birth date and place, including daylight saving if it applied. The engine has no time zone database. India has used +5.5 with no daylight saving since 1945; most other countries need the historical rule for the exact date. A July 1985 birth in Chicago is -5 (CDT), not -6, and getting this wrong moves the ascendant by a full sign.

## Python

```python
import sys; sys.path.insert(0, "scripts")
import jyotish as jy

jy.setup(ephe_path="ephe", ayanamsa="lahiri")
jd = jy.julday(1995, 8, 15, 6, 30, 0, tz_offset=5.5)
pos = jy.positions(jd)
asc, mc, cusps = jy.ascendant(jd, 12.97, 77.59)

print(jy.SIGNS[jy.sign_of(asc)], jy.dms(asc % 30))
print(jy.varga(pos["Moon"]["lon"], 9))           # Moon's navamsa sign index
print(jy.dasha_at(jy.vimshottari(jd, pos["Moon"]["lon"]), jd))
```

`setup()` defaults to the Raman ayanamsa. Pass `ayanamsa` explicitly so the choice is visible in your code.

## Using it as a Claude skill

`SKILL.md` tells Claude how to gather and check birth data, which functions to call in which order, and which common errors to check for. `INTERPRETATION.md` covers how to write a reading, including how to frame questions about life outcomes. `REFERENCE.md` holds the technique tables.

To install, zip the project folder (the zip must contain the `vedic-astrology/` folder with `SKILL.md` inside it) and upload it as a custom skill in Claude:

```bash
cd ..
zip -r vedic-astrology.zip vedic-astrology \
  -x "vedic-astrology/.git/*" "vedic-astrology/.venv/*" "vedic-astrology/ephe/*"
```

## Tests

```bash
pip install pytest
pytest -q
```

The suite runs the self-test and checks ashtakavarga totals, nakshatra boundaries, navamsa rules, the 120-year Vimshottari cycle and the command-line input validation. GitHub Actions runs it on every push (`.github/workflows/tests.yml`).

The self-test fixture is the J2000.0 epoch (1 January 2000, 12:00 UT) at Greenwich, not a real person's chart. Its Julian Day and the Sun's position match published astronomical values. The other expected values are a snapshot of this engine's output: they catch unintended changes, but they have not been checked against an independent jyotish program.

## Limits the caller has to handle

- Daylight saving and historical time zones, as described under Command line.
- Vimshottari periods are generated for 150 years from birth by default. For older charts pass a larger `span_years`; an empty result from `dasha_at()` means the span is too short.
- Placidus and Koch houses are undefined above about 66 degrees latitude and swisseph raises an error there. Whole sign and Porphyry work at every latitude.

## Project layout

```
SKILL.md                 instructions Claude reads when the skill triggers
REFERENCE.md             technique tables
INTERPRETATION.md        rules for writing readings
scripts/jyotish.py       computation engine and command-line interface
scripts/chart_svg.py     South and North Indian chart renderers
scripts/fetch_ephemeris.sh
tests/test_jyotish.py
requirements.txt
```

## Acknowledgements

Planetary positions come from the Swiss Ephemeris by Astrodienst, through the pyswisseph Python bindings.

Astrological interpretation is a tradition, not a scientific prediction. The engine computes positions; `INTERPRETATION.md` explains how the skill keeps that distinction visible in its readings.
