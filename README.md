# Marswalk: Jezero EVA Planner

An interactive map for planning a safe astronaut walk on Mars. It layers real
NASA orbital data on one map and checks your route against hazard zones in
real time.

## The problem

Mission planners and crews need to see terrain, science targets and danger
zones together. Today that usually means switching between separate tools.
Marswalk puts them in one view and gives instant feedback while you move
waypoints, so a route that clips a boulder field or a radiation zone is
obvious immediately.

## What it does

- **Four NASA data layers**, stackable with opacity sliders:
  MRO CTX (sharp terrain imagery), MGS MOLA (elevation hillshade),
  Odyssey THEMIS (thermal infrared) and Viking MDIM 2.1 (global colour).
- **Science targets** and **hazard zones** drawn as true-radius circles,
  with layer toggles and click-to-fly cards.
- **Route planner**: draw waypoints, drag to move them, right-click to
  delete, undo, clear, reset to the preset, and export as GeoJSON.
- **Live route analysis**: distance, estimated walking time, and clearance
  from each hazard, reported as `CLEAR`, `CAUTION` or `CONFLICT`.
- **EVA time budget**: the out-and-back time is compared against the
  budget and flagged `OVER BUDGET` when exceeded.
- **NASA surface imagery**: Perseverance / Jezero photos from the NASA
  Image and Video Library, cached, loaded after first paint. If NASA is
  unreachable the app shows "unavailable"; it never invents images.
- Responsive layout and keyboard-accessible controls.

## Data sources

| Layer | Mission / instrument | Resolution | Use |
|---|---|---|---|
| CTX mosaic, Jezero | Mars Reconnaissance Orbiter CTX | ~10 m/px at max zoom | Detailed terrain |
| MOLA colour hillshade | Mars Global Surveyor MOLA | 463 m/px | Elevation context |
| THEMIS infrared (day) | Mars Odyssey THEMIS | 100 m/px | Thermal context |
| Viking colour mosaic | Viking Orbiter MDIM 2.1 | 232 m/px | Global colour context |
| Surface photos | NASA Image and Video Library | n/a | Ground-level imagery |

Map tiles are served by NASA/JPL Mars Trek. Positions and distances are
computed on a Mars-radius sphere (3,396,190 m), not Earth's.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py                    # http://127.0.0.1:5000
```

No API key is needed.

Other commands:

```bash
FLASK_DEBUG=1 python app.py      # dev mode (never in production)
gunicorn "app:create_app()"      # production
pytest                           # run the tests
```

Optional environment variables: `HOST`, `PORT`, `LOG_LEVEL`,
`IMAGERY_TTL_SECONDS`.

## Project layout

| File | Purpose |
|---|---|
| `mission_data.py` | Single source of truth: layers, targets, hazards, route |
| `planning.py` / `geo.py` | Route length, EVA time, hazard clearance (Mars radius) |
| `imagery.py` | Cached NASA Image Library client, never fabricates images |
| `app.py` | Flask app factory and API |
| `templates/index.html` | Page shell |
| `static/app.js` / `static/style.css` | Map, sidebar and route logic; styling |
| `tests/test_app.py` | Backend tests |

### API

| Endpoint | Returns |
|---|---|
| `GET /api/v1/mission` | Mission definition plus computed route analysis |
| `GET /api/v1/imagery` | Cached NASA imagery with status |
| `GET /api/v1/status` | Service health |

## Limitations

- The **science targets, hazards and route are illustrative placeholders**
  positioned inside Jezero Crater. They are not real CRISM / HiRISE
  coordinates.
- Walking speed (2 km/h), the 100 m caution buffer and the 240-minute EVA
  budget are **planning assumptions**, not measured values.
- The header pressure and radiation figures are published reference values
  (MSL REMS / RAD) and are labelled "not live".
- Radiation zones carry a maximum dwell time in the data, but the app does
  not yet track time spent inside them.

## Roadmap

- Radiation dwell-time tracking per hazard zone
- Slope-aware auto-routing from MOLA elevation
- HiRISE close-up layer
- Real target and hazard coordinates from published CRISM / HiRISE products
- Photos linked to each science target

## Credits

Map tiles: NASA/JPL Mars Trek. Imagery: NASA Image and Video Library.
Mapping: [Leaflet](https://leafletjs.com/).
