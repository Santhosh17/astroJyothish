# Jyotish technique reference

All tables here are implemented in `scripts/jyotish.py`. This file explains
*why* each one is the way it is, so that a future run does not "correct" a
correct table into a wrong one.

---

## 1. Ayanamsa

Swiss Ephemeris sidereal mode numbers:

| Ayanamsa | Mode | Notes |
|---|---|---|
| Lahiri / Chitrapaksha | 1 | Indian government standard. Default when unspecified. |
| Raman (B.V. Raman) | 3 | ≈ Lahiri − 1°27′ in the late 20th century. |
| Krishnamurti (KP) | 5 | For KP work only. |
| Fagan–Bradley | 0 | Western sidereal. Rarely wanted in jyotish. |

Worked example — J2000.0 (1 Jan 2000, 12:00 UT): Raman 22°24′39″, Lahiri 23°51′26″, delta 1°26′47″.

What survives an ayanamsa switch, in practice: rashi, nakshatra and lagna
usually do. What often does not: nakshatra pada, navamsa positions, and most
divisional-chart lagnas. **Always name the ayanamsa in the output.**

---

## 2. Houses

Jyotish default is **whole sign** (rashi = bhava): the whole of the rising sign
is the 1st house, the next sign the 2nd, and so on.

The Sripati system (equivalent to Porphyry, `hsys=b'O'`) divides each quadrant
into three; the bhava *madhya* is the cusp and the bhava *sandhi* is the midpoint
between consecutive madhyas. A planet past a sandhi belongs to the next bhava.

**Always run `bhava_chalit()` and report any shift.** A planet a few degrees from
a sandhi is 12th-house by whole sign and 1st-house by cusp, which is not a
technical footnote — it can be the single largest interpretive fact in a chart.
Present both and let the person know the reading is system-dependent.

---

## 3. Divisional charts (shodashavarga)

`varga(lon, division)` implements all sixteen. Definitions of the ones people
get wrong:

- **D-9 Navamsa** — `(sign * 9 + part) % 12`, `part = int(deg / 3°20′)`.
  Check: Aries 0° → Aries; Taurus 0° → Capricorn; Gemini 0° → Libra;
  Cancer 0° → Cancer. If your D-9 fails these four, the formula is wrong.
- **D-10 Dasamsa** — odd signs count from the same sign, **even signs from the
  9th**. Dropping the even-sign offset is the usual bug.
- **D-7 Saptamsa** — odd from the same sign, even from the 7th.
- **D-30 Trimsamsa** — not equal parts. Odd signs: 0–5 Mars, 5–10 Saturn,
  10–18 Jupiter, 18–25 Mercury, 25–30 Venus. Even signs reverse the order:
  0–5 Venus, 5–12 Mercury, 12–20 Jupiter, 20–25 Saturn, 25–30 Mars.
- **D-16, D-20, D-45** start from Aries/Leo/Sagittarius for movable/fixed/dual
  signs — but **D-20 uses a different rotation** (movable Aries, fixed
  Sagittarius, dual Leo). Do not assume they share one rule.
- **D-27 Bhamsa** — starts from Aries/Cancer/Libra/Capricorn by element
  (fire/earth/air/water).

Signification: D-1 body and life, D-2 wealth, D-3 siblings, D-4 property,
D-7 children, D-9 spouse and dharma, D-10 career, D-12 parents, D-16 comforts,
D-20 spiritual practice, D-24 education, D-27 strengths, D-30 adversity,
D-40 maternal legacy, D-45 paternal legacy, D-60 carried-forward karma.

**Vargottama** = same sign in D-1 and D-9. Its total absence across a chart is a
finding worth stating, not a blank to skip past.

**Divisional charts are birth-time sensitive.** The ascendant moves roughly
4.3 arcminutes per minute of clock time at mid latitudes, so a D-60 lagna needs
the birth time accurate to seconds to mean anything. Say this rather than
presenting D-60 with false confidence.

---

## 4. Ashtakavarga

Bhinnashtakavarga counts benefic points contributed to each sign by each of the
seven grahas plus the lagna.

