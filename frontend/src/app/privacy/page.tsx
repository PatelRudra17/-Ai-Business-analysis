import Link from "next/link";

export const metadata = { title: "Privacy Policy" };

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="border-b border-gray-100 bg-white">
        <div className="max-w-3xl mx-auto px-4 h-16 flex items-center">
          <Link href="/" className="text-xl font-bold text-brand-700">BLIP</Link>
        </div>
      </nav>
      <div className="max-w-3xl mx-auto px-4 py-12 prose prose-gray">
        <h1>Privacy Policy</h1>
        <p><strong>Effective date:</strong> 1 July 2026</p>
        <h2>1. Information We Collect</h2>
        <p>We collect your name, email address, phone number (optional), and the business and location data you enter during analysis. We do not sell your personal data.</p>
        <h2>2. How We Use Your Information</h2>
        <p>Your data is used to generate your location intelligence reports and to improve the platform. Location coordinates and business parameters are passed to Google Places API and our AI models for analysis.</p>
        <h2>3. Data Retention</h2>
        <p>Analysis data is retained for 2 years. You may request deletion of your account and data at any time by emailing us.</p>
        <h2>4. Third-Party Services</h2>
        <p>We use Google Places API (data collection), Razorpay (payments), and Anthropic Claude (AI analysis). Each operates under their own privacy policies.</p>
        <h2>5. Data Export & Deletion</h2>
        <p>You may request a copy of your data or request deletion by contacting support. Account deletion is processed within 30 days.</p>
        <h2>6. Contact</h2>
        <p>For privacy questions, contact us at privacy@blip.in</p>
      </div>
    </div>
  );
}
