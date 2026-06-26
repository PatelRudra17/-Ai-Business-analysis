import Link from "next/link";

export const metadata = { title: "Terms of Service" };

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="border-b border-gray-100 bg-white">
        <div className="max-w-3xl mx-auto px-4 h-16 flex items-center">
          <Link href="/" className="text-xl font-bold text-brand-700">BLIP</Link>
        </div>
      </nav>
      <div className="max-w-3xl mx-auto px-4 py-12 prose prose-gray">
        <h1>Terms of Service</h1>
        <p><strong>Effective date:</strong> 1 July 2026</p>
        <h2>1. Service Description</h2>
        <p>BLIP provides data-backed location intelligence reports for entrepreneurs and business owners. Reports are decision-support tools based on available data and user assumptions.</p>
        <h2>2. Disclaimer</h2>
        <p><strong>This platform provides data-backed estimates, comparisons, and recommendations based on available data and user-provided assumptions. It does not guarantee revenue, demand, regulatory approval, financing, property suitability, or business success. Users must independently verify legal, financial, property, and local-market conditions before investing.</strong></p>
        <h2>3. Payments & Refunds</h2>
        <p>Reports are charged on a per-analysis basis. Once a report is generated and unlocked, refunds are not available. If a report fails to generate due to a platform error, a full refund or re-analysis will be provided.</p>
        <h2>4. Data Accuracy</h2>
        <p>Competitor and demand data is sourced from Google Places API and may not reflect every business in an area. Financial scenarios use benchmark assumptions. All estimates are clearly labelled.</p>
        <h2>5. Acceptable Use</h2>
        <p>You may not use the platform for resale, scraping, or automated bulk analysis without written permission.</p>
        <h2>6. Contact</h2>
        <p>For queries, contact legal@blip.in</p>
      </div>
    </div>
  );
}
