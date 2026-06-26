"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { AlertCircle, ArrowLeft, CheckCircle, Clock, Download, Loader2, Lock } from "lucide-react";
import Link from "next/link";
import toast from "react-hot-toast";
import { api } from "@/lib/api";
import { ScoreGauge } from "@/components/ScoreGauge";
import { ConfidenceBadge } from "@/components/ConfidenceBadge";
import { CompetitorMap } from "@/components/CompetitorMap";
import { CompetitorSection } from "@/components/report/CompetitorSection";
import { GapFinderSection } from "@/components/report/GapFinderSection";
import { FinancialSection } from "@/components/report/FinancialSection";
import { PaymentModal } from "@/components/PaymentModal";
import { decisionColor, decisionLabel } from "@/lib/utils";

const PIPELINE_STEPS = [
  "Collecting competitor data",
  "Analysing demand signals",
  "Extracting review weaknesses",
  "Running Gap Finder",
  "Calculating Opportunity Score",
  "Running financial scenarios",
  "Writing report with AI",
  "Generating PDF",
];

function ProcessingView({ status }: { status: string }) {
  return (
    <div className="card text-center py-16">
      <Loader2 size={48} className="animate-spin text-brand-600 mx-auto mb-4" />
      <h2 className="text-xl font-bold text-gray-900">Analysing your location…</h2>
      <p className="text-gray-500 mt-2 mb-8">This takes 1-2 minutes. You can stay on this page.</p>
      <div className="max-w-xs mx-auto space-y-3 text-left">
        {PIPELINE_STEPS.map((step, i) => (
          <div key={step} className="flex items-center gap-3 text-sm">
            {i < 3 ? <CheckCircle size={16} className="text-green-500 shrink-0" /> : <Clock size={16} className="text-gray-300 shrink-0" />}
            <span className={i < 3 ? "text-gray-900" : "text-gray-400"}>{step}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function FailedView() {
  return (
    <div className="card text-center py-16">
      <AlertCircle size={48} className="text-red-500 mx-auto mb-4" />
      <h2 className="text-xl font-bold text-gray-900">Analysis Failed</h2>
      <p className="text-gray-500 mt-2">Something went wrong. Please try a new analysis.</p>
      <Link href="/analyze" className="btn-primary mt-6 inline-flex">Try Again</Link>
    </div>
  );
}

function ReportSection({ title, children, locked }: { title: string; children: React.ReactNode; locked?: boolean }) {
  return (
    <div className="card">
      <h3 className="text-lg font-bold text-gray-900 mb-4">{title}</h3>
      {locked ? (
        <div className="flex items-center justify-center gap-3 py-10 bg-gray-50 rounded-xl border border-dashed border-gray-200">
          <Lock size={18} className="text-gray-400" />
          <span className="text-gray-500 text-sm">Unlock the full report to view this section</span>
        </div>
      ) : children}
    </div>
  );
}

export default function ReportPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const queryClient = useQueryClient();
  const [showPayment, setShowPayment] = useState(false);

  const { data: statusData, isLoading: statusLoading } = useQuery({
    queryKey: ["analysis-status", id],
    queryFn: () => api.get(`/v1/analyses/${id}/status`).then((r) => r.data),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "completed" || status === "failed" ? false : 3000;
    },
  });

  const { data: report } = useQuery({
    queryKey: ["report", id],
    queryFn: () => api.get(`/v1/analyses/${id}/report`).then((r) => r.data),
    enabled: statusData?.status === "completed",
  });

  const { data: financials } = useQuery({
    queryKey: ["financials", id],
    queryFn: () => api.get(`/v1/analyses/${id}/financials`).then((r) => r.data).catch(() => null),
    enabled: report?.is_free_preview === false,
  });

  if (statusLoading) {
    return <div className="min-h-screen flex items-center justify-center"><Loader2 size={40} className="animate-spin text-brand-600" /></div>;
  }

  const status = statusData?.status;
  const exec = report?.executive_summary || {};
  const isPaid = report && !report.is_free_preview;
  const competitors = report?.competitor_landscape?.competitors || [];
  const center = { lat: 23.033, lng: 72.465 }; // placeholder — real: from analysis job

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="border-b border-gray-100 bg-white sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button onClick={() => router.back()} className="text-gray-500 hover:text-gray-700"><ArrowLeft size={20} /></button>
            <span className="font-bold text-brand-700">BLIP</span>
            <span className="text-gray-300">·</span>
            <span className="text-gray-600 text-sm">Location Report</span>
          </div>
          {report?.pdf_url && (
            <a href={report.pdf_url} target="_blank" rel="noopener noreferrer" className="btn-secondary text-sm py-1.5">
              <Download size={14} /> Download PDF
            </a>
          )}
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 py-10 space-y-6">
        {status === "failed" && <FailedView />}
        {(status === "queued" || status === "processing") && <ProcessingView status={status} />}

        {status === "completed" && report && (
          <>
            {/* Executive Summary */}
            <div className="card">
              <div className="flex items-start justify-between gap-4 mb-4 flex-wrap">
                <div>
                  <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold border ${decisionColor(exec.decision || "")}`}>
                    {decisionLabel(exec.decision || "")}
                  </span>
                  <p className="text-gray-600 mt-3 max-w-2xl">{exec.decision_summary}</p>
                </div>
                <ConfidenceBadge score={exec.confidence || 0} />
              </div>
              <div className="grid grid-cols-2 gap-6">
                <ScoreGauge label="Opportunity Score" score={exec.score || 0} color="brand" />
                <ScoreGauge label="Risk Score" score={exec.risk_score || 0} color="danger" />
              </div>
              {exec.best_gap && (
                <div className="mt-4 p-4 bg-green-50 rounded-xl border border-green-100">
                  <p className="text-sm font-semibold text-green-800">Best Gap Identified</p>
                  <p className="text-green-700 mt-1 capitalize">{exec.best_gap}</p>
                </div>
              )}
              {exec.main_risk && (
                <div className="mt-3 p-4 bg-red-50 rounded-xl border border-red-100">
                  <p className="text-sm font-semibold text-red-800">Main Risk</p>
                  <p className="text-red-700 mt-1">{exec.main_risk}</p>
                </div>
              )}
              {exec.next_action && (
                <div className="mt-3 p-4 bg-blue-50 rounded-xl border border-blue-100">
                  <p className="text-sm font-semibold text-blue-800">Recommended Next Action</p>
                  <p className="text-blue-700 mt-1">{exec.next_action}</p>
                </div>
              )}
            </div>

            {/* Competitor Map */}
            {competitors.length > 0 && (
              <ReportSection title={`Competitor Map (${competitors.length} found)`}>
                <CompetitorMap center={center} competitors={competitors} radiusMeters={3000} />
              </ReportSection>
            )}

            {/* Competitor Analysis */}
            <ReportSection title="Competitor Landscape" locked={report.competitor_landscape?.locked && !isPaid}>
              {report.competitor_landscape && !report.competitor_landscape.locked && (
                <CompetitorSection
                  competitors={competitors}
                  count={report.competitor_landscape.count || 0}
                  avg_rating={report.competitor_landscape.avg_rating || 0}
                  weak_themes={report.competitor_landscape.weak_themes || []}
                  analysis_text={report.competitor_landscape.analysis_text}
                />
              )}
            </ReportSection>

            {/* Demand Indicators */}
            <ReportSection title="Demand Indicators">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="bg-gray-50 rounded-xl p-4">
                  <div className="text-xl font-bold text-gray-900">{report.demand_indicators?.signals_0_1km || 0}</div>
                  <div className="text-xs text-gray-500 mt-1">Signals 0-1 km</div>
                </div>
                <div className="bg-gray-50 rounded-xl p-4">
                  <div className="text-xl font-bold text-gray-900">{report.demand_indicators?.signals_1_3km || 0}</div>
                  <div className="text-xs text-gray-500 mt-1">Signals 1-3 km</div>
                </div>
                <div className="bg-gray-50 rounded-xl p-4">
                  <div className="text-xl font-bold text-gray-900">{report.demand_indicators?.signals_3_5km || 0}</div>
                  <div className="text-xs text-gray-500 mt-1">Signals 3-5 km</div>
                </div>
              </div>
              {report.demand_indicators?.analysis_text && (
                <p className="text-sm text-gray-600 mt-4">{report.demand_indicators.analysis_text}</p>
              )}
            </ReportSection>

            {/* Gap Finder */}
            <ReportSection title="Gap Finder" locked={report.gap_finder?.locked && !isPaid}>
              {report.gap_finder && !report.gap_finder.locked && (
                <GapFinderSection gaps={report.gap_finder.gaps || []} />
              )}
            </ReportSection>

            {/* Micro-Zones */}
            {report.micro_zones?.length > 0 && (
              <ReportSection title="Recommended Micro-Zones" locked={!isPaid}>
                {isPaid && (
                  <div className="space-y-3">
                    {report.micro_zones.map((z: any) => (
                      <div key={z.label} className="border border-gray-100 rounded-xl p-4">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-semibold text-gray-900">{z.label} — {z.direction}</span>
                          <span className="text-xs text-gray-400">{z.nearby_competitors} competitors nearby</span>
                        </div>
                        <p className="text-sm text-gray-600">{z.rationale}</p>
                      </div>
                    ))}
                  </div>
                )}
              </ReportSection>
            )}

            {/* Financial Scenarios */}
            <ReportSection title="Financial Scenarios" locked={!isPaid}>
              {isPaid && financials && <FinancialSection scenarios={financials} />}
            </ReportSection>

            {/* Marketing Strategy */}
            <ReportSection title="Marketing Strategy" locked={report.marketing_strategy?.locked && !isPaid}>
              {isPaid && report.marketing_strategy && !report.marketing_strategy.locked && (
                <div className="space-y-4">
                  {report.marketing_strategy.positioning && (
                    <div className="bg-brand-50 rounded-xl p-4">
                      <p className="text-sm font-semibold text-brand-800 mb-1">Positioning</p>
                      <p className="text-brand-700">{report.marketing_strategy.positioning}</p>
                    </div>
                  )}
                  {report.marketing_strategy.channels && (
                    <div>
                      <p className="text-sm font-semibold text-gray-700 mb-2">Recommended Channels</p>
                      <ul className="space-y-1">
                        {report.marketing_strategy.channels.map((c: string, i: number) => (
                          <li key={i} className="flex items-center gap-2 text-sm text-gray-600">
                            <CheckCircle size={14} className="text-green-500" /> {c}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </ReportSection>

            {/* 30-Day Launch Plan */}
            {isPaid && report.launch_plan?.length > 0 && (
              <ReportSection title="30-Day Launch Plan">
                <div className="space-y-4">
                  {report.launch_plan.map((week: any) => (
                    <div key={week.week}>
                      <p className="text-sm font-semibold text-gray-700 mb-2">Week {week.week}: {week.theme}</p>
                      <ul className="space-y-1">
                        {week.tasks?.map((t: string, i: number) => (
                          <li key={i} className="flex items-center gap-2 text-sm text-gray-600">
                            <Clock size={12} className="text-gray-400 shrink-0" /> {t}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </ReportSection>
            )}

            {/* Limitations */}
            {report.limitations?.length > 0 && (
              <ReportSection title="Limitations & Assumptions">
                <ul className="space-y-2">
                  {report.limitations.map((l: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                      <AlertCircle size={14} className="text-yellow-500 shrink-0 mt-0.5" /> {l}
                    </li>
                  ))}
                </ul>
              </ReportSection>
            )}

            {/* Unlock CTA */}
            {!isPaid && (
              <div className="card text-center py-10 bg-brand-50 border-brand-100">
                <Lock size={32} className="text-brand-500 mx-auto mb-3" />
                <h3 className="text-xl font-bold text-gray-900 mb-2">Unlock the Full Report</h3>
                <p className="text-gray-600 mb-6">Complete competitor analysis · Gap Finder · Financial scenarios · Micro-zones · Marketing plan · PDF</p>
                <button onClick={() => setShowPayment(true)} className="btn-primary text-base px-8 py-3">
                  Unlock for ₹999
                </button>
                <p className="text-xs text-gray-400 mt-3">One-time payment · Instant access · Razorpay secured</p>
              </div>
            )}

            {/* Compare CTA */}
            <div className="card flex items-center justify-between gap-4 flex-wrap">
              <div>
                <p className="font-semibold text-gray-900">Compare with another location</p>
                <p className="text-sm text-gray-500">See how two locations score side by side.</p>
              </div>
              <Link href={`/compare?a=${id}`} className="btn-secondary text-sm">Compare Locations</Link>
            </div>
          </>
        )}
      </div>

      {showPayment && (
        <PaymentModal
          analysisId={id}
          onUnlocked={() => {
            setShowPayment(false);
            queryClient.invalidateQueries({ queryKey: ["report", id] });
            queryClient.invalidateQueries({ queryKey: ["financials", id] });
            toast.success("Report unlocked!");
          }}
          onClose={() => setShowPayment(false)}
        />
      )}
    </div>
  );
}
