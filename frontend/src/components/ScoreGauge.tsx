"use client";

interface Props {
  label: string;
  score: number;
  color: "brand" | "danger" | "warning";
}

const COLOR_MAP = {
  brand:   { bar: "bg-brand-600",  text: "text-brand-700"  },
  danger:  { bar: "bg-red-500",    text: "text-red-700"    },
  warning: { bar: "bg-yellow-500", text: "text-yellow-700" },
};

export function ScoreGauge({ label, score, color }: Props) {
  const pct = Math.min(100, Math.max(0, score || 0));
  const { bar, text } = COLOR_MAP[color];

  return (
    <div>
      <div className="flex items-end justify-between mb-1">
        <span className="text-sm font-medium text-gray-600">{label}</span>
        <span className={`text-2xl font-bold ${text}`}>{Math.round(pct)}</span>
      </div>
      <div className="h-2.5 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all duration-700 ${bar}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
