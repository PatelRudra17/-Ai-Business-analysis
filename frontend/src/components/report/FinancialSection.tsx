"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { formatINR } from "@/lib/utils";

interface Scenario {
  scenario_type: string;
  monthly_revenue: number;
  monthly_costs: number;
  monthly_profit: number;
  gross_margin_pct: number;
  break_even_months: number;
  break_even_customers_per_day: number;
}

interface Props { scenarios: Scenario[]; }

const COLORS = { conservative: "#f59e0b", expected: "#6366f1", optimistic: "#22c55e" };

export function FinancialSection({ scenarios }: Props) {
  const chartData = scenarios.map((s) => ({
    name: s.scenario_type.charAt(0).toUpperCase() + s.scenario_type.slice(1),
    Revenue: s.monthly_revenue,
    Costs: s.monthly_costs,
    Profit: s.monthly_profit,
  }));

  return (
    <div className="space-y-6">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100">
              <th className="text-left py-2 text-gray-500 font-medium">Scenario</th>
              <th className="text-right py-2 text-gray-500 font-medium">Monthly Revenue</th>
              <th className="text-right py-2 text-gray-500 font-medium">Monthly Costs</th>
              <th className="text-right py-2 text-gray-500 font-medium">Monthly Profit</th>
              <th className="text-right py-2 text-gray-500 font-medium">Break-Even</th>
            </tr>
          </thead>
          <tbody>
            {scenarios.map((s) => (
              <tr key={s.scenario_type} className="border-b border-gray-50">
                <td className="py-3 font-semibold capitalize" style={{ color: COLORS[s.scenario_type as keyof typeof COLORS] }}>
                  {s.scenario_type}
                </td>
                <td className="text-right py-3 text-gray-900">{formatINR(s.monthly_revenue)}</td>
                <td className="text-right py-3 text-gray-600">{formatINR(s.monthly_costs)}</td>
                <td className={`text-right py-3 font-semibold ${s.monthly_profit >= 0 ? "text-green-600" : "text-red-600"}`}>
                  {formatINR(s.monthly_profit)}
                </td>
                <td className="text-right py-3 text-gray-600">{s.break_even_months} months</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`} tick={{ fontSize: 11 }} />
            <Tooltip formatter={(v: number) => formatINR(v)} />
            <Legend />
            <Bar dataKey="Revenue" fill="#6366f1" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Costs" fill="#f87171" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Profit" fill="#22c55e" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <p className="text-xs text-gray-400">
        Financial scenarios use benchmark assumptions for Ahmedabad 2026. Validate with your actual costs before committing.
      </p>
    </div>
  );
}
