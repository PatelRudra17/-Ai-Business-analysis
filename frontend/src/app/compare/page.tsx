"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeftRight, Loader2, Trophy } from "lucide-react";
import toast from "react-hot-toast";
import Link from "next/link";
import { api } from "@/lib/api";
import { ScoreGauge } from "@/components/ScoreGauge";
import { decisionLabel } from "@/lib/utils";

const schema = z.object({
  analysis_id_a: z.string().uuid("Enter a valid analysis ID"),
  analysis_id_b: z.string().uuid("Enter a valid analysis ID"),
});
type Form = z.infer<typeof schema>;

interface ComparisonResult {
  analysis_a: { analysis_id: string; opportunity_score: number; risk_score: number; confidence: number; decision: string };
  analysis_b: { analysis_id: string; opportunity_score: number; risk_score: number; confidence: number; decision: string };
  winner: "a" | "b" | "tie";
  recommendation: string;
  score_diff: number;
}

export default function ComparePage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ComparisonResult | null>(null);

  const { register, handleSubmit, formState: { errors } } = useForm<Form>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: Form) => {
    setLoading(true);
    try {
      const res = await api.post("/v1/comparisons", data);
      setResult(res.data);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Comparison failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="border-b border-gray-100 bg-white sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 h-16 flex items-center justify-between">
          <Link href="/dashboard" className="text-xl font-bold text-brand-700">BLIP</Link>
          <span className="text-gray-600 text-sm">Location Comparison</span>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 py-10">
        <div className="card mb-8">
          <h1 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <ArrowLeftRight size={20} className="text-brand-600" /> Compare Two Locations
          </h1>
          <form onSubmit={handleSubmit(onSubmit)} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Location A — Analysis ID</label>
              <input {...register("analysis_id_a")} placeholder="Paste analysis ID"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
              {errors.analysis_id_a && <p className="text-red-500 text-xs mt-1">{errors.analysis_id_a.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Location B — Analysis ID</label>
              <input {...register("analysis_id_b")} placeholder="Paste analysis ID"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
              {errors.analysis_id_b && <p className="text-red-500 text-xs mt-1">{errors.analysis_id_b.message}</p>}
            </div>
            <div className="sm:col-span-2">
              <button type="submit" disabled={loading} className="btn-primary">
                {loading ? <Loader2 size={16} className="animate-spin" /> : <><ArrowLeftRight size={16} /> Compare Locations</>}
              </button>
            </div>
          </form>
        </div>

        {result && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {(["a", "b"] as const).map((side) => {
              const data = result[`analysis_${side}`];
              const isWinner = result.winner === side;
              return (
                <div key={side} className={`card relative ${isWinner ? "border-brand-300 ring-2 ring-brand-200" : ""}`}>
                  {isWinner && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-brand-600 text-white text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1">
                      <Trophy size={12} /> Recommended
                    </div>
                  )}
                  <h3 className="font-bold text-gray-900 mb-4">Location {side.toUpperCase()}</h3>
                  <div className="space-y-3">
                    <ScoreGauge label="Opportunity Score" score={data.opportunity_score} color="brand" />
                    <ScoreGauge label="Risk Score" score={data.risk_score} color="danger" />
                  </div>
                  <p className="text-xs text-gray-500 mt-4 capitalize">{decisionLabel(data.decision)}</p>
                  <Link href={`/report/${data.analysis_id}`} className="mt-3 text-brand-600 text-sm font-medium hover:underline block">
                    View full report →
                  </Link>
                </div>
              );
            })}
            <div className="sm:col-span-2 card bg-brand-50 border-brand-100">
              <p className="text-gray-800 font-medium">{result.recommendation}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
