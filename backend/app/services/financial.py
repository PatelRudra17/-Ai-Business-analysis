"""Financial scenario engine — all arithmetic done in code, not AI."""
from __future__ import annotations

from dataclasses import dataclass


# ---------- Benchmark defaults (Ahmedabad 2026) ----------
BENCHMARKS: dict[str, dict] = {
    "gym": {
        "monthly_members":       {"conservative": 80,  "expected": 150, "optimistic": 250},
        "monthly_fee":           {"conservative": 1200, "expected": 1500, "optimistic": 2000},
        "staff_cost":            {"pct_revenue": 0.25},
        "utilities":             {"fixed": 15000},
        "supplies":              {"pct_revenue": 0.05},
        "marketing":             {"pct_revenue": 0.08},
        "setup_cost":            {"default": 1500000},
        "gross_margin_typical":  0.60,
        "aov_label":             "monthly membership fee",
    },
    "cafe": {
        "daily_covers":          {"conservative": 40,  "expected": 80,  "optimistic": 140},
        "average_order_value":   {"conservative": 200, "expected": 300, "optimistic": 450},
        "cogs_pct":              {"conservative": 0.40, "expected": 0.35, "optimistic": 0.30},
        "staff_cost":            {"pct_revenue": 0.20},
        "utilities":             {"fixed": 12000},
        "marketing":             {"pct_revenue": 0.06},
        "setup_cost":            {"default": 1200000},
        "gross_margin_typical":  0.60,
        "aov_label":             "average order value",
    },
    "salon": {
        "daily_clients":         {"conservative": 10,  "expected": 20,  "optimistic": 35},
        "average_service_value": {"conservative": 400, "expected": 700, "optimistic": 1200},
        "cogs_pct":              {"conservative": 0.30, "expected": 0.25, "optimistic": 0.20},
        "staff_cost":            {"pct_revenue": 0.35},
        "utilities":             {"fixed": 8000},
        "marketing":             {"pct_revenue": 0.07},
        "setup_cost":            {"default": 800000},
        "gross_margin_typical":  0.65,
        "aov_label":             "average service value",
    },
}


@dataclass
class FinancialInput:
    business_type: str
    monthly_rent: float
    total_investment: float
    average_order_value: float | None = None


@dataclass
class Scenario:
    scenario_type: str
    monthly_revenue: float
    monthly_costs: float
    monthly_profit: float
    gross_margin_pct: float
    break_even_months: float
    break_even_customers_per_day: float
    assumptions_snapshot: dict
    model_version: str = "financial-v1"
    sensitivity: dict = None

    def __post_init__(self):
        if self.sensitivity is None:
            self.sensitivity = {}


def calculate_scenarios(inp: FinancialInput) -> list[Scenario]:
    bm = BENCHMARKS.get(inp.business_type, BENCHMARKS["cafe"])
    scenarios = []
    for stype in ("conservative", "expected", "optimistic"):
        s = _build_scenario(inp, bm, stype)
        scenarios.append(s)
    return scenarios


def _build_scenario(inp: FinancialInput, bm: dict, stype: str) -> Scenario:
    btype = inp.business_type

    if btype == "gym":
        members = bm["monthly_members"][stype]
        fee = inp.average_order_value or bm["monthly_fee"][stype]
        revenue = members * fee
        cogs = 0.0
        staff = revenue * bm["staff_cost"]["pct_revenue"]
        util = bm["utilities"]["fixed"]
        supplies = revenue * bm["supplies"]["pct_revenue"]
        marketing = revenue * bm["marketing"]["pct_revenue"]
        other = 5000
        total_costs = inp.monthly_rent + staff + util + supplies + marketing + other
        gross_margin = 1.0 - (supplies / revenue if revenue else 0)
        bep_cust_day = None

    elif btype == "salon":
        daily = bm["daily_clients"][stype]
        avg = inp.average_order_value or bm["average_service_value"][stype]
        revenue = daily * 26 * avg  # 26 working days
        cogs_pct = bm["cogs_pct"][stype]
        cogs = revenue * cogs_pct
        staff = revenue * bm["staff_cost"]["pct_revenue"]
        util = bm["utilities"]["fixed"]
        marketing = revenue * bm["marketing"]["pct_revenue"]
        other = 3000
        total_costs = inp.monthly_rent + cogs + staff + util + marketing + other
        gross_margin = 1.0 - cogs_pct
        bep_cust_day = daily

    else:  # cafe default
        daily = bm["daily_covers"][stype]
        aov = inp.average_order_value or bm["average_order_value"][stype]
        revenue = daily * 30 * aov
        cogs_pct = bm["cogs_pct"][stype]
        cogs = revenue * cogs_pct
        staff = revenue * bm["staff_cost"]["pct_revenue"]
        util = bm["utilities"]["fixed"]
        marketing = revenue * bm["marketing"]["pct_revenue"]
        other = 4000
        total_costs = inp.monthly_rent + cogs + staff + util + marketing + other
        gross_margin = 1.0 - cogs_pct
        bep_cust_day = _break_even_customers(inp.monthly_rent + util + staff + marketing + other, aov, cogs_pct)

    profit = revenue - total_costs
    bep_months = (inp.total_investment / profit) if profit > 0 else 999
    gm_pct = round((revenue - (total_costs - inp.monthly_rent - bm.get("utilities", {}).get("fixed", 0))) / revenue, 3) if revenue else 0

    sensitivity = {
        "rent_plus_20pct": round(profit - inp.monthly_rent * 0.20, 0),
        "revenue_minus_20pct": round(profit - revenue * 0.20, 0),
        "aov_minus_15pct": round(profit - revenue * 0.15, 0),
    }

    return Scenario(
        scenario_type=stype,
        monthly_revenue=round(revenue, 0),
        monthly_costs=round(total_costs, 0),
        monthly_profit=round(profit, 0),
        gross_margin_pct=round(gross_margin, 3),
        break_even_months=round(min(bep_months, 120), 1),
        break_even_customers_per_day=round(bep_cust_day, 1) if bep_cust_day else 0,
        assumptions_snapshot={
            "monthly_rent": inp.monthly_rent,
            "total_investment": inp.total_investment,
            "average_order_value": inp.average_order_value,
            "scenario_type": stype,
            "benchmark_source": "internal_ahmedabad_2026",
        },
        sensitivity=sensitivity,
    )


def _break_even_customers(fixed_costs: float, aov: float, cogs_pct: float) -> float:
    contribution = aov * (1 - cogs_pct)
    if contribution <= 0:
        return 9999
    monthly_bep = fixed_costs / contribution
    return monthly_bep / 30