**Row totals must be:** Sun 48, Moon 49, Mars 39, Mercury 54, Jupiter 56,
Venus 52, Saturn 39. **Grand total 337.** `assert_bav_totals()` enforces this and
runs automatically inside `ashtakavarga()`.

> **The one row people mistype:** Venus-from-Lagna is `[1,2,3,4,5,8,9,11]` —
> eight places. Many sources drop the 11, giving Venus a total of 51 and a grand
> total of 336. If your checksum reads 336, that is where it is.

Reading it:

- **SAV per sign** 28+ is strong, 25 or under is weak, 30+ is notably strong.
- **BAV of the transiting planet in the transited sign** is the transit strength
  filter. A planet with 1–2 bindus in a sign is weak there no matter how good the
  house looks. This is the single most useful thing ashtakavarga does.
- A house crowded with planets but low in bindus means *activity without support* —
  a genuinely useful and non-obvious observation.

Kaksha (each sign split into 8 sub-divisions of 3°45′, assigned Saturn, Mars,
Jupiter, Sun, Venus, Mercury, Moon, Lagna) refines Saturn transits further. Not
implemented here; add it if a request needs that resolution.

---

## 5. Vimshottari dasha

120-year cycle. Order and lengths: Ketu 7, Venus 20, Sun 6, Moon 10, Mars 7,
Rahu 18, Jupiter 16, Saturn 19, Mercury 17.

Starting lord = lord of the Moon's birth nakshatra (`nakshatra_index % 9` into
the order above). Balance at birth = `(1 − elapsed_fraction) × lord_years`.

Year length: **365.2425 days**. Some traditions use 360-day years, which shifts
long-range dates by months — if reconciling with someone else's chart, this is
usually the discrepancy.

Sub-periods nest proportionally: `sub_duration = parent_duration × sub_years/120`.
Level 1 mahadasha, 2 antardasha, 3 pratyantardasha, 4 sookshma, 5 prana.
Three levels is the useful depth for most work; go to four only for a specific
dated question.

Other dasha systems (Ashtottari, Yogini, Chara/Jaimini, Kalachakra) are not
implemented. Say so if asked rather than improvising one.

---

## 6. Dignities, combustion, aspects

**Exaltation** (sign, degree): Sun Aries 10°, Moon Taurus 3°, Mars Capricorn 28°,
Mercury Virgo 15°, Jupiter Cancer 5°, Venus Pisces 27°, Saturn Libra 20°.
Debilitation is the opposite sign.

**Combustion (asta)** — orbs from the Sun, direct motion:
Moon 12°, Mars 17°, Mercury 14°, Jupiter 11°, Venus 10°, Saturn 15°.
Retrograde: Mercury 12°, Venus 8°.

A combust planet is functionally burnt. **This is the most under-applied factor
in automated chart output.** A combust lagna lord in its own sign is not simply
a strong lagna lord. Check combustion before naming any yoga the planet forms.

**Graha drishti** — everything aspects the 7th. Additionally: Mars the 4th and
8th, Jupiter the 5th and 9th, Saturn the 3rd and 10th, and the nodes the 5th,
7th and 9th (node aspects are accepted by some authorities and not others — say
which convention you are using if it matters to the reading).

**Gandanta** — the water-to-fire junctions: last 3°20′ of Cancer, Scorpio, Pisces
and first 3°20′ of Leo, Sagittarius, Aries. Weight heavily for the Moon and the
lagna; note but do not over-read for other planets.

---

## 7. Yoga conditions in full

The recurring failure is checking half a condition. Each of these needs all of it:

**Pancha-Mahapurusha** (Ruchaka Mars, Bhadra Mercury, Hamsa Jupiter,
Malavya Venus, Sasa Saturn): the planet must be in its **own sign or exalted**
*and* **in a kendra (1/4/7/10) from the lagna or from the Moon**. Own sign in the
5th does not form it. Combustion severely diminishes any that does form.

**Kala Sarpa**: **all seven** grahas strictly within one Rahu–Ketu semicircle.
One planet a degree outside breaks it. Report the margin — most charts labelled
Kala Sarpa online are near-misses, and telling someone their chart misses by
1°35′ is far more useful than repeating the label.

