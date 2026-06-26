"""Location scoring engine — deterministic, formula-based. No AI involved."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScoringInput:
    # Competitor data
    competitor_count: int = 0
    avg_competitor_rating: float = 0.0
    avg_competitor_reviews: float = 0.0
    weak_review_themes: list[str] = field(default_factory=list)
    price_gap_exists: bool = False

    # Demand signals (counts by ring)
    signals_0_1km: int = 0
    signals_1_3km: int = 0
    signals_3_5km: int = 0

    # Accessibility
    has_parking: bool = False
    on_main_road: bool = False

    # Financial fit
    rent_to_revenue_ratio: float = 0.0
    break_even_months: float = 0.0
    gross_margin_pct: float = 0.0

    # Growth signals
    development_projects_nearby: int = 0

    # Data quality
    data_completeness: float = 0.8
    source_reliability: float = 0.9
    data_freshness: float = 1.0

    # Category weights override
    weights: dict = field(default_factory=dict)


@dataclass
class ScoreResult:
    raw_opportunity_score: float
    final_opportunity_score: float
    risk_score: float
    confidence_score: float
    penalties: float
    components: list[dict]
    decision: str
    formula_version: str = "opportunity-v1.0"


_DEFAULT_WEIGHTS = {
    "demand_potential":   0.25,
    "competition_gap":    0.20,
    "accessibility":      0.15,
    "financial_fit":      0.15,
    "growth_potential":   0.10,
    "unmet_need":         0.10,
    "data_confidence":    0.05,
}


def calculate_score(inp: ScoringInput) -> ScoreResult:
    weights = {**_DEFAULT_WEIGHTS, **inp.weights}
    components = []

    # 1. Demand Potential (0-100)
    demand = _demand_score(inp)
    components.append(_comp("demand_potential", demand, weights["demand_potential"]))

    # 2. Competition Gap (0-100)
    gap = _competition_gap_score(inp)
    components.append(_comp("competition_gap", gap, weights["competition_gap"]))

    # 3. Accessibility (0-100)
    access = _accessibility_score(inp)
    components.append(_comp("accessibility", access, weights["accessibility"]))

    # 4. Financial Fit (0-100)
    fin = _financial_fit_score(inp)
    components.append(_comp("financial_fit", fin, weights["financial_fit"]))

    # 5. Growth Potential (0-100)
    growth = min(100, 40 + inp.development_projects_nearby * 15)
    components.append(_comp("growth_potential", growth, weights["growth_potential"]))

    # 6. Unmet Need (0-100)
    unmet = _unmet_need_score(inp)
    components.append(_comp("unmet_need", unmet, weights["unmet_need"]))

    # 7. Data Confidence (0-100)
    conf = _data_confidence(inp) * 100
    components.append(_comp("data_confidence", conf, weights["data_confidence"]))

    raw = sum(c["weighted_value"] for c in components)

    # Risk penalties
    penalties = 0.0
    if inp.competitor_count > 10:
        penalties += min(15, (inp.competitor_count - 10) * 1.5)
    if inp.rent_to_revenue_ratio > 0.35:
        penalties += min(10, (inp.rent_to_revenue_ratio - 0.35) * 50)
    if inp.data_completeness < 0.5:
        penalties += 5

    final = max(0.0, round(raw - penalties, 1))
    risk = _risk_score(inp)
    confidence = round(_data_confidence(inp) * 100, 1)
    decision = _decision_label(final, risk, confidence)

    return ScoreResult(
        raw_opportunity_score=round(raw, 1),
        final_opportunity_score=final,
        risk_score=round(risk, 1),
        confidence_score=confidence,
        penalties=round(penalties, 1),
        components=components,
        decision=decision,
    )


def _demand_score(inp: ScoringInput) -> float:
    total_signals = inp.signals_0_1km * 3 + inp.signals_1_3km * 2 + inp.signals_3_5km
    return min(100, total_signals * 4)


def _competition_gap_score(inp: ScoringInput) -> float:
    if inp.competitor_count == 0:
        return 70  # no competitors = opportunity but also unproven market
    density_penalty = min(60, inp.competitor_count * 6)
    quality_bonus = 0
    if inp.avg_competitor_rating < 3.8:
        quality_bonus += 20
    if inp.avg_competitor_reviews < 50:
        quality_bonus += 10
    if inp.price_gap_exists:
        quality_bonus += 15
    return max(0, min(100, 100 - density_penalty + quality_bonus))


def _accessibility_score(inp: ScoringInput) -> float:
    score = 50.0
    if inp.has_parking:
        score += 25
    if inp.on_main_road:
        score += 25
    return min(100, score)


def _financial_fit_score(inp: ScoringInput) -> float:
    if inp.rent_to_revenue_ratio == 0:
        return 60  # unknown — neutral
    score = 100 - (inp.rent_to_revenue_ratio * 200)  # 0.3 ratio = 40 points
    score -= max(0, (inp.break_even_months - 18) * 2)
    score += max(0, (inp.gross_margin_pct - 0.5) * 50)
    return max(0, min(100, score))


def _unmet_need_score(inp: ScoringInput) -> float:
    score = 30.0
    score += len(inp.weak_review_themes) * 10
    if inp.price_gap_exists:
        score += 20
    return min(100, score)


def _risk_score(inp: ScoringInput) -> float:
    risk = 20.0
    if inp.competitor_count > 8:
        risk += 20
    if inp.rent_to_revenue_ratio > 0.35:
        risk += 25
    if inp.break_even_months > 24:
        risk += 15
    if inp.data_completeness < 0.6:
        risk += 10
    return min(100, round(risk, 1))


def _data_confidence(inp: ScoringInput) -> float:
    return round(
        0.30 * inp.data_completeness
        + 0.25 * inp.source_reliability
        + 0.20 * inp.data_freshness
        + 0.15 * 0.9  # geographic precision assumed high
        + 0.10 * min(1.0, inp.competitor_count / 5),
        3,
    )


def _decision_label(score: float, risk: float, confidence: float) -> str:
    if confidence < 40:
        return "INSUFFICIENT_DATA"
    if score >= 70 and risk <= 40:
        return "STRONG_OPPORTUNITY"
    if score >= 55 and risk <= 60:
        return "PROMISING_WITH_CONDITIONS"
    if score >= 40:
        return "NEEDS_LOCAL_VALIDATION"
    return "HIGH_RISK_OPPORTUNITY"


def _comp(name: str, raw: float, weight: float) -> dict:
    return {
        "component_name": name,
        "weight": weight,
        "raw_value": round(raw, 2),
        "weighted_value": round(raw * weight, 2),
        "source": "scoring-engine-v1",
    }
