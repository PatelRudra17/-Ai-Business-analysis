"""AI service — Groq integration (free tier) for review analysis, gap explanation, and report writing.

Get your FREE Groq API key at: https://console.groq.com
Sign up with Google or GitHub — no credit card required.
Free tier: 14,400 requests/day with Llama 3.1 models.
"""
import json
from typing import Any

import httpx

from app.config import settings

_GROQ_BASE = "https://api.groq.com/openai/v1"
_MODEL = "llama-3.1-8b-instant"           # fast, free — for classification tasks
_REPORT_MODEL = "llama-3.3-70b-versatile"  # stronger — for report writing


async def _call_groq(
    messages: list[dict],
    model: str = _MODEL,
    max_tokens: int = 1024,
    system: str = "",
) -> str:
    if not settings.AI_API_KEY or settings.AI_API_KEY in ("", "your-groq-api-key-here"):
        raise ValueError("AI_API_KEY not set. Get a free key at https://console.groq.com")

    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)

    headers = {
        "Authorization": f"Bearer {settings.AI_API_KEY}",
        "Content-Type": "application/json",
    }
    body: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": full_messages,
        "temperature": 0.3,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(f"{_GROQ_BASE}/chat/completions", headers=headers, json=body)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


# ---------- Review Classification ----------

REVIEW_SYSTEM = """You are a business review classifier. Extract themes from a customer review.
Return ONLY valid JSON matching this schema:
{"themes": [{"category": string, "sentiment": "positive"|"negative"|"neutral", "severity": 1-5, "evidence": string}]}
Do not invent themes not present in the review. Return empty themes array if no themes found."""


async def classify_review(text: str, taxonomy: list[str]) -> list[dict]:
    prompt = f"Review: {text}\n\nValid categories: {', '.join(taxonomy)}\n\nExtract themes."
    try:
        raw = await _call_groq([{"role": "user", "content": prompt}], system=REVIEW_SYSTEM, max_tokens=512)
        data = json.loads(raw)
        return data.get("themes", [])
    except Exception:
        return []


# ---------- Gap Explanation ----------

async def explain_gap(gap_type: str, supporting_signals: list[str], business_type: str, location: str) -> str:
    prompt = f"""Write a 2-3 sentence explanation of this market gap opportunity for a business report.

Gap identified: {gap_type.replace('_', ' ').title()}
Business type: {business_type}
Location: {location}
Supporting signals: {chr(10).join(f'- {s}' for s in supporting_signals)}

Be specific, practical, and honest. Mention what data supports this gap. Do not guarantee success."""
    try:
        return await _call_groq([{"role": "user", "content": prompt}], max_tokens=256)
    except Exception:
        return f"A potential {gap_type.replace('_', ' ')} opportunity was identified based on area data."


# ---------- Score Explanation ----------

async def explain_score(score: float, risk: float, decision: str, components: list[dict], business_type: str) -> str:
    comp_summary = "\n".join(
        f"- {c['component_name']}: {c['raw_value']:.0f}/100 (weight {c['weight']*100:.0f}%)"
        for c in components
    )
    prompt = f"""Write a 3-4 sentence explanation of this location's Opportunity Score for a business report.

Business type: {business_type}
Opportunity Score: {score}/100
Risk Score: {risk}/100
Decision: {decision.replace('_', ' ').title()}

Score components:
{comp_summary}

Be clear about what's driving the score. Be honest about limitations. Avoid guaranteeing success."""
    try:
        return await _call_groq([{"role": "user", "content": prompt}], max_tokens=300)
    except Exception:
        return f"The location scored {score}/100 on the opportunity scale with a risk score of {risk}/100."


# ---------- Marketing Strategy ----------

async def generate_marketing_strategy(
    business_type: str, subtype: str | None, gaps: list[dict], target_customer: str | None
) -> dict:
    prompt = f"""Generate a practical marketing strategy for a new {business_type} business in Ahmedabad.

Business subtype: {subtype or 'general'}
Target customer: {target_customer or 'general public'}
Key gaps/opportunities identified: {', '.join(g.get('gap_type', '') for g in gaps[:2])}

Return JSON with keys:
- positioning: one sentence positioning statement
- channels: list of 4-5 marketing channels with brief notes
- launch_offers: list of 2-3 specific launch offers
- retention_tactics: list of 3 retention strategies

Return ONLY valid JSON."""
    try:
        raw = await _call_groq([{"role": "user", "content": prompt}], max_tokens=600)
        # Strip markdown code fences if present
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception:
        return {
            "positioning": f"Quality {business_type} serving {target_customer or 'local customers'} in Ahmedabad.",
            "channels": ["Google My Business", "Instagram", "Local WhatsApp groups", "Referral programme"],
            "launch_offers": ["20% off for first 50 customers", "Refer a friend — both get 10% off"],
            "retention_tactics": ["Loyalty card", "Monthly newsletter", "Birthday offers"],
        }


