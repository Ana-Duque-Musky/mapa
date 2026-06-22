# Musky · Mapa PoC

Preview del mapa personalizado (OpenStreetMap + estilo Musky) para **toda España**.

## Ver online

**https://ana-duque-musky.github.io/mapa/**

## Datos

Los POIs (parques, pipicans, fuentes, veterinarios, playas caninas) se cargan desde **OpenStreetMap**:

- **Online:** al elegir categoría y acercar el mapa (zoom ≥ 10), se consulta Overpass en la zona visible.
- **Offline (opcional):** genera un bundle estático con `python3 fetch-osm-places-es.py` → `osm-places-es.js`.

## Archivos

| Archivo | Descripción |
|---|---|
| `index.html` | Mapa interactivo |
| `fetch-osm-places-es.py` | Script para descargar POIs de toda España |

Sin backend, sin API keys.

## Repo

https://github.com/Ana-Duque-Musky/mapa
