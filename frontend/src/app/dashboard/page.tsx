"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { ArrowRight, BarChart3, Clock, MapPin, Plus } from "lucide-react";
import { api } from "@/lib/api";

function StatusChip({ status }: { status: string }) {
  const map: Record<string, string> = {
    queued: "bg-gray-100 text-gray-600",
    processing: "bg-yellow-100 text-yellow-700",
    completed: "bg-green-100 text-green-700",
    failed: "bg-red-100 text-red-700",
  };
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${map[status] || "bg-gray-100 text-gray-600"}`}>
      {status}
    </span>
  );
}

export default function DashboardPage() {
  const { data: analyses } = useQuery({
    queryKey: ["analyses"],
    queryFn: () => api.get("/v1/analyses").then((r) => r.data).catch(() => []),
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="border-b border-gray-100 bg-white sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <span className="text-xl font-bold text-brand-700">BLIP</span>
          <Link href="/analyze" className="btn-primary text-sm py-2 px-4">
            <Plus size={16} /> New Analysis
          </Link>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-4 py-10">
        <h1 className="text-2xl font-bold text-gray-900 mb-8">My Analyses</h1>

        {!analyses || analyses.length === 0 ? (
          <div className="card text-center py-20">
            <BarChart3 size={48} className="text-gray-300 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-700 mb-2">No analyses yet</h2>
            <p className="text-gray-500 mb-6">Analyse your first location to get started.</p>
            <Link href="/analyze" className="btn-primary inline-flex">
              Start Analysis <ArrowRight size={16} />
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {analyses.map((a: any) => (
              <Link key={a.id} href={`/report/${a.id}`} className="card hover:border-brand-300 hover:shadow-md transition-all group">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2 text-gray-600 text-sm">
                    <MapPin size={14} />
                    <span>Location analysis</span>
                  </div>
                  <StatusChip status={a.status} />
                </div>
                <p className="text-sm text-gray-500 flex items-center gap-1 mt-2">
                  <Clock size={12} />
                  {new Date(a.created_at).toLocaleDateString("en-IN")}
                </p>
                <div className="mt-4 flex items-center gap-2 text-brand-600 text-sm font-medium group-hover:gap-3 transition-all">
                  View Report <ArrowRight size={14} />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
