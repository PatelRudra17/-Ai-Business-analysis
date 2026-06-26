"""
Overpass API client — free OpenStreetMap-based place search.
Replaces Google Places API. No API key needed.
"""
import asyncio
import math
from typing import Any

import httpx

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# OSM tags for each business type query
OSM_TAG_MAP: dict[str, list[str]] = {
    # Competitors
    "gym":              ['amenity=gym', 'leisure=fitness_centre', 'leisure=sports_centre'],
    "yoga studio":      ['amenity=gym', 'leisure=yoga'],
    "fitness center":   ['leisure=fitness_centre'],
    "cafe":             ['amenity=cafe'],
    "coffee shop":      ['amenity=cafe'],
    "bakery":           ['shop=bakery'],
    "tea shop":         ['amenity=cafe'],
    "restaurant":       ['amenity=restaurant'],
    "salon":            ['shop=hairdresser', 'shop=beauty'],
    "beauty parlour":   ['shop=beauty'],
    "hair studio":      ['shop=hairdresser'],
    "nail salon":       ['shop=beauty'],
    "spa":              ['leisure=spa'],
    "barbershop":       ['shop=hairdresser'],
    # Demand signals
    "college":          ['amenity=college', 'amenity=university'],
    "office":           ['office=company', 'office=commercial'],
    "coworking_space":  ['amenity=coworking_space'],
    "shopping_mall":    ['shop=mall', 'building=retail'],
    "metro_station":    ['railway=station', 'station=subway'],
    "apartment_complex":['building=apartments', 'building=residential'],
    "shopping_area":    ['shop=mall', 'landuse=commercial'],
    "gym":              ['leisure=fitness_centre'],
    "residential_society": ['building=apartments', 'landuse=residential'],
    "office_complex":   ['office=company'],
}


def _build_overpass_query(lat: float, lng: float, radius: int, tags: list[str]) -> str:
    parts = []
    for tag in tags:
        key, _, val = tag.partition("=")
        if val:
            parts.append(f'node["{key}"="{val}"](around:{radius},{lat},{lng});')
            parts.append(f'way["{key}"="{val}"](around:{radius},{lat},{lng});')
        else:
            parts.append(f'node["{key}"](around:{radius},{lat},{lng});')
    return f"[out:json][timeout:30];({' '.join(parts)});out center 60;"


async def _run_query(query: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(OVERPASS_URL, data={"data": query})
        resp.raise_for_status()
        elements = resp.json().get("elements", [])
        results = []
        for el in elements:
            tags = el.get("tags", {})
            if el["type"] == "node":
                lat, lng = el.get("lat"), el.get("lon")
            else:
                center = el.get("center", {})
                lat, lng = center.get("lat"), center.get("lon")
            if not lat or not lng:
                continue
            results.append({
                "place_id": f"osm-{el['type']}-{el['id']}",
                "name": tags.get("name", "Unnamed"),
                "latitude": lat,
                "longitude": lng,
                "address": _build_address(tags),
                "rating": None,  # OSM has no ratings
                "review_count": None,
                "price_level": None,
                "google_types": [],
                "is_open_now": None,
                "osm_tags": tags,
            })
        return results


def _build_address(tags: dict) -> str:
    parts = [tags.get("addr:housenumber", ""), tags.get("addr:street", ""), tags.get("addr:city", "")]
    return ", ".join(p for p in parts if p) or ""


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((phi2 - phi1) / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(math.radians(lng2 - lng1) / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class OverpassClient:

    async def collect_competitors(self, lat: float, lng: float, radius: int, queries: list[str]) -> list[dict]:
        seen: dict[str, dict] = {}
        tasks = []
        for q in queries:
            tags = OSM_TAG_MAP.get(q.lower(), [f'name~"{q}",i'])
            query = _build_overpass_query(lat, lng, radius, tags)
            tasks.append(_run_query(query))

        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        for results in results_list:
            if isinstance(results, Exception):
                continue
            for place in results:
                pid = place["place_id"]
                if pid not in seen:
                    seen[pid] = place
        return list(seen.values())

    async def collect_signals(self, lat: float, lng: float, radius: int, signal_types: list[str]) -> list[dict]:
        seen: dict[str, dict] = {}
        tasks = []
        type_list = []
        for stype in signal_types:
            tags = OSM_TAG_MAP.get(stype.lower(), [])
            if not tags:
                continue
            query = _build_overpass_query(lat, lng, radius, tags)
            tasks.append(_run_query(query))
            type_list.append(stype)

        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        for stype, results in zip(type_list, results_list):
            if isinstance(results, Exception):
                continue
            for place in results:
                pid = place["place_id"]
                if pid not in seen:
                    place["signal_type"] = stype
                    seen[pid] = place
        return list(seen.values())

    def distance_meters(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        return _haversine(lat1, lng1, lat2, lng2)

    def distance_ring(self, meters: float) -> str:
        if meters <= 1000:
            return "0-1km"
        if meters <= 3000:
            return "1-3km"
        return "3-5km"


overpass_client = OverpassClient()
