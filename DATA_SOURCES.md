# Fuentes de datos · Mapa Musky PoC

Documentación de bases de mapa, paquetes de POIs, APIs externas y contenido de cada archivo del PoC.

**Última revisión:** junio 2026

---

## Resumen

| Capa | Fuente | Licencia |
|---|---|---|
| Geometría del mapa (calles, edificios, parques base…) | [OpenStreetMap](https://www.openstreetmap.org/) | [ODbL](https://www.openstreetmap.org/copyright) |
| Tiles + estilo (HTML PoC) | [OpenFreeMap](https://openfreemap.org/) · estilo Liberty | Basado en OSM |
| Tiles (Flutter PoC) | [CARTO Basemaps](https://carto.com/basemaps/) · light_all | OSM + atribución CARTO |
| POIs Musky (parques, pipicans, fuentes, vets, playas) | OpenStreetMap vía [Overpass API](https://overpass-api.de/) | ODbL |
| Renderizado web | [MapLibre GL JS](https://maplibre.org/) 5.24.0 | BSD-3-Clause |
| Tipografía labels | [Krub](https://fonts.google.com/specimen/Krub) (Google Fonts) | SIL Open Font License |

---

## Arquitectura de datos

```
┌─────────────────────────────────────────────────────────────┐
│  CAPA VISUAL (mapa base)                                    │
│  HTML: OpenFreeMap Liberty → MapLibre GL JS                   │
│  Flutter: CARTO light_all → flutter_map                      │
│  Datos subyacentes: OpenStreetMap                            │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│  CAPA POIs (lugares Musky)                                  │
│                                                              │
│  1. Estático al cargar → osm-places-bcn.js                   │
│  2. Estático opcional   → osm-places-es.js (incompleto)      │
│  3. Dinámico en uso     → Overpass API (viewport, zoom ≥ 10) │
│                                                              │
│  Origen de todos los POIs: OpenStreetMap                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Servicios externos (URLs)

### Mapa base

| Servicio | URL | Uso en el proyecto |
|---|---|---|
| OpenStreetMap | https://www.openstreetmap.org/ | Fuente de datos geográficos |
| Atribución OSM | https://www.openstreetmap.org/copyright | Licencia ODbL |
| OpenFreeMap · estilo Liberty | https://tiles.openfreemap.org/styles/liberty | Estilo vectorial del PoC HTML |
| OpenFreeMap (proyecto) | https://openfreemap.org/ | Documentación del proveedor de tiles |
| CARTO Basemaps | https://carto.com/basemaps/ | Tiles raster en Flutter |
| CARTO tile URL | `https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png` | `musky_map.dart` |
| MapLibre GL JS (CDN) | https://unpkg.com/maplibre-gl@5.24.0/ | Librería de renderizado |
| Google Fonts · Krub | https://fonts.google.com/specimen/Krub | Tipografía de etiquetas del mapa |

### POIs (lugares)

| Servicio | URL | Uso en el proyecto |
|---|---|---|
| Overpass API (instancia DE) | https://overpass-api.de/api/interpreter | Generación de bundles + carga dinámica |
| Documentación Overpass | https://wiki.openstreetmap.org/wiki/Overpass_API | Referencia de la API |
| Overpass Turbo | https://overpass-turbo.eu/ | Probar queries OSM manualmente |

### Otros (no son datos de mapa)

| Servicio | URL | Uso |
|---|---|---|
| Google Maps Directions | `https://www.google.com/maps/dir/?api=1&destination={lat},{lng}` | Botón «Cómo llegar» en detalle de lugar |
| GitHub Pages (PoC online) | https://ana-duque-musky.github.io/mapa/ | Hosting público |
| Repo GitHub | https://github.com/Ana-Duque-Musky/mapa | Código y bundles publicados |

---

## Categorías Musky ↔ tags OpenStreetMap

| Chip en la app | ID filtro | Tags OSM consultados |
|---|---|---|
| Parques | `park` | `leisure=park` (node + way) |
| Parque para perros | `dog` | `leisure=dog_park` (node + way) |
| Fuentes de agua | `fountain` | `amenity=drinking_water` (node) |
| Veterinarios | `vet` | `amenity=veterinary` (node) |
| Playa de perros | `beach` | `leisure=beach` + `dog=yes` (node + way) |

### Diferencia entre queries

La query del **mapa en vivo** (`preview.html` → `buildOverpassQuery`) incluye **todos** los parques.

La query del **generador estático** (`fetch-osm-places-es.py`) filtra parques con `way["leisure"="park"]["name"]` — solo parques **con nombre**. Esto hace que el bundle generado por el script sea **menos completo** que lo que devuelve Overpass en runtime.

---

## Archivos del PoC HTML

Ubicación principal: `docs/map-poc/`  
Copia publicada en GitHub Pages: `musky-map-poc/` (repo [mapa](https://github.com/Ana-Duque-Musky/mapa))

---

### `preview.html` (~64 KB · ~2 000 líneas)

**Qué es:** Aplicación web completa del mapa Musky (PoC principal).

**Contiene:**
- UI: header, búsqueda, chips de categoría, drawer de lista, detalle de lugar, geolocalización
- Estilos Musky aplicados en runtime sobre OpenFreeMap (colores de vías, verdes, mar, edificios…)
- Lógica de carga de POIs: estático → dinámico (Overpass)
- Modo captura `?shot=1` para pantallazos sin UI
- Parámetros URL: `lat`, `lng`, `z`, `f`, `q`, `place`, `view`, `ulat`, `ulng`, `shot`, `download`, `w`, `h`

**Servicios que consume en runtime:**
- `https://tiles.openfreemap.org/styles/liberty` — mapa base
- `https://overpass-api.de/api/interpreter` — POIs dinámicos (zoom ≥ 10)
- `osm-places-bcn.js` — POIs estáticos (script tag)
- `https://unpkg.com/maplibre-gl@5.24.0/` — MapLibre
- `https://fonts.googleapis.com/` — Krub

**Equivalente publicado:** `musky-map-poc/index.html`

---

### `osm-places-bcn.js` (~378 KB)

**Qué es:** Bundle estático de POIs Musky para el área de Barcelona, en formato JavaScript.

**Formato:**
```javascript
window.OSM_PLACES_DATA = { "version": 0.6, "elements": [ … ] };
```

**Origen:** OpenStreetMap, extraído vía Overpass API.  
**Generación:** descarga manual/script puntual (no hay `fetch-osm-places-bcn.py` en el repo; el formato es compatible con el generador de España).

**Estadísticas (junio 2026):**

| Métrica | Valor |
|---|---:|
| Total POIs | 1 316 |
| Con nombre | 289 (22 %) |
| Tamaño | ~378 KB |
| Latitud | 41.35 – 41.45 |
| Longitud | 2.05 – 2.25 |

**Desglose por categoría Musky:**

| Categoría | POIs | Con nombre |
|---|---:|---:|
| Fuentes (`drinking_water`) | 898 | 17 (2 %) |
| Parques (`park`) | 218 | 218 (100 %) |
| Pipicans (`dog_park`) | 147 | 6 (4 %) |
| Veterinarios (`veterinary`) | 52 | 47 (90 %) |
| Playas caninas (`beach` + `dog=yes`) | 1 | 1 (100 %) |

**Cobertura por zona:**

| Zona | POIs aprox. | Notas |
|---|---:|---|
| Barcelona ciudad | ~1 255 | Cobertura buena |
| Badalona | 9 | Solo pipicans, sin nombres |
| L'Hospitalet / Santa Coloma | 15 | Solo pipicans |

**Cómo se carga:** `<script src="osm-places-bcn.js">` al inicio de `preview.html`. Es la fuente estática principal.

**Publicado en:** https://ana-duque-musky.github.io/mapa/osm-places-bcn.js

---

### `osm-places-bcn.json` (~378 KB)

**Qué es:** Mismo contenido que `osm-places-bcn.js` pero en JSON puro (sin wrapper JS).

**Diferencia con `.js`:** 1 315 elementos vs 1 316 (el `.js` incluye 1 playa canina adicional). Por lo demás, contenido equivalente.

**Cómo se carga:** Fallback en `bootstrapPlacesData()` vía `fetch('osm-places-bcn.json')` si el script JS no está disponible.

**No publicado** en GitHub Pages (solo está el `.js`).

---

### `osm-places-es.js` (~187 KB)

**Qué es:** Bundle estático nacional de POIs Musky para España. **Incompleto.**

**Formato:** Igual que `osm-places-bcn.js` → `window.OSM_PLACES_DATA = { … }`

**Origen:** Generado por `fetch-osm-places-es.py` llamando a Overpass API.

**Estadísticas (junio 2026):**

| Métrica | Valor |
|---|---:|
| Total POIs | 851 |
| Con nombre | 399 (47 %) |
| Tamaño | ~187 KB |
| Cobertura real | **Solo Canarias** (lat 27.6 – 29.0, lon -18.1 – -8.1) |
| Península / Baleares | **0 POIs** |

**Desglose por categoría:**

| Categoría | POIs |
|---|---:|
| Fuentes | 468 |
| Parques | 293 |
| Veterinarios | 60 |
| Pipicans | 30 |
| Playas caninas | 0 |

**Estado de generación:** de 176 tiles planificados, solo ~7 tiles de Canarias devolvieron datos antes de errores 429/504/connection refused (ver `fetch-osm.log`).

**Cómo se carga:** Segundo fallback en `bootstrapPlacesData()` — solo si existe y el bundle BCN ya se cargó.

**No publicado** en GitHub Pages.

---

### `osm-places-es.json` (~187 KB)

**Qué es:** Mismo contenido que `osm-places-es.js` en JSON puro.

**Cómo se carga:** Tercer fallback en `bootstrapPlacesData()` vía `fetch('osm-places-es.json')`.

---

### `fetch-osm-places-es.py` (~3 KB · 106 líneas)

**Qué es:** Script Python para descargar POIs de **toda España** desde Overpass y generar `osm-places-es.js` + `osm-places-es.json`.

**API que llama:** https://overpass-api.de/api/interpreter

**Parámetros:**
- Bbox España: sur 27.5, oeste -18.5, norte 43.9, este 4.6
- Tiles: cuadrícula de 1.5° × 1.5° → 176 tiles
- Pausa entre tiles: 2 s
- User-Agent: `MuskyMapPoC/1.0 (contact@musky.app)`

**Query Overpass (resumen):**
```
node/way leisure=dog_park
node amenity=drinking_water
node amenity=veterinary
way leisure=park + name        ← solo parques con nombre
node/way leisure=beach + dog=yes
```

**Uso:**
```bash
cd docs/map-poc
python3 fetch-osm-places-es.py
```

**Salida:** `osm-places-es.js`, `osm-places-es.json`

**Estado:** funcional pero la última ejecución falló en la mayoría de tiles (rate limiting y timeouts de Overpass).

---

### `fetch-osm.log` (~15 KB · 354 líneas)

**Qué es:** Log de la última ejecución de `fetch-osm-places-es.py`.

**Contiene:**
- Progreso tile a tile (`[N/176] lat,lon → lat,lon`)
- POIs acumulados por tile
- Errores: HTTP 504, 429, connection refused
- Resultado final: 851 lugares → `osm-places-es.js` (187 KB)

**Utilidad:** diagnóstico de por qué el bundle nacional está incompleto.

---

## Archivos Flutter (app)

Ubicación: `lib/presentation/map/` y `assets/map/`

---

### `lib/presentation/map/ui/widgets/musky_map.dart`

**Qué es:** Widget de mapa en Flutter (PoC).

**Tiles:** CARTO light_all  
`https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png`

**Atribución:** OpenStreetMap + CARTO (widget `RichAttributionWidget`).

**POIs:** recibe lista de `MapPlace` — **no carga bundles OSM**.

---

### `lib/presentation/map/models/map_place.dart`

**Qué es:** Modelo de lugar + **5 POIs hardcodeados** para el PoC Flutter.

**Contenido:** `mapPocPlaces` — lista fija de 5 lugares de ejemplo en Barcelona (parque, pipican, vet, fuente, playa).

**Nota en código:** referencia al bundle real en `docs/map-poc/osm-places-bcn.js` como objetivo futuro.

---

### `lib/presentation/map/ui/pages/map_explorer_screen.dart`

**Qué es:** Pantalla del explorador de mapa (chips, pins, selección).

**Datos:** usa `mapPocPlaces` estático — no conectado a OSM ni Overpass.

---

### `assets/map/musky_map_style.json`

**Qué es:** Documentación de tokens de color del mapa Musky y referencia al estilo base.

**Contiene:**
- Mapeo Figma → hex → tokens del repo (`AppColors.*`)
- Colores: vías, fondo, áreas verdes, zonas beige, edificios, mar
- URL estilo base: `https://tiles.openfreemap.org/styles/liberty`
- Nota: overrides se aplican en runtime vía MapLibre `setPaintProperty` (solo HTML PoC)

---

## Repo publicado (GitHub Pages)

Repo: https://github.com/Ana-Duque-Musky/mapa  
URL: https://ana-duque-musky.github.io/mapa/

| Archivo publicado | Contenido |
|---|---|
| `index.html` | Copia de `preview.html` |
| `osm-places-bcn.js` | Bundle POIs Barcelona |
| `fetch-osm-places-es.py` | Generador nacional (sin ejecutar en CI) |
| `README.md` | Introducción breve |
| `.nojekyll` | Desactiva Jekyll en GitHub Pages |

**No publicados:** `osm-places-es.js`, `osm-places-bcn.json`, `preview.html`, `fetch-osm.log`, `DATA_SOURCES.md`

---

## Orden de carga de POIs en `preview.html`

```
1. osm-places-bcn.js          ← script al parsear HTML (siempre)
2. osm-places-bcn.json        ← fetch fallback
3. osm-places-es.js           ← script dinámico si existe
4. osm-places-es.json         ← fetch fallback
5. Overpass API               ← al elegir categoría + zoom ≥ 10
6. FALLBACK_OSM_ELEMENTS      ← 6 lugares hardcodeados si Overpass falla y no hay datos
```

Con geolocalización activa, los POIs visibles se filtran a **25 km** del usuario (`USER_RADIUS_KM = 25`).

---

## Modos especiales de URL

| Parámetro | Ejemplo | Efecto |
|---|---|---|
| `shot=1` | `?shot=1&lat=41.4&lng=2.15&z=15` | Mapa a pantalla completa, sin UI |
| `download=1` | `…&shot=1&download=1` | Descarga PNG automática al cargar |
| `w`, `h` | `…&w=1200&h=630` | Tamaño fijo del viewport (modo captura) |
| `f` | `?f=dog` | Filtro de categoría activo |
| `lat`, `lng`, `z` | — | Posición y zoom del mapa |

---

## Atribución obligatoria

Al usar estos datos en producción, incluir:

- **© OpenStreetMap contributors** — https://www.openstreetmap.org/copyright
- **OpenFreeMap** o **CARTO** según el stack de tiles usado
- **MapLibre** si se usa su logo/atribución según licencia BSD

---

## Estado actual y pendientes

| Elemento | Estado |
|---|---|
| Mapa base HTML (OpenFreeMap + Musky) | Funcional |
| Mapa base Flutter (CARTO) | Funcional, colores Musky no aplicados |
| Bundle Barcelona | Completo para ciudad, incompleto en área metropolitana |
| Bundle España | ~2 % (solo Canarias) |
| Carga dinámica Overpass | Funcional |
| Flujo «ubicación → bundle local» | No implementado |
| Flutter conectado a OSM | No (5 POIs hardcodeados) |

**Próximos pasos sugeridos:**
1. Unificar query Overpass entre `fetch-osm-places-es.py` y `preview.html`
2. Completar generación nacional o por tiles/chunks
3. Ampliar bbox del bundle Barcelona (Badalona, metro)
4. Conectar Flutter al bundle/chunk según ubicación del usuario
