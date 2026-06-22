# Musky · Mapa PoC

Preview del mapa personalizado (OpenStreetMap + estilo Musky) para Barcelona.

## Ver online

1. En el repo: **Settings → Pages → Build and deployment → Source: GitHub Actions** (solo la primera vez).
2. Tras el workflow verde: **https://ana-duque-musky.github.io/mapa/**

Código: [github.com/Ana-Duque-Musky/mapa](https://github.com/Ana-Duque-Musky/mapa)

## Archivos

| Archivo | Descripción |
|---|---|
| `index.html` | Mapa interactivo (MapLibre + chips + lista + detalle) |
| `osm-places-bcn.js` | POIs OSM Barcelona (~1300 lugares) |

Sin backend, sin API keys. Tiles: [OpenFreeMap](https://openfreemap.org/).

## Local

Abrir `index.html` en un servidor estático (no `file://` para compartir enlace):

```bash
npx --yes serve -p 3456
```

## Privacidad

Repo público = mapa visible para cualquiera con el enlace. Para uso interno, cambia el repo a **Private** en GitHub (Settings → Danger zone → Change visibility). GitHub Pages en repos privados requiere plan de pago; alternativa: [Netlify Drop](https://app.netlify.com/drop) con el zip de esta carpeta.
