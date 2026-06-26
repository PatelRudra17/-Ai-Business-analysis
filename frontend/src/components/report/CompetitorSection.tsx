"use client";

import { Star, MapPin } from "lucide-react";

interface Competitor {
  place_id: string;
  name: string;
  rating?: number;
  review_count?: number;
  distance_meters?: number;
  price_level?: number;
  address?: string;
}

interface Props {
  competitors: Competitor[];
  count: number;
  avg_rating: number;
  weak_themes: string[];
  analysis_text?: string;
}

const PRICE_LABEL: Record<number, string> = { 1: "₹", 2: "₹₹", 3: "₹₹₹", 4: "₹₹₹₹" };

export function CompetitorSection({ competitors, count, avg_rating, weak_themes, analysis_text }: Props) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-4 text-center">
        <div className="bg-gray-50 rounded-xl p-4">
          <div className="text-2xl font-bold text-gray-900">{count}</div>
          <div className="text-xs text-gray-500 mt-1">Competitors Found</div>
        </div>
        <div className="bg-gray-50 rounded-xl p-4">
          <div className="text-2xl font-bold text-gray-900">{avg_rating?.toFixed(1) || "—"}</div>
          <div className="text-xs text-gray-500 mt-1">Avg. Rating</div>
        </div>
        <div className="bg-gray-50 rounded-xl p-4">
          <div className="text-2xl font-bold text-gray-900">{weak_themes.length}</div>
          <div className="text-xs text-gray-500 mt-1">Review Weaknesses</div>
        </div>
      </div>

      {analysis_text && <p className="text-sm text-gray-600">{analysis_text}</p>}

      {weak_themes.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-gray-500 mb-2">Common complaints at competitors:</p>
          <div className="flex flex-wrap gap-2">
            {weak_themes.map((t) => (
              <span key={t} className="px-2 py-1 bg-red-50 text-red-700 rounded-full text-xs font-medium capitalize">
                {t.replace(/_/g, " ")}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-2 mt-4">
        {competitors.map((c) => (
          <div key={c.place_id} className="flex items-center justify-between py-2 border-b border-gray-50">
            <div>
              <p className="text-sm font-medium text-gray-900">{c.name}</p>
              {c.address && <p className="text-xs text-gray-400 flex items-center gap-1"><MapPin size={10} />{c.address}</p>}
            </div>
            <div className="text-right shrink-0 ml-4">
              {c.rating && (
                <p className="flex items-center gap-1 text-sm text-yellow-600 justify-end">
                  <Star size={12} fill="currentColor" /> {c.rating}
                  <span className="text-gray-400 text-xs">({c.review_count})</span>
                </p>
              )}
              <div className="flex items-center gap-2 justify-end mt-0.5">
                {c.price_level && <span className="text-xs text-gray-400">{PRICE_LABEL[c.price_level]}</span>}
                {c.distance_meters && <span className="text-xs text-gray-400">{(c.distance_meters / 1000).toFixed(1)} km</span>}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
