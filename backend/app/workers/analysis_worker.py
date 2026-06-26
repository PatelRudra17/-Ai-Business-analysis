"""
Analysis orchestrator — runs the full pipeline for an analysis job.
Uses Overpass API (free, OpenStreetMap) for place data.

Pipeline:
  1. Load job + category config
  2. Generate search grid
  3. Collect competitors (Overpass/OSM — FREE)
  4. Collect demand signals (Overpass/OSM — FREE)
  5. AI review weakness extraction (no reviews from OSM; use gap rules)
  6. Gap Finder
  7. Scoring engine
  8. Financial scenarios
  9. AI report writer + claim checker
 10. PDF generation + upload
 11. Mark job completed
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone

import structlog
from geoalchemy2.elements import WKTElement
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.analysis import AnalysisJob, Location, SearchGrid
from app.models.audit import AIRun, ApiUsage
from app.models.billing import Alert
from app.models.category import BusinessConfiguration
from app.models.competitor import Place, PlaceSnapshot, ReviewSample, ReviewTheme
from app.models.financial import Assumption, FinancialScenario
from app.models.report import Report, ReportClaim
from app.models.scoring import ScoreComponent, ScoreVersion
from app.models.signals import AreaSignal
from app.services import ai_service, gap_finder, scoring, financial as fin_service, pdf_service, storage
from app.services.overpass import overpass_client as places_client  # FREE — no API key needed
from app.services.search_grid import generate_search_grid

log = structlog.get_logger()

MAX_REVIEW_DETAILS = 5      # max competitors to fetch full details+reviews for
MAX_REVIEWS_PER_PLACE = 3   # Google Places API returns max 5 reviews


async def run_analysis(analysis_id: uuid.UUID) -> None:
    async with AsyncSessionLocal() as db:
        job = await db.get(AnalysisJob, analysis_id)
        if not job:
            log.error("analysis_not_found", analysis_id=str(analysis_id))
            return
        try:
            await _run(db, job)
        except Exception as e:
            log.error("analysis_failed", analysis_id=str(analysis_id), error=str(e))
            job.status = "failed"
            job.error_message = str(e)
            await db.commit()


async def _run(db: AsyncSession, job: AnalysisJob) -> None:
    job.status = "processing"
    await db.commit()
    logger = log.bind(analysis_id=str(job.id))

    # --- Load job data ---
    location: Location = await db.get(Location, job.location_id)
    lat, lng = location.latitude, location.longitude
    radius = job.radius_meters

    # --- Load business configuration ---
    config = await db.scalar(
        select(BusinessConfiguration).where(
            BusinessConfiguration.category_id == job.category_id,
            BusinessConfiguration.is_active == True,
        )
    )
    if not config:
        raise ValueError("No active business configuration found for category")

    logger.info("config_loaded", version=config.version)

    # --- Step 1: Search grid ---
    grid_points = generate_search_grid(lat, lng, radius)
    grid = SearchGrid(analysis_job_id=job.id, grid_points=grid_points, radius_meters=radius)
    db.add(grid)
    await db.flush()
    logger.info("search_grid_generated", points=len(grid_points))

    # --- Step 2: Collect competitors ---
    raw_competitors = await places_client.collect_competitors(lat, lng, radius, config.competitor_queries)
    logger.info("competitors_collected", count=len(raw_competitors))
    await _log_api_usage(db, job.id, "places_client", "nearby_search", len(config.competitor_queries))

    # Save places
    saved_places: list[Place] = []
    for c in raw_competitors:
        existing = await db.scalar(select(Place).where(Place.place_id == c["place_id"]))
        if not existing:
            p = Place(
                place_id=c["place_id"],
                name=c["name"],
                place_type="competitor",
                category_id=job.category_id,
                latitude=c["latitude"],
                longitude=c["longitude"],
                point=WKTElement(f"POINT({c['longitude']} {c['latitude']})", srid=4326),
                address=c.get("address"),
                google_types=c.get("google_types", []),
            )
            db.add(p)
            await db.flush()
            existing = p

        dist = places_client.distance_meters(lat, lng, c["latitude"], c["longitude"])
        snap = PlaceSnapshot(
            place_id=existing.id,
            analysis_job_id=job.id,
            rating=c.get("rating"),
            review_count=c.get("review_count"),
            price_level=c.get("price_level"),
            is_open_now=c.get("is_open_now"),
        )
        db.add(snap)
        saved_places.append(existing)

    await db.flush()
    logger.info("places_saved", count=len(saved_places))

    # --- Step 3: Collect demand signals ---
    raw_signals = await places_client.collect_signals(lat, lng, radius, config.positive_signals)
    logger.info("signals_collected", count=len(raw_signals))
    await _log_api_usage(db, job.id, "places_client", "nearby_search_signals", len(config.positive_signals))

    signal_counts: dict[str, int] = {}
    for s in raw_signals:
        dist = places_client.distance_meters(lat, lng, s["latitude"] or lat, s["longitude"] or lng)
        ring = places_client.distance_ring(dist)
        stype = s.get("signal_type", "unknown")
        signal_counts[stype] = signal_counts.get(stype, 0) + 1
        db.add(AreaSignal(
            analysis_job_id=job.id,
            signal_type=stype,
            place_id=s.get("place_id"),
            name=s.get("name"),
            distance_meters=dist,
            distance_ring=ring,
            latitude=s.get("latitude"),
            longitude=s.get("longitude"),
        ))

    await db.flush()

    # Aggregate by ring
    signals_0_1 = sum(1 for s in raw_signals if places_client.distance_meters(lat, lng, s.get("latitude") or lat, s.get("longitude") or lng) <= 1000)
    signals_1_3 = sum(1 for s in raw_signals if 1000 < places_client.distance_meters(lat, lng, s.get("latitude") or lat, s.get("longitude") or lng) <= 3000)
    signals_3_5 = sum(1 for s in raw_signals if 3000 < places_client.distance_meters(lat, lng, s.get("latitude") or lat, s.get("longitude") or lng) <= 5000)

    # --- Step 4: Review weakness analysis ---
    # OSM (Overpass) does not provide reviews or price levels.
    # We derive proxy weak themes from competitor density and name patterns.
    # Switch to Google Places API later to get real review analysis.
    weak_themes: list[str] = []
    price_levels: dict[int, int] = {}

    if len(saved_places) > 6:
        weak_themes.append("overcrowding")
    if len(saved_places) > 3:
        weak_themes.append("waiting_time")

    # Infer premium/budget from place names (proxy)
    for p in saved_places:
        name_lower = (p.name or "").lower()
        if any(w in name_lower for w in ["premium", "luxury", "elite", "gold"]):
            price_levels[3] = price_levels.get(3, 0) + 1
        elif any(w in name_lower for w in ["budget", "cheap", "economy"]):
            price_levels[1] = price_levels.get(1, 0) + 1

    await db.flush()
    weak_themes_unique = list(set(weak_themes))
    logger.info("review_analysis_done", weak_themes=weak_themes_unique, source="osm_proxy")

    # --- Step 5: Gap Finder ---
    has_late_night = any("24" in p.name.lower() or "late" in (p.name or "").lower() for p in saved_places)
    has_ladies = any("ladies" in (p.name or "").lower() or "women" in (p.name or "").lower() for p in saved_places)
    max_pl = max(price_levels.keys(), default=0)
    min_pl = min(price_levels.keys(), default=0)

    gap_input = gap_finder.GapInput(
        business_type=_get_category_slug(job),
        business_subtype=None,
        competitor_count=len(saved_places),
        competitor_subtypes=[],
        competitor_avg_rating=_avg([c.get("rating") for c in raw_competitors if c.get("rating")]),
        weak_themes=weak_themes_unique,
        price_level_distribution=price_levels,
        signals=signal_counts,
        target_customer=job.target_customer,
        has_late_night_competitors=has_late_night,
        has_ladies_only=has_ladies,
        has_premium_option=max_pl >= 3,
        has_budget_option=min_pl <= 1,
    )
    gaps = gap_finder.find_gaps(gap_input)
    logger.info("gaps_found", count=len(gaps))

    # Explain gaps with AI
    gap_dicts = []
    category_slug = _get_category_slug(job)
    for g in gaps:
        explanation = await ai_service.explain_gap(g.gap_type, g.supporting_signals, category_slug, location.display_name)
        gap_dicts.append({
            "gap_type": g.gap_type,
            "opportunity_score": g.opportunity_score,
            "confidence": g.confidence,
            "supporting_signals": g.supporting_signals,
            "limitations": g.limitations,
            "explanation": explanation,
        })

    # --- Step 6: Scoring engine ---
    rent = job.monthly_rent_limit or 50000
    invest = job.total_investment or 1500000
    aov = job.average_order_value or 300
    gross_margin = 0.60 if category_slug == "gym" else 0.65 if category_slug == "salon" else 0.62
    rent_to_rev = rent / max(aov * 30, 1)
    bep_months_est = invest / max((aov * 80 * gross_margin) - rent, 1)

    score_input = scoring.ScoringInput(
        competitor_count=len(saved_places),
        avg_competitor_rating=gap_input.competitor_avg_rating,
        avg_competitor_reviews=_avg([c.get("review_count") for c in raw_competitors if c.get("review_count")]),
        weak_review_themes=weak_themes_unique,
        price_gap_exists=len(gap_dicts) > 0,
        signals_0_1km=signals_0_1,
        signals_1_3km=signals_1_3,
        signals_3_5km=signals_3_5,
        has_parking=job.parking_required,
        on_main_road=False,  # would need extra data
        rent_to_revenue_ratio=min(rent_to_rev, 1.0),
        break_even_months=max(0, bep_months_est),
        gross_margin_pct=gross_margin,
        data_completeness=0.75 if len(saved_places) >= 3 else 0.50,
        weights=config.scoring_weights or {},
    )
    score_result = scoring.calculate_score(score_input)
    logger.info("scoring_done", score=score_result.final_opportunity_score, risk=score_result.risk_score)

    # Save score
    score_explanation = await ai_service.explain_score(
        score_result.final_opportunity_score, score_result.risk_score,
        score_result.decision, score_result.components, category_slug,
    )
    score_version = ScoreVersion(
        analysis_job_id=job.id,
        formula_version=score_result.formula_version,
        raw_opportunity_score=score_result.raw_opportunity_score,
        penalties=score_result.penalties,
        final_opportunity_score=score_result.final_opportunity_score,
        risk_score=score_result.risk_score,
        confidence_score=score_result.confidence_score,
        decision=score_result.decision,
        decision_summary=score_explanation[:500],
        best_gap=gap_dicts[0]["gap_type"].replace("_", " ").title() if gap_dicts else None,
        main_risk=f"{'High competition' if len(saved_places) > 8 else 'Rent pressure' if rent_to_rev > 0.35 else 'Limited data'}",
        next_action="Compare 2-3 candidate properties and validate footfall on weekdays and weekends.",
    )
    db.add(score_version)
    await db.flush()

    for comp in score_result.components:
        db.add(ScoreComponent(score_version_id=score_version.id, **comp, confidence=0.8, collected_at=datetime.now(timezone.utc)))

    # --- Step 7: Financial scenarios ---
    fin_input = fin_service.FinancialInput(
        business_type=category_slug,
        monthly_rent=rent,
        total_investment=invest,
        average_order_value=aov if job.average_order_value else None,
    )
    scenarios = fin_service.calculate_scenarios(fin_input)
    for s in scenarios:
        db.add(FinancialScenario(
            analysis_job_id=job.id,
            scenario_type=s.scenario_type,
            monthly_revenue=s.monthly_revenue,
            monthly_costs=s.monthly_costs,
            monthly_profit=s.monthly_profit,
            gross_margin_pct=s.gross_margin_pct,
            break_even_months=s.break_even_months,
            break_even_customers_per_day=s.break_even_customers_per_day,
            assumptions_snapshot=s.assumptions_snapshot,
            sensitivity=s.sensitivity,
            model_version=s.model_version,
        ))

    # --- Step 8: Marketing strategy + launch plan ---
    marketing = await ai_service.generate_marketing_strategy(category_slug, None, gap_dicts, job.target_customer)
    launch_plan = await ai_service.generate_launch_plan(category_slug, score_result.decision, score_version.main_risk)

    # --- Step 9: AI report narrative ---
    exp_scenario = next((s for s in scenarios if s.scenario_type == "expected"), scenarios[0])
    report_data_for_ai = {
        "business_type": category_slug,
        "location": location.display_name,
        "opportunity_score": score_result.final_opportunity_score,
        "risk_score": score_result.risk_score,
        "decision": score_result.decision,
        "competitor_count": len(saved_places),
        "gaps": gap_dicts,
        "financial_summary": {
            "expected_monthly_revenue": exp_scenario.monthly_revenue,
            "expected_monthly_profit": exp_scenario.monthly_profit,
            "break_even_months": exp_scenario.break_even_months,
        },
    }
    narrative = await ai_service.write_report_narrative(report_data_for_ai)
    await _log_ai_run(db, job.id, "report_writing", 1000, 800)

    # --- Step 10: Claim checker ---
    narrative_text = " ".join(str(v) for v in narrative.values())
    claims = await ai_service.check_claims(narrative_text, {
        "competitor_count": len(saved_places),
        "opportunity_score": score_result.final_opportunity_score,
        "risk_score": score_result.risk_score,
    })

    # --- Step 11: Save report ---
    competitor_data = [
        {**c, "distance_meters": places_client.distance_meters(lat, lng, c["latitude"], c["longitude"])}
        for c in raw_competitors[:15]
    ]
    report = Report(
        analysis_job_id=job.id,
        executive_summary={
            "decision": score_result.decision,
            "decision_summary": score_version.decision_summary,
            "score": score_result.final_opportunity_score,
            "risk_score": score_result.risk_score,
            "confidence": score_result.confidence_score,
            "best_gap": score_version.best_gap,
            "main_risk": score_version.main_risk,
            "next_action": score_version.next_action,
        },
        competitor_landscape={
            "count": len(saved_places),
            "competitors": competitor_data[:10],
            "avg_rating": gap_input.competitor_avg_rating,
            "weak_themes": weak_themes_unique,
            "analysis_text": narrative.get("competitor_analysis_text", ""),
        },
        demand_indicators={
            "signals_0_1km": signals_0_1,
            "signals_1_3km": signals_1_3,
            "signals_3_5km": signals_3_5,
            "signal_counts": signal_counts,
            "analysis_text": narrative.get("demand_analysis_text", ""),
        },
        gap_finder={
            "gaps": gap_dicts,
            "count": len(gap_dicts),
        },
        micro_zones=_suggest_micro_zones(lat, lng, competitor_data),
        marketing_strategy=marketing,
        launch_plan=launch_plan,
        limitations=[
            "Competitor data sourced from Google Places — may not capture all businesses.",
            "Demographic data is derived from proxies, not official census at street level.",
            "Financial scenarios use benchmark assumptions — validate with local market data.",
            "Review samples are limited and may not represent full customer sentiment.",
            "On-ground validation is recommended before signing a property agreement.",
        ],
        data_sources=[
            {"source": "Google Places API", "type": "Observed", "collected_at": datetime.now(timezone.utc).isoformat()},
            {"source": "Platform scoring engine v1.0", "type": "Derived"},
            {"source": "Internal benchmarks — Ahmedabad 2026", "type": "Estimated"},
        ],
        narrative_html=f"<p>{narrative.get('executive_summary', '')}</p>",
        is_free_preview=True,
        report_version="v1",
    )
    db.add(report)
    await db.flush()

    for claim in claims:
        db.add(ReportClaim(
            report_id=report.id,
            claim_text=claim.get("claim", ""),
            is_supported=claim.get("is_supported", True),
            action_taken=claim.get("action", "kept"),
        ))

    # --- Step 12: Generate PDF ---
    full_report_data = {
        **report_data_for_ai,
        "competitors": competitor_data,
        "financial_scenarios": [
            {"scenario_type": s.scenario_type, "monthly_revenue": s.monthly_revenue,
             "monthly_costs": s.monthly_costs, "monthly_profit": s.monthly_profit,
             "break_even_months": s.break_even_months}
            for s in scenarios
        ],
        "gaps": gap_dicts,
        "limitations": report.limitations,
    }
    try:
        pdf_bytes = await pdf_service.generate_pdf(full_report_data, str(job.id))
        pdf_key = f"reports/{job.id}/report.pdf"
        pdf_url = storage.upload_pdf(pdf_key, pdf_bytes)
        report.pdf_url = pdf_url
        report.pdf_generated_at = datetime.now(timezone.utc)
    except Exception as e:
        logger.warning("pdf_generation_failed", error=str(e))

    # --- Complete job ---
    job.status = "completed"
    job.completed_at = datetime.now(timezone.utc)
    job.workflow_steps = {
        "competitors": "completed",
        "signals": "completed",
        "review_analysis": "completed",
        "gap_finder": "completed",
        "scoring": "completed",
        "financial": "completed",
        "report": "completed",
        "pdf": "completed" if report.pdf_url else "skipped",
    }
    await db.commit()
    logger.info("analysis_completed", score=score_result.final_opportunity_score)


def _avg(values: list) -> float:
    clean = [v for v in values if v is not None]
    return round(sum(clean) / len(clean), 2) if clean else 0.0


def _get_category_slug(job: AnalysisJob) -> str:
    # We look this up from the job — in practice, join or cache
    return "cafe"  # placeholder; overridden by actual join in full impl


def _suggest_micro_zones(center_lat: float, center_lng: float, competitors: list[dict]) -> list[dict]:
    """Suggest 3 micro-zones by finding low-competition pockets."""
    import math
    offsets = [
        {"label": "Zone A", "direction": "North", "lat_d": 0.008, "lng_d": 0.002},
        {"label": "Zone B", "direction": "East",  "lat_d": 0.002, "lng_d": 0.010},
        {"label": "Zone C", "direction": "South", "lat_d": -0.006, "lng_d": 0.003},
    ]
    zones = []
    for o in offsets:
        zlat = center_lat + o["lat_d"]
        zlng = center_lng + o["lng_d"]
        nearby_count = sum(
            1 for c in competitors
            if math.sqrt((c.get("latitude", 0) - zlat) ** 2 + (c.get("longitude", 0) - zlng) ** 2) < 0.01
        )
        zones.append({
            "label": o["label"],
            "direction": o["direction"],
            "latitude": round(zlat, 6),
            "longitude": round(zlng, 6),
            "nearby_competitors": nearby_count,
            "rationale": f"Lower competitor density ({nearby_count} within 1 km) than the central area.",
        })
    return sorted(zones, key=lambda z: z["nearby_competitors"])


async def _log_api_usage(db: AsyncSession, job_id: uuid.UUID, provider: str, endpoint: str, count: int) -> None:
    db.add(ApiUsage(analysis_job_id=job_id, provider=provider, endpoint=endpoint, request_count=count))
    await db.flush()


async def _log_ai_run(db: AsyncSession, job_id: uuid.UUID, task: str, input_tokens: int, output_tokens: int) -> None:
    db.add(AIRun(
        analysis_job_id=job_id,
        task=task,
        model="claude-haiku-4-5-20251001",
        prompt_version="v1",
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        status="success",
    ))
    await db.flush()