**Kemadruma**: no planet (excluding the nodes and the Sun) in the 2nd, 12th or
same sign as the Moon. Standard cancellations: the Moon in a kendra from the
lagna; a benefic in a kendra from the Moon; the Moon conjunct or aspected by a
benefic. **Almost every Kemadruma chart has a bhanga.** Naming the yoga without
the cancellation is scaremongering, not analysis.

**Gaja Kesari**: Jupiter in a kendra from the Moon. Always report Jupiter's
combustion status alongside.

**Raja yoga**: a kendra lord and a trikona lord (1/5/9) conjunct, in mutual
aspect, or in mutual sign exchange. Note when the same conjunction that forms it
also damages it — e.g. a 9th-lord Sun forming a raja yoga with the lagna lord
while simultaneously combusting it. That tension is the interesting part of the
reading, not a detail to smooth over.

**Vipreeta Raja yoga**: Harsha = 6th lord in 6/8/12; Sarala = 8th lord in 6/8/12;
Vimala = 12th lord in 6/8/12.

**Neecha Bhanga**: cancellation of debilitation. Conditions vary widely between
texts. If you apply it, name which condition you used.

---

## 8. Gochara

Reckoned **from the natal Moon** (Janma Rashi). Favourable houses:

| Planet | Favourable houses from the Moon |
|---|---|
| Sun | 3, 6, 10, 11 |
| Moon | 1, 3, 6, 7, 10, 11 |
| Mars | 3, 6, 11 |
| Mercury | 2, 4, 6, 8, 10, 11 |
| Jupiter | 2, 5, 7, 9, 11 |
| Venus | 1, 2, 3, 4, 5, 8, 9, 11, 12 |
| Saturn | 3, 6, 11 |
| Rahu, Ketu | 3, 6, 11 |

Always report the house from the **lagna** too — it tells you *which area of life*
the transit lands in, which the Moon reckoning does not.

**Saturn states relative to the natal Moon:**

| Saturn's house from the Moon | Name | Duration |
|---|---|---|
| 12, 1, 2 | Sade Sati | ~7.5 years |
| 4 | Kantaka / Ardhashtama Shani | ~2.5 years |
| 8 | Ashtama Shani | ~2.5 years |

These are routinely conflated. State which is actually running, and state
plainly when none is.

**Vedha (obstruction):** a planet occupying a paired house cancels another's
transit effect. **This skill deliberately does not apply vedha**, because the
tables differ materially between Brihat Samhita and later commentaries and there
is no version I can present as authoritative. Say this to the user rather than
implying the reading is complete without it.

**Chandrashtama** — the Moon transiting the 8th from the natal Moon, 2–3 days a
month. Cheap to compute (`chandrashtama()`) and one of the more genuinely useful
short-term markers.

**Eclipses** — compute with `swe.sol_eclipse_when_glob` / `lun_eclipse_when` and
convert to the sidereal sign. An eclipse within a degree or two of a natal point
is worth flagging. Note that these functions give *global* maxima; local
visibility is a separate computation, and traditions differ on whether an
invisible eclipse counts.

---

## 9. Panchanga

- **Tithi** = `(Moon − Sun) / 12°`, 1–30. Shukla paksha 1–15, Krishna 16–30.
- **Nitya yoga** = `(Moon + Sun) / 13°20′`, 27 named yogas.
- **Karana** = half a tithi, 60 per lunar month. First is Kimstughna, last three
  are Shakuni, Chatushpada, Naga; the middle 56 cycle the seven movable karanas.
- **Vara** = weekday, **beginning at sunrise, not midnight**. A birth at 00:40 on
  a Tuesday has Monday's vara. Compute sunrise (`sunrise()`) and compare.

---

## 10. Deliberately not implemented

Say so plainly if asked, rather than improvising:

- Shadbala and its six components (a real computation, not a difficult one — add
  it properly if a request needs it, do not approximate)
- Vedha tables for gochara (see above)
- Ashtottari, Yogini, Chara, Kalachakra dashas
- Ashtakoot / Guna Milan compatibility matching
- Muhurta election
- Prashna (horary)
- Kaksha subdivision of ashtakavarga
- Panchanga-based inauspicious periods (Rahu kaal, Yamaganda, Gulika kaal)
