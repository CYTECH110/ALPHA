"""
navigation.py
Computes a route between any two campus locations. Always attempts
real road/path routing via OSRM first (which correctly uses mapped
internal campus roads like University Street when they exist). Falls
back to a direct line only when OSRM's route is a suspiciously large
detour compared to the straight-line distance -- which happens when
OSRM has no internal path data and instead routes around the campus
wall via the public road network.
"""

import requests
from geopy.distance import geodesic
from campus_data import CAMPUS_LOCATIONS

START_POINT = "entrance"

OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/foot"

# If OSRM's route is more than this many times longer than the straight
# line distance, we treat it as an illegal wall-detour and use a direct
# line instead. Real walking paths are rarely more than ~1.5-2x the
# straight-line distance; a wall-avoidance detour is usually far worse.
DETOUR_RATIO_LIMIT = 2.2

# Additional safeguard: if OSRM's route adds more than this many extra
# meters versus the straight line, also treat it as a bad detour --
# catches cases where the ratio looks OK but the absolute extra
# distance is still clearly a workaround (e.g. very short trips).
DETOUR_EXTRA_METERS_LIMIT = 250


def get_road_route(start_coords, destination_coords, via_points=None):
    """
    Calls the OSRM public API for a real walking route. If via_points
    is provided, OSRM is forced to route through those coordinates in
    order (start -> via_points -> destination), keeping the route on
    real mapped roads/paths instead of taking a long outer detour.

    Uses a wide "radiuses" tolerance so OSRM can still snap a live GPS
    point to the nearest known road/path even if the person is standing
    somewhat off the mapped network (e.g. inside a building, on an
    unmapped path) -- without this, OSRM silently fails to route from
    such points and we'd incorrectly fall back to a straight line.
    """
    via_points = via_points or []
    all_points = [start_coords] + via_points + [destination_coords]

    coord_string = ";".join(f"{lon},{lat}" for lat, lon in all_points)
    # Allow each point to snap to a road/path within 200 meters
    radius_string = ";".join(["200"] * len(all_points))

    url = f"{OSRM_BASE_URL}/{coord_string}"
    params = {
        "overview": "full",
        "geometries": "geojson",
        "radiuses": radius_string,
    }

    try:
        response = requests.get(url, params=params, timeout=6)
        response.raise_for_status()
        data = response.json()

        if data.get("code") != "Ok" or not data.get("routes"):
            print(f"[OSRM] Route request failed: code={data.get('code')}, "
                  f"message={data.get('message', 'no message')}")
            return None

        route = data["routes"][0]
        distance_meters = route["distance"]
        waypoints = [
            (point[1], point[0]) for point in route["geometry"]["coordinates"]
        ]

        return {"waypoints": waypoints, "distance_meters": distance_meters}

    except (requests.RequestException, KeyError, ValueError, IndexError) as e:
        print(f"[OSRM] Request exception: {e}")
        return None


def generate_turn_instructions(waypoints, destination_name, total_distance):
    return [
        {
            "instruction": f"Head towards {destination_name.title()}, "
                            f"about {int(total_distance)} meters away",
            "trigger_coords": list(waypoints[-1]),
        },
        {
            "instruction": f"You have arrived at {destination_name.title()}",
            "trigger_coords": list(waypoints[-1]),
        },
    ]


def compute_route(start_coords, destination_coords):
    """
    Tries real road routing first. Falls back to a direct line if OSRM
    fails, OR if OSRM's route looks like an illegal wall-avoidance
    detour (much longer than the straight-line distance would suggest).
    """
    straight_line_distance = geodesic(start_coords, destination_coords).meters

    road_route = get_road_route(start_coords, destination_coords)

    if road_route is not None:
        road_distance = road_route["distance_meters"]
        extra_distance = road_distance - straight_line_distance
        ratio = road_distance / straight_line_distance if straight_line_distance > 0 else 1

        looks_like_bad_detour = (
            ratio > DETOUR_RATIO_LIMIT and extra_distance > DETOUR_EXTRA_METERS_LIMIT
        )

        if not looks_like_bad_detour:
            return road_route["waypoints"], road_distance

    # Fallback: OSRM failed, OR its route was a clear wall-avoidance detour
    return [start_coords, destination_coords], straight_line_distance


def find_route_from_coords(start_coords, destination: str):
    """Routes from a raw GPS coordinate to a named destination."""
    destination = destination.lower().strip()

    if destination not in CAMPUS_LOCATIONS:
        return {"error": f"Unknown destination: '{destination}'"}

    destination_coords = CAMPUS_LOCATIONS[destination]
    waypoints, distance = compute_route(start_coords, destination_coords)

    return {
        "path": ["your location", destination],
        "coordinates": [list(point) for point in waypoints],
        "distance_meters": round(distance, 1),
        "turn_instructions": generate_turn_instructions(waypoints, destination, distance),
    }


def find_route(start: str, destination: str):
    """Routes between two NAMED locations."""
    start = start.lower().strip()
    destination = destination.lower().strip()

    if start == destination:
        return {"error": "You're already at that location."}
    if start not in CAMPUS_LOCATIONS:
        return {"error": f"Unknown starting point: '{start}'"}
    if destination not in CAMPUS_LOCATIONS:
        return {"error": f"Unknown destination: '{destination}'"}

    start_coords = CAMPUS_LOCATIONS[start]
    destination_coords = CAMPUS_LOCATIONS[destination]
    waypoints, distance = compute_route(start_coords, destination_coords)

    return {
        "path": [start, destination],
        "coordinates": [list(point) for point in waypoints],
        "distance_meters": round(distance, 1),
        "turn_instructions": generate_turn_instructions(waypoints, destination, distance),
    }


def find_nearest_landmark(user_coords):
    """Returns the name and distance of the closest known landmark."""
    nearest_name = None
    nearest_distance = float("inf")

    for name, coords in CAMPUS_LOCATIONS.items():
        distance = geodesic(user_coords, coords).meters
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_name = name

    return nearest_name, round(nearest_distance, 1)


if __name__ == "__main__":
    test_pairs = [
        ("science department", "library"),   # should follow University Street now
        ("ict department", "volleyball court"),  # should stay a direct line (wall detour)
        ("entrance", "advance park"),         # should follow real public roads
        ("library", "south market"),          # should follow real public roads
    ]

    for start, destination in test_pairs:
        result = find_route(start, destination)
        print(f"{start} -> {destination}: {result['distance_meters']} m, "
              f"{len(result['coordinates'])} waypoints")