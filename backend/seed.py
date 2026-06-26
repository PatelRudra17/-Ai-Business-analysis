"""Seed initial business categories, subtypes, and configurations."""
import asyncio
import json

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.category import BusinessCategory, BusinessConfiguration, BusinessSubtype

CATEGORIES = [
    {
        "slug": "gym",
        "name": "Gym & Fitness Studio",
        "description": "Gyms, fitness centres, yoga studios, and related fitness businesses",
        "icon": "dumbbell",
        "display_order": 1,
        "subtypes": [
            {"slug": "full_gym", "name": "Full-Service Gym"},
            {"slug": "yoga_studio", "name": "Yoga Studio"},
            {"slug": "ladies_gym", "name": "Ladies-Only Gym"},
            {"slug": "crossfit", "name": "CrossFit / Functional Fitness"},
            {"slug": "martial_arts", "name": "Martial Arts / MMA"},
        ],
        "config": {
            "version": "gym-v1",
            "competitor_queries": ["gym", "fitness center", "yoga studio", "crossfit", "sports club"],
            "positive_signals": ["residential_society", "office_complex", "college", "corporate_park", "sports_complex"],
            "negative_signals": ["high_competition", "poor_parking", "no_ground_floor", "low_residential_density"],
            "review_taxonomy": ["equipment", "cleanliness", "staff", "pricing", "parking", "overcrowding", "air_conditioning", "amenities"],
            "scoring_weights": {"demand_potential": 0.25, "competition_gap": 0.20, "accessibility": 0.15, "financial_fit": 0.15, "growth_potential": 0.10, "unmet_need": 0.10, "data_confidence": 0.05},
            "financial_model": "gym-v1",
            "scoring_model": "gym-location-v1",
        },
    },
    {
        "slug": "cafe",
        "name": "Café & Small Restaurant",
        "description": "Cafés, coffee shops, tea houses, and small dine-in restaurants",
        "icon": "coffee",
        "display_order": 2,
        "subtypes": [
            {"slug": "premium_cafe", "name": "Premium Café"},
            {"slug": "budget_cafe", "name": "Budget / Quick-Service Café"},
            {"slug": "tea_house", "name": "Tea House / Chai Bar"},
            {"slug": "bakery_cafe", "name": "Bakery + Café"},
            {"slug": "cloud_kitchen_cafe", "name": "Delivery-First Café"},
        ],
        "config": {
            "version": "cafe-v1",
            "competitor_queries": ["cafe", "coffee shop", "bakery", "tea shop", "restaurant"],
            "positive_signals": ["college", "office", "coworking_space", "shopping_mall", "metro_station"],
            "negative_signals": ["high_competition", "poor_parking", "high_rent", "low_evening_activity"],
            "review_taxonomy": ["taste", "price", "service", "ambience", "parking", "waiting_time", "seating", "cleanliness"],
            "scoring_weights": {"demand_potential": 0.25, "competition_gap": 0.20, "accessibility": 0.15, "financial_fit": 0.15, "growth_potential": 0.10, "unmet_need": 0.10, "data_confidence": 0.05},
            "financial_model": "cafe-v1",
            "scoring_model": "cafe-location-v1",
        },
    },
    {
        "slug": "salon",
        "name": "Salon & Beauty Studio",
        "description": "Hair salons, beauty parlours, nail salons, and grooming studios",
        "icon": "scissors",
        "display_order": 3,
        "subtypes": [
            {"slug": "unisex_salon", "name": "Unisex Salon"},
            {"slug": "ladies_salon", "name": "Ladies Salon / Beauty Parlour"},
            {"slug": "gents_salon", "name": "Gents Salon / Barbershop"},
            {"slug": "nail_studio", "name": "Nail Studio"},
            {"slug": "premium_spa", "name": "Premium Spa & Wellness"},
        ],
        "config": {
            "version": "salon-v1",
            "competitor_queries": ["salon", "beauty parlour", "hair studio", "nail salon", "spa", "barbershop"],
            "positive_signals": ["apartment_complex", "shopping_area", "women_clothing_store", "gym", "wedding_store"],
            "negative_signals": ["high_competition", "low_foot_traffic", "poor_visibility", "low_residential_density"],
            "review_taxonomy": ["hygiene", "staff_behaviour", "waiting_time", "price", "appointment_management", "service_quality"],
            "scoring_weights": {"demand_potential": 0.25, "competition_gap": 0.20, "accessibility": 0.15, "financial_fit": 0.15, "growth_potential": 0.10, "unmet_need": 0.10, "data_confidence": 0.05},
            "financial_model": "salon-v1",
            "scoring_model": "salon-location-v1",
        },
    },
]


async def seed():
    async with AsyncSessionLocal() as session:
        for cat_data in CATEGORIES:
            existing = await session.scalar(select(BusinessCategory).where(BusinessCategory.slug == cat_data["slug"]))
            if existing:
                print(f"Category '{cat_data['slug']}' already exists, skipping.")
                continue

            cat = BusinessCategory(
                slug=cat_data["slug"],
                name=cat_data["name"],
                description=cat_data["description"],
                icon=cat_data["icon"],
                display_order=cat_data["display_order"],
            )
            session.add(cat)
            await session.flush()

            for st in cat_data["subtypes"]:
                session.add(BusinessSubtype(category_id=cat.id, slug=st["slug"], name=st["name"]))

            cfg = cat_data["config"]
            session.add(BusinessConfiguration(
                category_id=cat.id,
                version=cfg["version"],
                competitor_queries=cfg["competitor_queries"],
                positive_signals=cfg["positive_signals"],
                negative_signals=cfg["negative_signals"],
                review_taxonomy=cfg["review_taxonomy"],
                scoring_weights=cfg["scoring_weights"],
                financial_model=cfg["financial_model"],
                scoring_model=cfg["scoring_model"],
            ))

            print(f"Seeded category: {cat_data['name']}")

        await session.commit()
        print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
