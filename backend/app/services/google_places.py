"""Google Places API client — competitor and demand signal collection."""
import asyncio
import math
from typing import Any

import httpx

from app.config import settings

BASE = "https://maps.googleapis.com/maps/api/place"


class GooglePlacesClient:
    def __init__(self):
        self.key = settings.GOOGLE_MAPS_API_KEY

    async def nearby_search(self, lat: float, lng: float, radius: int, keyword: str) -> list[dict]:
        results = []
        next_page_token = None
        async with httpx.AsyncClient(timeout=15) as client:
            for _ in range(3):  # max 3 pages = 60 results
                params = {
                    "location": f"{lat},{lng}",
                    "radius": radius,
                    "keyword": keyword,
                    "key": self.key,
                }
                if next_page_token:
                    params = {"pagetoken": next_page_token, "key": self.key}
                    await asyncio.sleep(2)  # required delay for next_page_token
                resp = await client.get(f"{BASE}/nearbysearch/json", params=params)
                data = resp.json()
                results.extend(data.get("results", []))
                next_page_token = data.get("next_page_token")
                if not next_page_token:
                    break
        return results

    async def place_details(self, place_id: str) -> dict:
        fields = "place_id,name,formatted_address,geometry,rating,user_ratings_total,price_level,opening_hours,formatted_phone_number,website,reviews,types"
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{BASE}/details/json",
                params={"place_id": place_id, "fields": fields, "key": self.key},
            )
            return resp.json().get("result", {})

    async def collect_competitors(
        self, lat: float, lng: float, radius: int, queries: list[str]
    ) -> list[dict]:
        all_results: dict[str, dict] = {}
        tasks = [self.nearby_search(lat, lng, radius, q) for q in queries]
        batches = await asyncio.gather(*tasks, return_exceptions=True)
        for batch in batches:
            if isinstance(batch, Exception):
                continue
            for place in batch:
                pid = place.get("place_id")
                if pid and pid not in all_results:
                    all_results[pid] = self._normalize_nearby(place)
        return list(all_results.values())

    async def collect_signals(
        self, lat: float, lng: float, radius: int, signal_types: list[str]
    ) -> list[dict]:
        all_results: dict[str, dict] = {}
        tasks = [self.nearby_search(lat, lng, radius, s) for s in signal_types]
        batches = await asyncio.gather(*tasks, return_exceptions=True)
        for batch, signal_type in zip(batches, signal_types):
            if isinstance(batch, Exception):
                continue
            for place in batch:
                pid = place.get("place_id")
                if pid and pid not in all_results:
                    norm = self._normalize_nearby(place)
                    norm["signal_type"] = signal_type
                    all_results[pid] = norm
        return list(all_results.values())

    def _normalize_nearby(self, p: dict) -> dict:
        geo = p.get("geometry", {}).get("location", {})
        return {
            "place_id": p.get("place_id"),
            "name": p.get("name"),
            "latitude": geo.get("lat"),
            "longitude": geo.get("lng"),
            "address": p.get("vicinity"),
            "rating": p.get("rating"),
            "review_count": p.get("user_ratings_total"),
            "price_level": p.get("price_level"),
            "google_types": p.get("types", []),
            "is_open_now": p.get("opening_hours", {}).get("open_now"),
        }

    def distance_meters(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        R = 6371000
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lng2 - lng1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def distance_ring(self, meters: float) -> str:
        if meters <= 1000:
            return "0-1km"
        if meters <= 3000:
            return "1-3km"
        return "3-5km"


google_places = GooglePlacesClient()
