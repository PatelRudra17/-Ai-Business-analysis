"""
Nominatim — free OpenStreetMap geocoding.
No API key. Limit: 1 request/second (add delay between calls).
"""
import asyncio
import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "BLIP-BusinessLocationPlatform/1.0 (contact@blip.in)"}


async def geocode(address: str) -> dict | None:
    await asyncio.sleep(1)  # respect 1 req/sec limit
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
        "countrycodes": "in",
    }
    async with httpx.AsyncClient(timeout=10, headers=HEADERS) as client:
        resp = await client.get(NOMINATIM_URL, params=params)
        resp.raise_for_status()
        results = resp.json()
        if not results:
            return None
        r = results[0]
        addr = r.get("address", {})
        return {
            "display_name": r.get("display_name", ""),
            "latitude": float(r["lat"]),
            "longitude": float(r["lon"]),
            "city": addr.get("city") or addr.get("town") or addr.get("village", ""),
            "state": addr.get("state", ""),
            "country": addr.get("country", "India"),
        }


async def reverse_geocode(lat: float, lng: float) -> dict | None:
    await asyncio.sleep(1)
    async with httpx.AsyncClient(timeout=10, headers=HEADERS) as client:
        resp = await client.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lng, "format": "json", "addressdetails": 1},
        )
        resp.raise_for_status()
        r = resp.json()
        addr = r.get("address", {})
        return {
            "display_name": r.get("display_name", ""),
            "city": addr.get("city") or addr.get("town") or addr.get("village", ""),
            "state": addr.get("state", ""),
        }
