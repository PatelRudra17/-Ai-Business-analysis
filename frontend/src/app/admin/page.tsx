"use client";

import { useQuery } from "@tanstack/react-query";
import { BarChart3, IndianRupee, Users, Zap } from "lucide-react";
import { api } from "@/lib/api";
import { formatINR } from "@/lib/utils";

function StatCard({ icon: Icon, label, value, sub }: { icon: any; label: string; value: string; sub?: string }) {
  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-2">
        <div className="w-9 h-9 bg-brand-100 rounded-lg flex items-center justify-center">
          <Icon size={18} className="text-brand-600" />
        </div>
        <span className="text-sm text-gray-500">{label}</span>
      </div>
      <div className="text-2xl font-bold text-gray-900">{value}</div>
      {sub && <div className="text-xs text-gray-400 mt-1">{sub}</div>}
    </div>
  );
}

export default function AdminPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ["admin-stats"],
    queryFn: () => api.get("/v1/admin/stats").then((r) => r.data),
  });

  const { data: analyses } = useQuery({
    queryKey: ["admin-analyses"],
    queryFn: () => api.get("/v1/admin/analyses?limit=20").then((r) => r.data),
  });

  if (isLoading) return <div className="min-h-screen flex items-center justify-center text-gray-400">Loading…</div>;
  if (!stats) return <div className="min-h-screen flex items-center justify-center text-red-500">Unauthorized</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="border-b border-gray-100 bg-white sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <span className="text-xl font-bold text-brand-700">BLIP Admin</span>
        </div>
      </nav>
      <div className="max-w-6xl mx-auto px-4 py-10">
        <h1 className="text-2xl font-bold text-gray-900 mb-8">Dashboard</h1>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
          <StatCard icon={Users} label="Total Users" value={stats.users.total} />
          <StatCard icon={BarChart3} label="Analyses" value={stats.analyses.total}
            sub={`${stats.analyses.paid} paid · ${stats.analyses.conversion_rate_pct}% conversion`} />
          <StatCard icon={IndianRupee} label="Total Revenue" value={formatINR(stats.revenue.total_inr)} />
          <StatCard icon={Zap} label="AI Cost (30d)" value={`$${stats.ai_cost_30d.estimated_usd}`}
            sub={`${(stats.ai_cost_30d.input_tokens / 1000).toFixed(0)}k in / ${(stats.ai_cost_30d.output_tokens / 1000).toFixed(0)}k out`} />
        </div>

        <div className="card">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Recent Analyses</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left py-2 text-gray-500 font-medium">ID</th>
                  <th className="text-left py-2 text-gray-500 font-medium">Status</th>
                  <th className="text-left py-2 text-gray-500 font-medium">Paid</th>
                  <th className="text-left py-2 text-gray-500 font-medium">Created</th>
                </tr>
              </thead>
              <tbody>
                {analyses?.map((a: any) => (
                  <tr key={a.id} className="border-b border-gray-50">
                    <td className="py-2 text-gray-500 font-mono text-xs">{a.id.slice(0, 8)}…</td>
                    <td className="py-2">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                        a.status === "completed" ? "bg-green-100 text-green-700" :
                        a.status === "failed" ? "bg-red-100 text-red-700" :
                        "bg-yellow-100 text-yellow-700"
                      }`}>{a.status}</span>
                    </td>
                    <td className="py-2">{a.is_paid ? "✅" : "—"}</td>
                    <td className="py-2 text-gray-400">{new Date(a.created_at).toLocaleDateString("en-IN")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
