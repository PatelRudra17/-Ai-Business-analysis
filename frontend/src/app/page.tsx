import Link from "next/link";
import { ArrowRight, BarChart3, MapPin, ShieldCheck, Zap } from "lucide-react";

const FEATURES = [
  {
    icon: MapPin,
    title: "Competitor Intelligence",
    description: "See every competitor on a map with ratings, review trends, and pricing gaps.",
  },
  {
    icon: BarChart3,
    title: "Opportunity & Risk Scores",
    description: "Transparent, formula-based scores with confidence levels — no black boxes.",
  },
  {
    icon: Zap,
    title: "Gap Finder",
    description: "Discover underserved customer segments that competitors are missing.",
  },
  {
    icon: ShieldCheck,
    title: "Financial Scenarios",
    description: "Conservative, expected, and optimistic revenue and break-even estimates.",
  },
];

const CATEGORIES = [
  { slug: "gym", name: "Gym & Fitness Studio", icon: "🏋️" },
  { slug: "cafe", name: "Café & Restaurant",   icon: "☕" },
  { slug: "salon", name: "Salon & Beauty",     icon: "✂️" },
];

export default function HomePage() {
  return (
    <main className="min-h-screen">
      {/* Nav */}
      <nav className="border-b border-gray-100 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <span className="text-xl font-bold text-brand-700">BLIP</span>
          <div className="flex items-center gap-4">
            <Link href="/login" className="text-gray-600 hover:text-gray-900 text-sm font-medium">Log in</Link>
            <Link href="/register" className="btn-primary text-sm py-2 px-4">Get Started</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="bg-gradient-to-br from-brand-50 via-white to-indigo-50 pt-24 pb-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-brand-100 text-brand-700 text-sm font-semibold px-4 py-1.5 rounded-full mb-6">
            <span>🚀</span> Launching in Ahmedabad
          </div>
          <h1 className="text-5xl font-bold text-gray-900 leading-tight mb-6">
            Tell us your business idea and location.<br />
            <span className="text-brand-600">We'll tell you if it'll work.</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-10">
            Data-backed competitor analysis, demand signals, gap detection, and financial scenarios — before you sign a lease.
          </p>
          <Link href="/analyze" className="btn-primary text-base px-8 py-4">
            Analyse My Location <ArrowRight size={20} />
          </Link>
          <p className="mt-4 text-sm text-gray-500">Free preview · No credit card required</p>
        </div>
      </section>

      {/* Categories */}
      <section className="py-16 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl font-bold text-center text-gray-900 mb-10">Supported Business Categories</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {CATEGORIES.map((cat) => (
              <Link
                key={cat.slug}
                href={`/analyze?category=${cat.slug}`}
                className="card hover:border-brand-300 hover:shadow-md transition-all group"
              >
                <div className="text-4xl mb-3">{cat.icon}</div>
                <h3 className="text-lg font-semibold text-gray-900 group-hover:text-brand-700">{cat.name}</h3>
                <p className="text-sm text-gray-500 mt-1">Analyse any location in Ahmedabad</p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl font-bold text-center text-gray-900 mb-10">What You Get in Every Report</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {FEATURES.map((f) => (
              <div key={f.title} className="card">
                <f.icon className="text-brand-600 mb-3" size={28} />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{f.title}</h3>
                <p className="text-gray-600">{f.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Disclaimer */}
      <section className="py-10 px-4 bg-white border-t border-gray-100">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-xs text-gray-400 leading-relaxed">
            This platform provides data-backed estimates, comparisons, and recommendations based on available data and user assumptions. It does not guarantee revenue, demand, regulatory approval, or business success. Users should independently verify all conditions before investing.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-8 px-4">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <span className="text-white font-bold text-lg">BLIP</span>
          <p className="text-sm">© 2026 Business Location Intelligence Platform. All rights reserved.</p>
        </div>
      </footer>
    </main>
  );
}
