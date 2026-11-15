"""Mission definition for the Marswalk Surface Explorer.

This is the single source of truth: the backend analyses it and the
frontend renders exactly what the API returns. Nothing is duplicated in
JavaScript.

IMPORTANT: target, hazard and route positions are APPROXIMATE planning
locations around the Jezero delta, placed from published descriptions of
the area (not surveyed). Check them against the CTX layer and adjust.
``REFERENCE_TELEMETRY`` values are published surface measurements (not
live) and are labelled that way in the UI.
"""

def _tile(layer: str, ext: str) -> str:
    return (
        f"https://trek.nasa.gov/tiles/Mars/EQ/{layer}/1.0.0/default/"
        f"default028mm/{{z}}/{{y}}/{{x}}.{ext}"
    )


MISSION = {
    "name": "Marswalk // Jezero Western Fan",
    "location": "Jezero Crater - Western Fan Segment",
    "objective": (
        "Walk from a rover drop-off to the Jezero delta front to examine "
        "layered sediments deposited in an ancient lake, while keeping clear "
        "of soft dune terrain and steep slopes."
    ),
    "data_note": (
        "Layers are real NASA data. Target, hazard and route positions are "
        "approximate planning locations, not surveyed."
    ),
    "map": {
        "center": [18.447, 77.40],
        "zoom": 13,
        "min_zoom": 8,
        "max_zoom": 15,
        "radius_m": 3_396_190,  # Mars 2000 sphere, matches NASA Trek CRS
        "bounds": [[15.9, 75.15], [19.45, 78.87]],  # CTX Jezero coverage
    },
    "data_layers": [
        {
            "id": "ctx", "title": "CTX mosaic, Jezero", "type": "Optical (sharp)",
            "resolution": "~10 m/px at max zoom", "source": "MRO CTX",
            "url": _tile("Jezero_CTX_BlockAdj_dd", "png"),
            "max_native_zoom": 12, "default_on": True, "default_opacity": 1.0,
            "attribution": "NASA/JPL Mars Trek - MRO CTX", "enabled": True,
        },
        {
            "id": "mola", "title": "MOLA colour hillshade", "type": "Topographic",
            "resolution": "463 m/px", "source": "Mars Global Surveyor MOLA",
            "url": _tile("Mars_MGS_MOLA_ClrShade_merge_global_463m", "jpg"),
            "max_native_zoom": 6, "default_on": True, "default_opacity": 0.45,
            "attribution": "NASA/JPL Mars Trek - MGS MOLA", "enabled": True,
        },
        {
            "id": "themis", "title": "THEMIS infrared (day)", "type": "Thermal",
            "resolution": "100 m/px", "source": "Mars Odyssey THEMIS",
            "url": _tile("THEMIS_DayIR_ControlledMosaics_100m_v2_oct2018", "jpg"),
            "alt_ext": "png",  # retried automatically if .jpg tiles 404
            "max_native_zoom": 8, "default_on": False, "default_opacity": 0.6,
            "attribution": "NASA/JPL Mars Trek - Odyssey THEMIS", "enabled": True,
        },
        {
            "id": "viking", "title": "Viking colour mosaic", "type": "Optical (global)",
            "resolution": "232 m/px", "source": "Viking Orbiter MDIM 2.1",
            "url": _tile("Mars_Viking_MDIM21_ClrMosaic_global_232m", "jpg"),
            "max_native_zoom": 6, "default_on": False, "default_opacity": 1.0,
            "attribution": "NASA/JPL Mars Trek - Viking MDIM 2.1", "enabled": True,
        },
    ],
    "science_targets": [
        {
            "id": "SCI-01",
            "name": "Delta Scarp Front (approx.)",
            "lat": 18.452,
            "lon": 77.385,
            "instrument": "CTX / HiRISE (optical)",
            "description": (
                "Steep eroded edge of the Jezero delta where layered "
                "sediments are exposed. Approximate position."
            ),
        },
        {
            "id": "SCI-02",
            "name": "Mid-Fan Layered Outcrop (approx.)",
            "lat": 18.449,
            "lon": 77.400,
            "instrument": "CTX (optical)",
            "description": (
                "Candidate stop on the way to the scarp to compare "
                "layering with the delta front. Approximate position."
            ),
        },
        {
            "id": "SCI-03",
            "name": "Landing Site Reference",
            "lat": 18.4446,
            "lon": 77.4509,
            "instrument": "Perseverance landing (reference)",
            "description": (
                "Octavia E. Butler landing site of NASA's Perseverance "
                "rover, a known ground-truth point to orient by."
            ),
        },
    ],
    "hazards": [
        {
            "id": "HAZ-01",
            "name": "Dune and Ripple Terrain (approx.)",
            "kind": "mobility",
            "lat": 18.428,
            "lon": 77.405,
            "radius_m": 300,
            "risk": (
                "Soft, rippled sand: foot and rover traction risk. "
                "Approximate zone."
            ),
        },
        {
            "id": "HAZ-02",
            "name": "Steep Scarp Slope (approx.)",
            "kind": "slope",
            "lat": 18.458,
            "lon": 77.380,
            "radius_m": 200,
            "risk": (
                "Steep cliff face below the delta edge: fall and slope "
                "hazard for suited crew. Approximate zone."
            ),
        },
        {
            "id": "HAZ-03",
            "name": "Rough Boulder Terrain (approx.)",
            "kind": "mobility",
            "lat": 18.440,
            "lon": 77.392,
            "radius_m": 250,
            "risk": (
                "Boulder-strewn ground: snag and trip hazard for suit "
                "joints and mobility units. Approximate zone."
            ),
        },
    ],
    "route": {
        "name": "EVA-1 planned traverse",
        "waypoints": [
            {"label": "Rover drop-off", "lat": 18.442, "lon": 77.420},
            {"label": "Mid-fan outcrop", "lat": 18.449, "lon": 77.400},
            {"label": "Delta front", "lat": 18.452, "lon": 77.385},
        ],
        # Planning assumptions, not measured values.
        "assumed_speed_kmh": 2.0,
        "caution_buffer_m": 100,
        "eva_budget_min": 240,
    },
}

REFERENCE_TELEMETRY = {
    "atmospheric_pressure": {"value": "~7 mbar", "source": "MSL REMS / Mars surface mean (reference)"},
    "radiation_dose": {"value": "~0.64 mSv/day", "source": "MSL RAD surface dose equivalent (reference)"},
}