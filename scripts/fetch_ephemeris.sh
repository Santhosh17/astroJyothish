#!/usr/bin/env sh
# Download the Swiss Ephemeris data files (1800-2400 CE) into ./ephe.
# Without them pyswisseph falls back to the Moshier ephemeris, which is
# accurate to about 1 arcsecond but less reproducible across versions.
set -e
mkdir -p ephe
for f in sepl_18.se1 semo_18.se1 seas_18.se1; do
  curl -sfL -o "ephe/$f" "https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/$f"
  echo "downloaded ephe/$f"
done
