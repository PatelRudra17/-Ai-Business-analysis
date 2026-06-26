"""Gap Finder — deterministic logic + AI explanation."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GapInput:
    business_type: str
    business_subtype: str | None
    competitor_count: int
    competitor_subtypes: list[str]
    competitor_avg_rating: float
    weak_themes: list[str]          # from review analysis
    price_level_distribution: dict  # {1: count, 2: count, ...}
    signals: dict                   # {"college": 3, "office": 5, ...}
    target_customer: str | None
    has_late_night_competitors: bool = False
    has_ladies_only: bool = False
    has_premium_option: bool = False
    has_budget_option: bool = False


@dataclass
class GapResult:
    gap_type: str
    opportunity_score: float
    confidence: float
    supporting_signals: list[str]
    limitations: list[str]
    ai_prompt_context: str = ""  # passed to AI for explanation


GAP_RULES: dict[str, list[dict]] = {
    "gym": [
        {
            "id": "ladies_only_gym",
            "label": "Ladies-Only Fitness Studio",
            "condition": lambda i: not i.has_ladies_only and (i.signals.get("residential_society", 0) > 2),
            "base_score": 72,
            "signals": lambda i: [
                f"{i.signals.get('residential_society', 0)} residential societies nearby",
                "No ladies-only gym identified in the area",
                f"{'Privacy complaints in reviews' if 'overcrowding' in i.weak_themes else 'Potential demand from residential population'}",
            ],
            "limitations": ["Ladies-only segment size requires local survey validation"],
        },
        {
            "id": "budget_gym",
            "label": "Budget / No-Frills Gym",
            "condition": lambda i: i.has_premium_option and not i.has_budget_option,
            "base_score": 68,
            "signals": lambda i: [
                "Existing gyms skew premium in the area",
                "No budget-friendly option identified",
                f"{i.signals.get('college', 0) + i.signals.get('office', 0)} colleges/offices nearby",
            ],
            "limitations": ["Budget segment profitability depends on membership volume"],
        },
        {
            "id": "24hr_gym",
            "label": "24-Hour / Late-Night Gym",
            "condition": lambda i: not i.has_late_night_competitors and i.signals.get("office", 0) > 3,
            "base_score": 65,
            "signals": lambda i: [
                f"{i.signals.get('office', 0)} offices within the area",
                "No late-night gym identified",
                "Working-professional demand typically extends past 9 PM",
            ],
            "limitations": ["Late-night operations increase staffing and security costs"],
        },
    ],
    "cafe": [
        {
            "id": "late_night_work_cafe",
            "label": "Late-Night Work-Friendly Café",
            "condition": lambda i: not i.has_late_night_competitors and (
                i.signals.get("college", 0) + i.signals.get("office", 0) > 3
            ),
            "base_score": 79,
            "signals": lambda i: [
                f"{i.signals.get('college', 0)} colleges and {i.signals.get('office', 0)} offices nearby",
                "No cafés with confirmed late-night operations identified",
                f"{'Seating and waiting complaints in existing reviews' if 'seating' in i.weak_themes or 'waiting_time' in i.weak_themes else 'Strong young professional base'}",
            ],
            "limitations": [
                "Late-night footfall requires on-ground validation",
                "Review analysis is based on available samples",
            ],
        },
        {
            "id": "premium_cafe",
            "label": "Premium Specialty Coffee Experience",
            "condition": lambda i: not i.has_premium_option and i.signals.get("office", 0) > 2,
            "base_score": 71,
            "signals": lambda i: [
                f"No premium café identified at price level 3-4",
                f"{i.signals.get('office', 0)} offices indicate working-professional traffic",
                f"{'Taste and ambience complaints suggest quality gap' if 'taste' in i.weak_themes else 'Premium coffee market growing in Ahmedabad'}",
            ],
            "limitations": ["Premium positioning requires differentiated product and trained staff"],
        },
        {
            "id": "delivery_first_cafe",
            "label": "Delivery-First Café (Cloud Kitchen Model)",
            "condition": lambda i: i.competitor_count > 6 and i.signals.get("coworking_space", 0) > 0,
            "base_score": 62,
            "signals": lambda i: [
                f"High dine-in competition ({i.competitor_count} competitors) makes delivery model more viable",
                "Coworking spaces nearby indicate work-from-home demand",
                "Lower rent requirement vs dine-in",
            ],
            "limitations": ["Delivery model depends on Swiggy/Zomato commission economics", "Brand-building slower without physical presence"],
        },
    ],
    "salon": [
        {
            "id": "premium_appointment_salon",
            "label": "Premium Appointment-Only Salon",
            "condition": lambda i: not i.has_premium_option and (
                "hygiene" in i.weak_themes or "appointment_management" in i.weak_themes
            ),
            "base_score": 76,
            "signals": lambda i: [
                f"{'Hygiene complaints in competitor reviews' if 'hygiene' in i.weak_themes else 'Quality gap identified'}",
                f"{'Appointment management issues at existing salons' if 'appointment_management' in i.weak_themes else ''}",
                f"{i.signals.get('apartment_complex', 0)} apartment complexes indicate residential demand",
            ],
            "limitations": ["Premium positioning requires strong stylist team from day 1"],
        },
        {
            "id": "gents_grooming",
            "label": "Premium Men's Grooming Studio",
            "condition": lambda i: i.business_subtype not in ("gents_salon",) and i.signals.get("office", 0) > 2,
            "base_score": 65,
            "signals": lambda i: [
                f"{i.signals.get('office', 0)} offices indicate male working-professional base",
                "Men's grooming segment growing at 18% annually in urban India",
                "Few dedicated men's grooming studios visible in area",
            ],
            "limitations": ["Men's grooming segment still developing in Ahmedabad vs Mumbai/Delhi"],
        },
    ],
}


def find_gaps(inp: GapInput) -> list[GapResult]:
    rules = GAP_RULES.get(inp.business_type, [])
    results = []
    for rule in rules:
        try:
            if rule["condition"](inp):
                score = float(rule["base_score"])
                conf = _calculate_confidence(inp, score)
                results.append(GapResult(
                    gap_type=rule["id"],
                    opportunity_score=score,
                    confidence=conf,
                    supporting_signals=[s for s in rule["signals"](inp) if s],
                    limitations=rule["limitations"],
                    ai_prompt_context=f"Gap: {rule['label']}. Business: {inp.business_type} in Ahmedabad. Competitors: {inp.competitor_count}.",
                ))
        except Exception:
            continue
    results.sort(key=lambda r: r.opportunity_score, reverse=True)
    return results[:3]  # top 3 gaps


def _calculate_confidence(inp: GapInput, base_score: float) -> float:
    conf = 0.70
    if inp.competitor_count < 3:
        conf -= 0.10  # fewer competitors = less review data
    if len(inp.weak_themes) > 2:
        conf += 0.10
    total_signals = sum(inp.signals.values())
    if total_signals > 10:
        conf += 0.05
    return round(min(0.95, max(0.40, conf)), 2)
