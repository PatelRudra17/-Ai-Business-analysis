"""Generate a hexagonal search grid over a circular area to ensure full coverage."""
import math


def generate_search_grid(lat: float, lng: float, radius_meters: int, step_meters: int = 800) -> list[dict]:
    """
    Return a list of {lat, lng} points covering the search area.
    Uses a hex grid so adjacent circles overlap correctly.
    """
    points = []
    # Convert metres to degrees (approximate)
    lat_step = step_meters / 111320
    lng_step = step_meters / (111320 * math.cos(math.radians(lat)))
    rows = int(radius_meters / step_meters) + 1

    for row in range(-rows, rows + 1):
        col_offset = 0.5 * lng_step if row % 2 else 0.0
        cols = int(math.sqrt(max(0, radius_meters ** 2 - (row * step_meters) ** 2)) / step_meters) + 1
        for col in range(-cols, cols + 1):
            p_lat = lat + row * lat_step
            p_lng = lng + col * lng_step + col_offset
            dist = _haversine(lat, lng, p_lat, p_lng)
            if dist <= radius_meters:
                points.append({"lat": round(p_lat, 6), "lng": round(p_lng, 6), "dist_from_center": round(dist)})

    return points


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    a = (
        math.sin((phi2 - phi1) / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(math.radians(lng2 - lng1) / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
