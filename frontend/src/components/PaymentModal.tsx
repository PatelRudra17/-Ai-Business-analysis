"use client";

import { useState } from "react";
import { Loader2, Lock, X } from "lucide-react";
import toast from "react-hot-toast";
import { api } from "@/lib/api";

interface Props {
  analysisId: string;
  onUnlocked: () => void;
  onClose: () => void;
}

declare global {
  interface Window {
    Razorpay: any;
  }
}

export function PaymentModal({ analysisId, onUnlocked, onClose }: Props) {
  const [loading, setLoading] = useState(false);

  const handlePay = async () => {
    setLoading(true);
    try {
      const { data: order } = await api.post("/v1/payments/orders", {
        analysis_id: analysisId,
        product: "single_report",
      });

      const rzp = new window.Razorpay({
        key: order.key_id,
        amount: order.amount_paise,
        currency: "INR",
        name: "BLIP",
        description: "Location Intelligence Report",
        order_id: order.order_id,
        handler: async (response: any) => {
          await api.post("/v1/payments/verify", {
            order_id: response.razorpay_order_id,
            payment_id: response.razorpay_payment_id,
            signature: response.razorpay_signature,
            analysis_id: analysisId,
          });
          toast.success("Payment successful! Full report unlocked.");
          onUnlocked();
        },
        prefill: {},
        theme: { color: "#4f46e5" },
      });
      rzp.open();
    } catch {
      toast.error("Could not initiate payment. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-8 relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
          <X size={20} />
        </button>
        <div className="text-center">
          <div className="w-16 h-16 bg-brand-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Lock size={28} className="text-brand-600" />
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Unlock Full Report</h2>
          <p className="text-gray-500 mb-6">Get complete competitor analysis, Gap Finder, financial scenarios, micro-zones, and 30-day launch plan.</p>

          <div className="bg-gray-50 rounded-xl p-4 mb-6 text-left space-y-2">
            {["Complete competitor list with all details", "Gap Finder — market opportunities", "3 financial scenarios + break-even", "3 recommended micro-zones", "Marketing strategy", "30-day launch plan", "Downloadable PDF"].map((f) => (
              <div key={f} className="flex items-center gap-2 text-sm text-gray-700">
                <span className="text-green-500">✓</span> {f}
              </div>
            ))}
          </div>

          <div className="text-3xl font-bold text-gray-900 mb-1">₹999</div>
          <p className="text-gray-400 text-sm mb-6">One-time payment · Instant access</p>

          <button onClick={handlePay} disabled={loading} className="btn-primary w-full justify-center text-base py-3">
            {loading ? <Loader2 size={18} className="animate-spin" /> : "Pay & Unlock — ₹999"}
          </button>
          <p className="text-xs text-gray-400 mt-3">Secured by Razorpay · All major cards, UPI, and net banking accepted</p>
        </div>
      </div>
    </div>
  );
}
