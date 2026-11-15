"""Route analysis: length, EVA time and clearance from each hazard."""

from __future__ import annotations

from geo import min_distance_to_route_m, route_length_m


def analyse_route(mission: dict) -> dict:
    """Return distance, duration and per-hazard clearance for the route."""
    route = mission["route"]
    points = [(w["lat"], w["lon"]) for w in route["waypoints"]]
    buffer_m = route.get("caution_buffer_m", 100)
    speed_kmh = route["assumed_speed_kmh"]

    length_m = route_length_m(points)
    walking_min = length_m / (speed_kmh * 1000 / 60)

    hazards = []
    for h in mission["hazards"]:
        dist = min_distance_to_route_m((h["lat"], h["lon"]), points)
        clearance = dist - h["radius_m"]
        if clearance < 0:
            status = "conflict"
        elif clearance < buffer_m:
            status = "caution"
        else:
            status = "clear"
        hazards.append(
            {
                "hazard_id": h["id"],
                "name": h["name"],
                "kind": h["kind"],
                "clearance_m": round(clearance),
                "status": status,
            }
        )

    return {
        "distance_m": round(length_m),
        "walking_time_min": round(walking_min),
        "assumed_speed_kmh": speed_kmh,
        "hazard_clearance": hazards,
        "has_conflict": any(h["status"] == "conflict" for h in hazards),
    }