# ---------- 30-Day Launch Plan ----------

async def generate_launch_plan(business_type: str, decision: str, main_risk: str | None) -> list[dict]:
    prompt = f"""Generate a realistic 30-day launch plan for a new {business_type} in Ahmedabad.
Main risk to address: {main_risk or 'competition'}
Decision context: {decision.replace('_', ' ')}

Return JSON array of weekly tasks (4 weeks), each with:
{{"week": 1, "theme": string, "tasks": [list of 4-5 specific tasks]}}

Return ONLY valid JSON array."""
    try:
        raw = await _call_groq([{"role": "user", "content": prompt}], max_tokens=800)
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception:
        return [
            {"week": 1, "theme": "Pre-launch setup", "tasks": ["Finalise property agreement", "Order equipment", "Recruit staff", "Register on Google My Business"]},
            {"week": 2, "theme": "Soft launch", "tasks": ["Invite 20 friends/family for free trial", "Set up Instagram page", "Collect first reviews", "Test operations"]},
            {"week": 3, "theme": "Paid launch", "tasks": ["Run WhatsApp campaign in nearby societies", "Instagram ads targeting local audience", "Launch opening offer", "Follow up with soft-launch visitors"]},
            {"week": 4, "theme": "Stabilise", "tasks": ["Review feedback", "Adjust pricing if needed", "Start referral programme", "Identify repeat customers", "Plan month 2 targets"]},
        ]


# ---------- Full Report Narrative ----------

REPORT_SYSTEM = """You are a business location analyst writing a professional market report for an entrepreneur.

Rules:
1. Separate OBSERVED facts (from data), OFFICIAL data, CALCULATIONS, and ESTIMATES.
2. Never guarantee revenue, demand, or success.
3. Label estimates clearly as estimates.
4. Be specific and actionable.
5. Write in plain English suitable for an Indian entrepreneur.
6. Always include the disclaimer: "This is a data-backed estimate. Verify locally before investing."
7. Return structured JSON only."""


async def write_report_narrative(report_data: dict) -> dict:
    prompt = f"""Write a complete business location report narrative for:

Business: {report_data.get('business_type')} ({report_data.get('business_subtype', '')})
Location: {report_data.get('location')}
Opportunity Score: {report_data.get('opportunity_score')}
Risk Score: {report_data.get('risk_score')}
Decision: {report_data.get('decision')}
Competitors found: {report_data.get('competitor_count')}
Key gaps: {report_data.get('gaps', [])}
Financial summary: {report_data.get('financial_summary', {})}

Return JSON with keys: executive_summary, competitor_analysis_text, demand_analysis_text, risk_analysis_text, recommendations.
Each value should be 2-4 sentences. Return ONLY valid JSON."""
    try:
        raw = await _call_groq(
            [{"role": "user", "content": prompt}],
            model=_REPORT_MODEL,
            system=REPORT_SYSTEM,
            max_tokens=1500,
        )
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception:
        return {
            "executive_summary": f"This analysis covers the {report_data.get('business_type', 'business')} opportunity at {report_data.get('location', 'the selected location')}.",
            "competitor_analysis_text": "Competitor data has been collected and analysed.",
            "demand_analysis_text": "Demand signals have been assessed based on nearby landmarks and activity.",
            "risk_analysis_text": "Key risks have been identified and should be validated on the ground.",
            "recommendations": "Review all three financial scenarios before committing to a lease.",
        }


# ---------- Claim Checker ----------

async def check_claims(narrative: str, verified_data: dict) -> list[dict]:
    prompt = f"""Review this business report narrative for unsupported claims.

Narrative: {narrative[:2000]}

Verified data available:
- Competitor count: {verified_data.get('competitor_count')}
- Opportunity score: {verified_data.get('opportunity_score')}
- Risk score: {verified_data.get('risk_score')}

Flag any claim that:
1. Guarantees revenue or success
2. States exact demographics not in the data
3. Makes predictions presented as facts

Return JSON array: [{{"claim": string, "is_supported": bool, "action": "kept"|"remove"|"qualify"}}]
Return empty array if no issues found. Return ONLY valid JSON."""
    try:
        raw = await _call_groq([{"role": "user", "content": prompt}], max_tokens=600)
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw) if raw.strip().startswith("[") else []
    except Exception:
        return []
