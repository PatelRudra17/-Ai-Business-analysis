"use client";

import { CheckCircle, AlertCircle } from "lucide-react";

interface Gap {
  gap_type: string;
  opportunity_score: number;
  confidence: number;
  supporting_signals: string[];
  limitations: string[];
  explanation?: string;
}

interface Props { gaps: Gap[]; }

export function GapFinderSection({ gaps }: Props) {
  if (!gaps || gaps.length === 0) {
    return <p className="text-gray-500 text-sm">No significant market gaps identified in this area.</p>;
  }

  return (
    <div className="space-y-4">
      {gaps.map((gap) => (
        <div key={gap.gap_type} className="border border-gray-100 rounded-xl p-4">
          <div className="flex items-start justify-between mb-3">
            <h4 className="font-semibold text-gray-900 capitalize">{gap.gap_type.replace(/_/g, " ")}</h4>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-brand-700">{gap.opportunity_score.toFixed(0)}/100</span>
              <span className="text-xs text-gray-400">{(gap.confidence * 100).toFixed(0)}% confidence</span>
            </div>
          </div>

          {gap.explanation && <p className="text-sm text-gray-600 mb-3">{gap.explanation}</p>}

          <div className="space-y-1 mb-3">
            {gap.supporting_signals.filter(Boolean).map((s, i) => (
              <div key={i} className="flex items-start gap-2 text-sm text-gray-700">
                <CheckCircle size={14} className="text-green-500 shrink-0 mt-0.5" />
                {s}
              </div>
            ))}
          </div>

          {gap.limitations.length > 0 && (
            <div className="bg-yellow-50 rounded-lg px-3 py-2">
              {gap.limitations.map((l, i) => (
                <div key={i} className="flex items-start gap-2 text-xs text-yellow-700">
                  <AlertCircle size={12} className="shrink-0 mt-0.5" />
                  {l}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
