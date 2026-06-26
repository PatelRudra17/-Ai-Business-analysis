"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter, useSearchParams } from "next/navigation";
import { ArrowLeft, ArrowRight, Loader2, MapPin } from "lucide-react";
import toast from "react-hot-toast";
import { api } from "@/lib/api";

const schema = z.object({
  business_type: z.string().min(1, "Select a business category"),
  business_subtype: z.string().optional(),
  location_text: z.string().min(3, "Enter a location"),
  latitude: z.number(),
  longitude: z.number(),
  radius_meters: z.number().min(500).max(10000),
  total_investment: z.number().optional(),
  monthly_rent_limit: z.number().optional(),
  average_order_value: z.number().optional(),
  target_customer: z.string().optional(),
  parking_required: z.boolean(),
});

type FormData = z.infer<typeof schema>;

const CATEGORIES = [
  { slug: "gym",   name: "Gym & Fitness Studio", icon: "🏋️" },
  { slug: "cafe",  name: "Café & Restaurant",    icon: "☕" },
  { slug: "salon", name: "Salon & Beauty",        icon: "✂️" },
];

const RADIUS_OPTIONS = [
  { value: 1000, label: "1 km" },
  { value: 2000, label: "2 km" },
  { value: 3000, label: "3 km (recommended)" },
  { value: 5000, label: "5 km" },
];

export default function AnalyzePage() {
  const router = useRouter();
  const params = useSearchParams();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      business_type: params.get("category") || "",
      radius_meters: 3000,
      parking_required: false,
    },
  });

  const businessType = watch("business_type");

  const handleGeocode = async () => {
    const text = watch("location_text");
    if (!text) return;
    try {
      // Free Nominatim geocoding — no API key needed
      const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(text + ", Ahmedabad, India")}&format=json&limit=1&countrycodes=in`;
      const res = await fetch(url, { headers: { "User-Agent": "BLIP-App/1.0" } });
      const data = await res.json();
      if (data?.[0]) {
        setValue("latitude", parseFloat(data[0].lat));
        setValue("longitude", parseFloat(data[0].lon));
        setValue("location_text", data[0].display_name);
        toast.success("Location confirmed");
      } else {
        toast.error("Location not found. Try a more specific name.");
      }
    } catch {
      toast.error("Could not geocode location. Please try again.");
    }
  };

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    try {
      const res = await api.post("/v1/analyses", data);
      toast.success("Analysis started!");
      router.push(`/report/${res.data.analysis_id}`);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Failed to start analysis");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="border-b border-gray-100 bg-white sticky top-0 z-50">
        <div className="max-w-3xl mx-auto px-4 h-16 flex items-center gap-4">
          <button onClick={() => router.back()} className="text-gray-500 hover:text-gray-700">
            <ArrowLeft size={20} />
          </button>
          <span className="font-semibold text-gray-900">New Analysis</span>
        </div>
      </nav>

      <div className="max-w-3xl mx-auto px-4 py-10">
        {/* Step indicator */}
        <div className="flex items-center gap-2 mb-8">
          {[1, 2, 3].map((s) => (
            <div key={s} className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${step >= s ? "bg-brand-600 text-white" : "bg-gray-200 text-gray-500"}`}>
                {s}
              </div>
              {s < 3 && <div className={`h-0.5 w-16 ${step > s ? "bg-brand-600" : "bg-gray-200"}`} />}
            </div>
          ))}
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Step 1: Category */}
          {step === 1 && (
            <div className="card">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Select your business type</h2>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {CATEGORIES.map((cat) => (
                  <button
                    key={cat.slug}
                    type="button"
                    onClick={() => { setValue("business_type", cat.slug); setStep(2); }}
                    className={`p-4 rounded-xl border-2 text-left transition-all ${businessType === cat.slug ? "border-brand-600 bg-brand-50" : "border-gray-200 hover:border-brand-300"}`}
                  >
                    <div className="text-3xl mb-2">{cat.icon}</div>
                    <div className="font-semibold text-gray-900">{cat.name}</div>
                  </button>
                ))}
              </div>
              {errors.business_type && <p className="text-red-500 text-sm mt-2">{errors.business_type.message}</p>}
            </div>
          )}

          {/* Step 2: Location */}
          {step === 2 && (
            <div className="card">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Where is your proposed location?</h2>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Area or address</label>
                <div className="flex gap-2">
                  <input
                    {...register("location_text")}
                    placeholder="e.g. Bopal, Ahmedabad"
                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                  <button type="button" onClick={handleGeocode} className="btn-secondary text-sm py-2">
                    <MapPin size={16} /> Confirm
                  </button>
                </div>
                {errors.location_text && <p className="text-red-500 text-sm mt-1">{errors.location_text.message}</p>}
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Search radius</label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {RADIUS_OPTIONS.map((r) => (
                    <button
                      key={r.value}
                      type="button"
                      onClick={() => setValue("radius_meters", r.value)}
                      className={`py-2 px-3 rounded-lg border text-sm font-medium transition-all ${watch("radius_meters") === r.value ? "border-brand-600 bg-brand-50 text-brand-700" : "border-gray-200 hover:border-brand-300"}`}
                    >
                      {r.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button type="button" onClick={() => setStep(1)} className="btn-secondary">Back</button>
                <button type="button" onClick={() => setStep(3)} className="btn-primary">
                  Next <ArrowRight size={16} />
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Business assumptions */}
          {step === 3 && (
            <div className="card">
              <h2 className="text-xl font-bold text-gray-900 mb-2">Business assumptions</h2>
              <p className="text-gray-500 text-sm mb-6">Skip anything you don't know — we'll use benchmarks.</p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Total investment budget (₹)</label>
                  <input
                    type="number"
                    {...register("total_investment", { valueAsNumber: true })}
                    placeholder="e.g. 1800000"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Max monthly rent (₹)</label>
                  <input
                    type="number"
                    {...register("monthly_rent_limit", { valueAsNumber: true })}
                    placeholder="e.g. 80000"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Average order value (₹)</label>
                  <input
                    type="number"
                    {...register("average_order_value", { valueAsNumber: true })}
                    placeholder="e.g. 350"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Target customer</label>
                  <input
                    {...register("target_customer")}
                    placeholder="e.g. young professionals"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                </div>
              </div>

              <div className="mt-4 flex items-center gap-2">
                <input type="checkbox" id="parking" {...register("parking_required")} className="rounded" />
                <label htmlFor="parking" className="text-sm text-gray-700">Parking required</label>
              </div>

              <div className="flex gap-3 mt-6">
                <button type="button" onClick={() => setStep(2)} className="btn-secondary">Back</button>
                <button type="submit" disabled={loading} className="btn-primary">
                  {loading ? <Loader2 size={16} className="animate-spin" /> : <><Zap size={16} /> Start Analysis</>}
                </button>
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}

function Zap(props: any) {
  const { Zap: Z } = require("lucide-react");
  return <Z {...props} />;
}
