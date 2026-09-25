import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import jyotish as jy  # noqa: E402

EPHE = os.path.join(ROOT, "ephe")


@pytest.fixture(autouse=True)
def lahiri():
    jy.setup(ephe_path=EPHE, ayanamsa="lahiri")


def test_selftest_passes(monkeypatch):
    monkeypatch.chdir(ROOT)
    assert jy._selftest()


def test_ashtakavarga_tables_total_337():
    assert jy.assert_bav_totals()


@pytest.mark.parametrize("signs", [
    {p: 0 for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]},
    {"Sun": 3, "Moon": 7, "Mars": 11, "Mercury": 2, "Jupiter": 5, "Venus": 9, "Saturn": 1},
])
def test_sarvashtakavarga_always_sums_to_337(signs):
    _, sav = jy.ashtakavarga(signs, asc_sign=4)
    assert sum(sav) == 337


@pytest.mark.parametrize("lon, expected", [
    (0.0, (0, 1, "Ketu")),                 # start of Ashwini
    (360 / 27 - 1e-9, (0, 4, "Ketu")),     # last pada of Ashwini
    (360 / 27, (1, 1, "Venus")),           # start of Bharani
    (360 - 1e-9, (26, 4, "Mercury")),      # end of Revati
])
def test_nakshatra_boundaries(lon, expected):
    assert jy.nakshatra_of(lon) == expected


@pytest.mark.parametrize("lon, sign", [
    (0.0, 0),        # 0 Aries -> Aries navamsa
    (3.34, 1),       # second navamsa of Aries -> Taurus
    (90.0, 3),       # 0 Cancer -> Cancer (movable sign starts from itself)
    (30.0, 9),       # 0 Taurus -> Capricorn (fixed sign: 9th from itself)
    (120.0, 0),      # 0 Leo -> Aries (9th from Leo)
])
def test_navamsa(lon, sign):
    assert jy.varga(lon, 9) == sign


def test_rasi_equals_sign_for_every_degree():
    for lon in range(360):
        assert jy.varga(lon + 0.5, 1) == jy.sign_of(lon + 0.5)


def test_unsupported_varga_raises():
    with pytest.raises(ValueError):
        jy.varga(10.0, 5)


def test_vimshottari_cycle_is_120_years():
    jd = jy.julday(2000, 1, 1, 12, 0, 0, tz_offset=0)
    maha = [p for p in jy.vimshottari(jd, 100.0, levels=1) if p["level"] == 1]
    first_nine = maha[:9]
    span = first_nine[-1]["end"] - first_nine[0]["start"]
    assert abs(span - 120 * jy.SOLAR_YEAR) < 1e-6


def test_cli_rejects_missing_birth_data():
    with pytest.raises(SystemExit) as e:
        jy._cli(["--date", "2000-01-01"])
    assert e.value.code == 2


def test_cli_rejects_invalid_date():
    with pytest.raises(SystemExit):
        jy._cli(["--date", "2000-13-01", "--time", "12:00", "--tz", "0",
                 "--lat", "0", "--lon", "0"])


def test_cli_writes_svg(tmp_path, capsys):
    out = tmp_path / "chart.svg"
    jy._cli(["--date", "2000-01-01", "--time", "12:00", "--tz", "0",
             "--lat", "51.4769", "--lon", "0", "--ephe", EPHE,
             "--svg", str(out)])
    assert out.read_text(encoding="utf-8").startswith("<svg")
    assert "Lagna: Aries" in capsys.readouterr().out
