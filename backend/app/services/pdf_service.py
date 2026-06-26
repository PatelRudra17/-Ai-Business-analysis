"""PDF report generator — renders HTML to PDF using WeasyPrint (server-side)."""
from __future__ import annotations

import uuid
from datetime import datetime


def render_report_html(report_data: dict, analysis_id: str) -> str:
    """Render a self-contained HTML string for the report."""
    exec_sum = report_data.get("executive_summary", {})
    score = exec_sum.get("score", 0)
    risk = exec_sum.get("risk_score", 0)
    decision = exec_sum.get("decision", "").replace("_", " ").title()
    location = report_data.get("location", "")
    business_type = report_data.get("business_type", "").replace("_", " ").title()
    generated = datetime.now().strftime("%d %b %Y")

    competitors = report_data.get("competitors", [])[:10]
    comp_rows = "".join(
        f"<tr><td>{c.get('name','')}</td><td>{c.get('rating','—')}</td><td>{c.get('review_count','—')}</td><td>{round(c.get('distance_meters',0)/1000,1)} km</td></tr>"
        for c in competitors
    )

    gaps = report_data.get("gaps", [])
    gap_items = "".join(
        f"<li><strong>{g.get('gap_type','').replace('_',' ').title()}</strong> — Score: {g.get('opportunity_score',0):.0f}, Confidence: {g.get('confidence',0)*100:.0f}%<br><ul>{''.join(f'<li>{s}</li>' for s in g.get('supporting_signals',[]))}</ul></li>"
        for g in gaps
    )

    scenarios = report_data.get("financial_scenarios", [])
    fin_rows = "".join(
        f"<tr><td><strong>{s.get('scenario_type','').title()}</strong></td><td>₹{s.get('monthly_revenue',0):,.0f}</td><td>₹{s.get('monthly_costs',0):,.0f}</td><td>₹{s.get('monthly_profit',0):,.0f}</td><td>{s.get('break_even_months',0):.1f} months</td></tr>"
        for s in scenarios
    )

    limitations = report_data.get("limitations", [])
    lim_items = "".join(f"<li>{l}</li>" for l in limitations)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>BLIP Report — {business_type} — {location}</title>
<style>
  body {{ font-family: Arial, sans-serif; font-size: 12px; color: #1a1a2e; margin: 0; padding: 40px; }}
  h1 {{ font-size: 22px; color: #4f46e5; }} h2 {{ font-size: 16px; color: #312e81; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px; }}
  .score-row {{ display: flex; gap: 40px; margin: 20px 0; }}
  .score-box {{ border: 2px solid #4f46e5; border-radius: 8px; padding: 16px 24px; text-align: center; }}
  .score-value {{ font-size: 40px; font-weight: bold; color: #4f46e5; }}
  .risk-value {{ font-size: 40px; font-weight: bold; color: #dc2626; }}
  table {{ width: 100%; border-collapse: collapse; margin: 12px 0; }}
  th {{ background: #f3f4f6; text-align: left; padding: 8px; }} td {{ padding: 8px; border-bottom: 1px solid #f3f4f6; }}
  .decision {{ font-size: 18px; font-weight: bold; color: #059669; margin: 12px 0; }}
  .disclaimer {{ background: #fef9c3; border: 1px solid #fde68a; border-radius: 6px; padding: 12px; font-size: 10px; margin-top: 30px; }}
  .footer {{ color: #9ca3af; font-size: 10px; margin-top: 20px; border-top: 1px solid #e5e7eb; padding-top: 8px; }}
</style>
</head>
<body>
<h1>Business Location Intelligence Report</h1>
<p><strong>Business:</strong> {business_type} &nbsp;|&nbsp; <strong>Location:</strong> {location} &nbsp;|&nbsp; <strong>Generated:</strong> {generated}</p>

<h2>Executive Decision</h2>
<p class="decision">{decision}</p>
<div class="score-row">
  <div class="score-box"><div class="score-value">{score:.0f}</div><div>Opportunity Score</div></div>
  <div class="score-box"><div class="risk-value">{risk:.0f}</div><div>Risk Score</div></div>
</div>
<p>{exec_sum.get('decision_summary','')}</p>

<h2>Competitor Landscape</h2>
<p><strong>{len(competitors)} competitors</strong> identified within the search area.</p>
<table><thead><tr><th>Name</th><th>Rating</th><th>Reviews</th><th>Distance</th></tr></thead>
<tbody>{comp_rows}</tbody></table>

<h2>Market Gaps Identified</h2>
<ul>{gap_items}</ul>

<h2>Financial Scenarios</h2>
<table><thead><tr><th>Scenario</th><th>Monthly Revenue</th><th>Monthly Costs</th><th>Monthly Profit</th><th>Break-Even</th></tr></thead>
<tbody>{fin_rows}</tbody></table>

<h2>Limitations & Assumptions</h2>
<ul>{lim_items}</ul>

<div class="disclaimer">
  <strong>Important:</strong> This report is a decision-support tool based on available data, user-provided assumptions, and calculated estimates.
  It does not guarantee revenue, demand, regulatory approval, financing, property suitability, or business success.
  Users should independently verify legal, financial, property, and local-market conditions before investing.
</div>
<div class="footer">Analysis ID: {analysis_id} &nbsp;|&nbsp; Powered by BLIP — Business Location Intelligence Platform</div>
</body>
</html>"""


async def generate_pdf(report_data: dict, analysis_id: str) -> bytes:
    """Generate PDF bytes from report data. Falls back to HTML bytes if WeasyPrint unavailable."""
    html = render_report_html(report_data, str(analysis_id))
    try:
        from weasyprint import HTML
        return HTML(string=html).write_pdf()
    except ImportError:
        # WeasyPrint not installed — return HTML as bytes (install weasyprint for real PDFs)
        return html.encode("utf-8")
