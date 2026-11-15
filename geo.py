"""Small geodesy helpers for a spherical Mars.

All distances are in metres. Latitude/longitude are in degrees.
Mars is modelled as a sphere (IAU sphere radius 3396.19 km), which is plenty
accurate for planning at the few-kilometre scale of a surface excursion.
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence

MARS_RADIUS_M = 3_396_190.0

LatLon = tuple[float, float]


def haversine_m(a: LatLon, b: LatLon) -> float:
    """Great-circle distance between two (lat, lon) points."""
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    h = (
        math.sin((lat2 - lat1) / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    )
    return 2 * MARS_RADIUS_M * math.asin(math.sqrt(h))


def _to_local_xy(point: LatLon, origin: LatLon) -> tuple[float, float]:
    """Project a point to local east/north metres around ``origin``."""
    lat, lon = point
    lat0, lon0 = origin
    x = math.radians(lon - lon0) * MARS_RADIUS_M * math.cos(math.radians(lat0))
    y = math.radians(lat - lat0) * MARS_RADIUS_M
    return x, y


def point_segment_distance_m(point: LatLon, start: LatLon, end: LatLon) -> float:
    """Shortest distance from ``point`` to the segment ``start``-``end``."""
    px, py = _to_local_xy(point, point)
    ax, ay = _to_local_xy(start, point)
    bx, by = _to_local_xy(end, point)
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return math.hypot(ax - px, ay - py)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length_sq))
    return math.hypot(ax + t * dx - px, ay + t * dy - py)


def route_length_m(points: Sequence[LatLon]) -> float:
    """Total length of a polyline."""
    return sum(haversine_m(a, b) for a, b in zip(points, points[1:]))


def min_distance_to_route_m(point: LatLon, route: Sequence[LatLon]) -> float:
    """Shortest distance from ``point`` to any segment of ``route``."""
    if len(route) == 1:
        return haversine_m(point, route[0])
    return min(
        point_segment_distance_m(point, a, b) for a, b in zip(route, route[1:])
    )


def clean_coords(points: Iterable[LatLon]) -> list[LatLon]:
    """Validate and normalise (lat, lon) pairs."""
    out: list[LatLon] = []
    for lat, lon in points:
        if not (-90 <= lat <= 90 and -180 <= lon <= 360):
            raise ValueError(f"Coordinate out of range: {lat}, {lon}")
        out.append((float(lat), float(lon)))
    return out
