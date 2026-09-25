# Writing the reading

The computation is astronomy. The interpretation is a tradition. Keep the
line between them visible in the writing itself, and the output is both more
useful and more honest.

---

## The framing that works

Attribute readings to the tradition rather than asserting them:

> "Ketu conjunct the Moon in the 10th is classically read as detachment from
> position — the texts describe recurring loss of interest rather than external
> removal."

Not:

> "You will lose interest in your job and quit."

This is not hedging. It is accurate: the first sentence is a true statement about
what the tradition says; the second is a claim about the future that nothing
supports. The tradition-attributed version also reads better — it gives the
person something to think with rather than something to worry about.

**Do not sprawl the disclaimers.** One clear statement at the end that astrology
has no demonstrated predictive validity under controlled testing, plus
tradition-attributed phrasing throughout, is enough. Repeating a caveat every
paragraph is its own kind of dishonesty — it signals you do not believe the
document you just spent effort producing.

## Lead with what was actually computed

Open with the hard facts: rashi, nakshatra and pada, lagna, and whatever the
person specifically asked for. Then the structural findings. Then the reading.

Say explicitly that the positions are checkable against any ephemeris. That is
what distinguishes this from the generated horoscope text the person has
probably seen before, and it is worth one sentence.

## Correct the false positives out loud

If the chart does *not* have Kala Sarpa, or does *not* form Ruchaka, **say so and
show the margin**. People arrive having read otherwise from software or a
website, and this is one of the few places where the work delivers something
verifiable and immediately useful.

> "There is no Kala Sarpa Yoga here. The Moon falls 1°35′ outside the nodal axis.
> Close, but the condition is not met."

Same for Sade Sati, which gets claimed constantly when Ashtama Shani or Kantaka
Shani is what is actually running.

## Do not smooth over contradictions

The interesting structure in most charts *is* the contradiction. A raja yoga
formed by the same conjunction that combusts one of its participants. A house
crowded with planets and starved of bindus. A dignified planet that fails the
kendra requirement. Write these as the tension they are — that is the analysis.
A reading with no tension in it is a reading that was not done.

---

## Domain → house map

Use both the natal house and its lord's placement, and check the relevant
divisional chart.

| Domain | Houses | Also check |
|---|---|---|
| Health, vitality | 1, 6, 8 | lagna lord; 6/8/12 lords; Sun and Moon; D-30 |
| Wealth (accumulated) | 2, 11 | 2nd and 11th lords; Jupiter and Venus; D-2 |
| Finance (flow) | 2, 6, 11, 12 | 11th vs 12th balance; Venus, Mercury; D-2 |
| Family, household | 2, 4, 7 | 4th lord; Moon for mother; Venus for spouse; D-12 |
| Mother | 4 | Moon; Matrikaraka; D-12, D-40 |
| Father | 9 | Sun; Pitrikaraka; D-12, D-45 |
| Spouse, marriage | 7 | 7th lord; Venus; Darakaraka; **D-9** |
| Children | 5 | 5th lord; Jupiter; Putrakaraka; **D-7** |
| Career, profession | 10, 6, 3 | 10th lord; Amatyakaraka; **D-10** |
| Education | 4, 5, 9 | Mercury and Jupiter; **D-24** |
| Property, land, home | 4 | 4th lord; Mars; **D-4**, D-16 |
| Foreign residence, loss | 12 | 12th lord; Saturn, Ketu, Rahu |
| Spiritual life | 9, 12 | Ketu; Atmakaraka; **D-20** |

---

## Life-outcome questions

"Will I lose my job?" "When will I marry?" "Is my health at risk?" "Will I be
rich?"

These are the questions people actually come with. Handle them like this:

**1. Say plainly what the technique cannot do.** There is no validated method for
predicting a discrete life event from a birth chart. The tradition has
combinations it associates with a domain, but those same combinations get read
after the fact as any of several outcomes — resigned, dismissed, restructured,
stayed and was unhappy. Nothing separates them beforehand. Say this first, and
say it without apology.

**2. Then give the actual analysis anyway.** Refusing to engage is not honest —
it is just unhelpful. Describe what the chart contains, what the tradition says
about it, and where the relevant periods cluster. The person asked a real
question and deserves a real answer about what their chart holds.

**3. Distinguish structural from temporal.** A natal configuration is a lifelong
disposition, not an upcoming event. If the Moon–Ketu contact in the 10th is
present at birth, it has been operating the whole time — it does not "happen" in
2027. Say that. It reframes the question usefully and it is true.

**4. Report the counterweights.** If a difficult stretch has a supportive transit
running through it, say so in the same breath. Selective emphasis on the adverse
is the commonest failure mode of astrological writing and it does real harm.

**5. Redirect to the real signal.** If someone is asking about job loss, something
in their actual life probably prompted it. Say that the real-world indicators —
the reorg, the quiet manager, the funding round — matter more than any transit,
and offer to help with that instead. This is usually the most useful sentence in
the whole response.

**Health specifically:** stay at the level of the tradition's general readings.
Never name a condition, never imply a diagnosis, never suggest delaying or
changing treatment. If a chart period looks difficult, the correct advice is
"see a doctor for ordinary reasons," not "because of a transit." Do not produce
content that could lead someone to defer care.

**Finance specifically:** not investment advice. Ashtama Shani is not a basis for
a portfolio decision, and should never be presented as one.

**Death, terminal illness, and harm to named others:** do not time these. Not
under any framing — not as *ayurdaya*, not as a Maraka period, not "what the
texts say", not for a third party. Decline the timing and offer the rest of the
reading. This is a firm line, not a preference.

---

## What to ask the person for

Ask once, near the end, and make it specific to what would change:

- **Birth-time provenance.** Hospital record or family recollection? Everything
  below D-9 depends on the answer.
- **The concrete situation**, if the question is domain-specific. A career
  reading is generic without knowing whether they are salaried, self-employed,
  or between roles.
- **Family structure**, if the 4th/5th/7th carry the traffic.
- **Location now**, if 12th-house or foreign-residence indications are live.

And offer the **backward test**: run the same method over years they have already
lived. It costs nothing, it is the only real check available on whether the
technique is telling them anything, and offering it unprompted is a signal of
good faith that most astrological writing never gives.

---

## Output format

- Substantial work (full horoscope, monthly gochara) → a **self-contained HTML
  file** with charts as inline SVG, presented via `present_files`.
- Chat response → headline facts, the direct answer to what was asked, the
  corrections to any false positives, and the caveats. Not a re-run of the file.
- Charts: **South Indian** for South Indian users and whenever asked; North
  Indian otherwise or on request. Ask if unclear — it is a one-word question.
- Give exact degrees in DMS and the decimal longitude. Show your arithmetic;
  it is the part that can be checked.
