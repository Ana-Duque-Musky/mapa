#!/usr/bin/env python3
"""Descarga POIs Musky de OpenStreetMap para toda España (Overpass API)."""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
# Península, Baleares y Canarias
SPAIN = dict(south=27.5, west=-18.5, north=43.9, east=4.6)
TILE_DEG = 1.5
SLEEP_SEC = 2

QUERY = """[out:json][timeout:90];
(
  node["leisure"="dog_park"]({s},{w},{n},{e});
  way["leisure"="dog_park"]({s},{w},{n},{e});
  node["amenity"="drinking_water"]({s},{w},{n},{e});
  node["amenity"="veterinary"]({s},{w},{n},{e});
  way["leisure"="park"]["name"]({s},{w},{n},{e});
  node["leisure"="beach"]["dog"="yes"]({s},{w},{n},{e});
  way["leisure"="beach"]["dog"="yes"]({s},{w},{n},{e});
);
out center;"""


def tiles():
    lat = SPAIN["south"]
    while lat < SPAIN["north"]:
        n = min(lat + TILE_DEG, SPAIN["north"])
        lng = SPAIN["west"]
        while lng < SPAIN["east"]:
            e = min(lng + TILE_DEG, SPAIN["east"])
            yield lat, lng, n, e
            lng += TILE_DEG
        lat += TILE_DEG


def fetch_tile(s: float, w: float, n: float, e: float) -> list[dict]:
    query = QUERY.format(s=s, w=w, n=n, e=e)
    body = urllib.parse.urlencode({"data": query}).encode()
    req = urllib.request.Request(
        OVERPASS_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "MuskyMapPoC/1.0 (contact@musky.app)",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        payload = json.load(resp)
    return payload.get("elements", [])


def dedupe(elements: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for el in elements:
        key = f"{el.get('type')}:{el.get('id')}"
        if key in seen:
            continue
        seen.add(key)
        out.append(el)
    return out


def main() -> int:
    out_dir = Path(__file__).resolve().parent
    all_elements: list[dict] = []
    tile_list = list(tiles())
    total = len(tile_list)

    print(f"Descargando {total} tiles de España…")
    for i, (s, w, n, e) in enumerate(tile_list, 1):
        print(f"[{i}/{total}] {s:.1f},{w:.1f} → {n:.1f},{e:.1f}", flush=True)
        try:
            chunk = fetch_tile(s, w, n, e)
            all_elements.extend(chunk)
            print(f"  +{len(chunk)} (acumulado {len(all_elements)})", flush=True)
        except Exception as err:  # noqa: BLE001
            print(f"  error: {err}", file=sys.stderr, flush=True)
        time.sleep(SLEEP_SEC)

    elements = dedupe(all_elements)
    payload = {"version": 0.6, "elements": elements}

    json_path = out_dir / "osm-places-es.json"
    js_path = out_dir / "osm-places-es.js"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    js_path.write_text(
        "window.OSM_PLACES_DATA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )

    print(f"Listo: {len(elements)} lugares → {js_path.name} ({js_path.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
