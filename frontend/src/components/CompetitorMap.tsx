"use client";

import { useEffect, useRef } from "react";

interface Competitor {
  place_id: string;
  name: string;
  latitude: number;
  longitude: number;
  rating?: number;
  review_count?: number;
  distance_meters?: number;
}

interface Props {
  center: { lat: number; lng: number };
  competitors: Competitor[];
  radiusMeters?: number;
}

function ratingColor(rating?: number): string {
  if (!rating) return "#9ca3af";
  if (rating >= 4) return "#22c55e";
  if (rating >= 3) return "#f59e0b";
  return "#ef4444";
}

export function CompetitorMap({ center, competitors, radiusMeters = 3000 }: Props) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<any>(null);

  useEffect(() => {
    if (!mapRef.current || mapInstance.current) return;

    // Dynamically load Leaflet CSS + JS (no API key needed — OpenStreetMap)
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
    document.head.appendChild(link);

    const script = document.createElement("script");
    script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
    script.onload = () => initMap();
    document.head.appendChild(script);

    function initMap() {
      const L = (window as any).L;
      if (!mapRef.current) return;

      const map = L.map(mapRef.current).setView([center.lat, center.lng], 14);
      mapInstance.current = map;

      // Free OpenStreetMap tiles
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
      }).addTo(map);

      // Radius circle
      L.circle([center.lat, center.lng], {
        radius: radiusMeters,
        color: "#6366f1",
        fillColor: "#6366f120",
        fillOpacity: 0.2,
        weight: 2,
      }).addTo(map);

      // Center pin (your location)
      const centerIcon = L.divIcon({
        html: `<div style="width:14px;height:14px;border-radius:50%;background:#4f46e5;border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.3)"></div>`,
        iconSize: [14, 14],
        className: "",
      });
      L.marker([center.lat, center.lng], { icon: centerIcon })
        .addTo(map)
        .bindPopup("<b>Your proposed location</b>");

      // Competitor pins
      competitors.forEach((c) => {
        const color = ratingColor(c.rating);
        const icon = L.divIcon({
          html: `<div style="width:10px;height:10px;border-radius:50%;background:${color};border:2px solid white;box-shadow:0 1px 4px rgba(0,0,0,0.25);cursor:pointer"></div>`,
          iconSize: [10, 10],
          className: "",
        });
        const km = c.distance_meters ? `${(c.distance_meters / 1000).toFixed(1)} km` : "";
        const ratingStr = c.rating ? `⭐ ${c.rating} (${c.review_count || 0} reviews)` : "No rating";
        L.marker([c.latitude, c.longitude], { icon })
          .addTo(map)
          .bindPopup(`<b>${c.name}</b><br>${ratingStr}<br>${km}`);
      });
    }

    return () => {
      if (mapInstance.current) {
        mapInstance.current.remove();
        mapInstance.current = null;
      }
    };
  }, [center.lat, center.lng]);

  return (
    <div className="space-y-2">
      <div ref={mapRef} className="h-[400px] rounded-xl overflow-hidden border border-gray-200 z-0" />
      <div className="flex items-center gap-4 text-xs text-gray-500">
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-green-500 inline-block" /> Rating ≥ 4</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-yellow-500 inline-block" /> Rating 3–4</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-gray-400 inline-block" /> No rating</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-brand-600 inline-block" /> Your location</span>
        <span className="text-gray-400">· Map: © OpenStreetMap</span>
      </div>
    </div>
  );
}
