"use client";

interface Props { score: number; }

export function ConfidenceBadge({ score }: Props) {
  const pct = Math.round(score || 0);

  if (pct >= 80) return <span className="badge-high">High confidence · {pct}%</span>;
  if (pct >= 60) return <span className="badge-medium">Moderate confidence · {pct}%</span>;
  if (pct >= 40) return <span className="badge-low">Limited confidence · {pct}%</span>;
  return <span className="badge-low">Insufficient data · {pct}%</span>;
}
