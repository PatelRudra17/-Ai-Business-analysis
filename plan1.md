# Business Location Intelligence Platform
## Complete A-to-Z Product, Technology, n8n, Data, Business, and Launch Plan

---

## 1. Executive Summary

### Product idea

A web and mobile platform where a user enters:

- Business category
- Business subtype
- Proposed location
- Search radius
- Investment budget
- Maximum rent
- Target customer
- Pricing assumptions

The platform collects location and market data, analyses competitors, identifies demand signals, estimates financial outcomes, highlights risks, compares locations, and generates a complete business-location report.

### One-line value proposition

> Tell us your business idea and location, and receive a data-backed market opportunity report before you invest.

### Important product principle

The platform is **not limited to gyms**.

It should support multiple business categories through configurable, category-specific analysis models.

The recommended first release should cover only a small number of categories and locations so that the scoring, data quality, and recommendations can be validated properly.

---

# A — Aim

The platform should help entrepreneurs answer five questions:

1. Is this area suitable for my business?
2. Which part of the area offers the strongest opportunity?
3. Who are my competitors?
4. What customer needs are not being served?
5. What revenue, cost, and break-even range is realistic?

The platform should provide decision support, not guaranteed outcomes.

Recommended wording:

> This platform provides data-backed estimates, comparisons, and recommendations based on available data and user assumptions.

Avoid statements such as:

> This location guarantees success.

---

# B — Business Categories

## Initial launch categories

Start with three categories:

1. Gym and fitness studio
2. Café and small restaurant
3. Salon and beauty studio

These categories are suitable because:

- They are highly location-dependent.
- Competitors are usually visible through map data.
- Customer demand can be estimated through nearby signals.
- Entrepreneurs commonly need help selecting locations.
- Financial models can be built using understandable assumptions.

## Future categories

- Clinic
- Pharmacy
- Tuition centre
- Preschool
- Grocery store
- Cloud kitchen
- Restaurant
- Bakery
- Co-working space
- Boutique
- Electronics shop
- Car wash
- Pet-care business
- Diagnostic centre
- Furniture shop
- Hardware store
- Local service centre

## Category-specific analysis

The shared platform remains the same, but each business category requires different:

- Competitor types
- Demand signals
- Review categories
- Financial formulas
- Risk factors
- Customer profiles
- Scoring weights
- Marketing recommendations

Example:

| Business | Important location signals |
|---|---|
| Gym | Residential societies, parking, offices, young population proxies, competitor density |
| Café | Colleges, offices, shopping areas, footfall proxies, delivery demand |
| Salon | Residential density, income proxies, women-focused businesses, parking |
| Clinic | Population, pharmacies, hospitals, road access, specialty competition |
| Tuition centre | Schools, family households, student population proxies, transport |
| Grocery store | Apartment density, households, nearby stores, delivery access |
| Cloud kitchen | Delivery radius, restaurant density, rent, rider access |

---

# C — Customer Journey

```text
Landing Page
    ↓
Create Account
    ↓
Select Business Category
    ↓
Select Business Subtype
    ↓
Enter Location or Drop Map Pin
    ↓
Choose Search Radius
    ↓
Enter Budget and Business Assumptions
    ↓
Confirm Analysis
    ↓
Platform Collects and Processes Data
    ↓
User Receives Preview
    ↓
User Unlocks Full Report
    ↓
User Compares Locations or Enables Alerts
```

## User input example

```json
{
  "business_type": "cafe",
  "business_subtype": "premium_cafe",
  "location_text": "Bopal, Ahmedabad",
  "latitude": 23.033,
  "longitude": 72.465,
  "radius_meters": 3000,
  "total_investment": 1800000,
  "monthly_rent_limit": 80000,
  "average_order_value": 350,
  "target_customer": "students and young professionals",
  "preferred_floor_area_sqft": 1500,
  "parking_required": true
}
```

Users should be allowed to skip unknown values.

The system should then:

1. Suggest benchmark assumptions.
2. Show those assumptions to the user.
3. Allow editing.
4. Calculate the report using confirmed values.

---

# D — Data Strategy

The system should clearly separate four types of information.

| Data type | Example | Display label |
|---|---|---|
| Observed | Competitor name, location, rating | Observed |
| Official | Census population, registered development | Official source |
| Derived | Competition density, distance score | Platform calculation |
| Estimated | Revenue, demand, purchasing power proxy | Estimate |

## Primary data sources

| Requirement | Suggested source |
|---|---|
| Competitors | Google Places API |
| Nearby landmarks | Google Places API |
| Travel time | Google Routes API or equivalent |
| Population | Census of India |
| Public datasets | data.gov.in |
| Upcoming developments | State RERA portals |
| Government schemes | MSME and official government portals |
| Rent | User input initially |
| Commercial property | Later through property partners |
| Flood or environmental risk | Official geospatial datasets |
| Local validation | User surveys and expert verification |

## Data limitations

The platform must not claim that map APIs directly provide:

- Exact household income
- Exact customer age by street
- Real pedestrian footfall
- Apartment occupancy
- Guaranteed revenue
- Complete review history
- Every upcoming development

Where exact data is unavailable, use clearly labelled proxies.

Example:

> Activity Potential Score

instead of:

> Actual daily footfall

---

# E — Evidence and Confidence System

Every important recommendation should include:

- Data source
- Collection date
- Geographic level
- Calculation version
- Confidence score
- Known limitations

## Example evidence record

```json
{
  "metric": "competitor_density",
  "value": 7,
  "unit": "competitors within 3 km",
  "source": "Google Places API",
  "collected_at": "2026-06-26T10:30:00+05:30",
  "confidence": 0.91,
  "calculation_version": "competition-density-v1.0"
}
```

## Confidence formula

```text
Data Confidence =
30% Data Completeness
+ 25% Source Reliability
+ 20% Data Freshness
+ 15% Geographic Precision
+ 10% Sample Size
```

## Confidence labels

| Score | Label |
|---:|---|
| 80–100 | High confidence |
| 60–79 | Moderate confidence |
| 40–59 | Limited confidence |
| Below 40 | Insufficient data |

When confidence is too low, the system should request more information or state that the recommendation needs local verification.

---

# F — Feature Roadmap

## MVP features

- Business category selection
- Business subtype selection
- Location search and map pin
- Search radius selection
- Competitor map
- Competitor density
- Competitor review-sample analysis
- Nearby demand signals
- Gap Finder
- Opportunity Score
- Risk Score
- Three recommended micro-zones
- Revenue scenarios
- Break-even estimate
- Marketing strategy
- Thirty-day launch plan
- PDF report
- Two-location comparison

## Version 2

- Weekly location alerts
- Upcoming development detector
- Government scheme matcher
- Candidate property comparison
- Hindi input
- Gujarati input
- Voice input
- Consultant dashboard
- White-label reports

## Version 3

- Mobile application
- More Indian cities
- More business categories
- Commercial property partnerships
- Advanced environmental risk
- Licensed demographic datasets
- Footfall-data partnerships
- Predictive trend analysis

---

# G — Gap Finder

The Gap Finder should combine deterministic calculations with AI explanation.

## Inputs

- Competitors by subtype
- Competitor price positioning
- Opening hours
- Ratings
- Review count
- Review complaints
- Nearby residential signals
- Nearby commercial signals
- Target customer
- Relevant complementary businesses
- User budget

## Examples

### Gym gap

```text
High residential density
+ low number of women-focused fitness businesses
+ privacy or overcrowding complaints
= possible ladies-only gym opportunity
```

### Café gap

```text
High college and office density
+ few late-night cafés
+ complaints about seating and waiting time
= possible late-night work-friendly café opportunity
```

### Salon gap

```text
High residential density
+ premium customer proxies
+ low premium salon supply
+ complaints about hygiene and appointments
= possible premium appointment-based salon opportunity
```

## Output example

```json
{
  "gap_type": "late_night_work_friendly_cafe",
  "opportunity_score": 79,
  "confidence": 0.72,
  "supporting_signals": [
    "High density of colleges and offices",
    "Few cafés remain open after 10 PM",
    "Competitor reviews mention limited seating"
  ],
  "limitations": [
    "Review analysis is based on available samples",
    "On-ground footfall validation is recommended"
  ]
}
```

---

# H — High-Level Architecture

```text
Web App / Mobile App
        │
        ▼
     FastAPI
Authentication, billing, validation,
projects, permissions, job status
        │
        ├──────────────► PostgreSQL + PostGIS
        │                Locations, scores, reports,
        │                competitors, spatial queries
        │
        ├──────────────► Redis
        │                Queue and cache
        │
        ▼
       n8n
Workflow orchestration
        │
        ├── Map and place data workflows
        ├── Government data workflows
        ├── Review analysis workflows
        ├── Financial workflows
        ├── Scoring workflows
        ├── Report workflows
        └── Alert workflows
        │
        ▼
AI Models + External APIs
```

## Recommended technology stack

| Layer | Technology |
|---|---|
| Web frontend | Next.js with TypeScript |
| Styling | Tailwind CSS |
| Maps | Google Maps JavaScript API |
| Mobile later | React Native |
| Backend | FastAPI |
| Database | PostgreSQL with PostGIS |
| Queue | Redis |
| Workflows | Self-hosted n8n |
| Storage | S3-compatible object storage |
| AI | Claude, OpenAI, or Groq-hosted models |
| Authentication | Clerk, Auth0, Supabase Auth, or JWT |
| Payments | Razorpay |
| Monitoring | Sentry and structured logs |
| Product analytics | PostHog or equivalent |

---

# I — Business Configuration System

Each business category should be controlled through configuration.

## Example: café configuration

```json
{
  "business_type": "cafe",
  "competitor_queries": [
    "cafe",
    "coffee shop",
    "bakery",
    "tea shop"
  ],
  "positive_signals": [
    "college",
    "office",
    "coworking_space",
    "shopping_mall",
    "metro_station"
  ],
  "negative_signals": [
    "high_competition",
    "poor_parking",
    "high_rent",
    "low_evening_activity"
  ],
  "review_taxonomy": [
    "taste",
    "price",
    "service",
    "ambience",
    "parking",
    "waiting_time",
    "seating",
    "cleanliness"
  ],
  "financial_model": "cafe-v1",
  "scoring_model": "cafe-location-v1"
}
```

## Example: salon configuration

```json
{
  "business_type": "salon",
  "competitor_queries": [
    "salon",
    "beauty parlour",
    "hair studio",
    "nail salon"
  ],
  "positive_signals": [
    "apartment_complex",
    "shopping_area",
    "women_clothing_store",
    "gym",
    "wedding_store"
  ],
  "review_taxonomy": [
    "hygiene",
    "staff_behaviour",
    "waiting_time",
    "price",
    "appointment_management",
    "service_quality"
  ],
  "financial_model": "salon-v1",
  "scoring_model": "salon-location-v1"
}
```

This configuration-driven design makes the platform scalable.

---

# J — n8n Workflow Plan

Do not create one giant workflow.

Use a parent workflow with specialist subworkflows.

## WF-01: Analysis Intake

```text
Webhook Trigger
→ Validate API Signature
→ Validate Input
→ Normalize Location
→ Create Analysis Job
→ Return Job ID
→ Execute Research Orchestrator
```

Response:

```json
{
  "analysis_id": "an_12345",
  "status": "queued"
}
```

## WF-02: Research Orchestrator

```text
Execute Workflow Trigger
→ Update Job Status
→ Load Business Configuration
→ Run Competitor Collector
→ Run Demand Signal Collector
→ Run Demographic Mapper
→ Run Development Collector
→ Run Financial Engine
→ Run Scoring Engine
→ Run AI Interpretation
→ Run Report Generator
→ Mark Job Completed
→ Notify User
```

Independent collectors should run in parallel.

## WF-03: Search Grid Generator

```text
Receive Centre and Radius
→ Generate Search Grid
→ Remove Points Outside Boundary
→ Attach Search Types
→ Return Search Tasks
```

## WF-04: Competitor Collector

```text
Receive Search Tasks
→ Batch Requests
→ Rate Limit
→ Search Nearby Places
→ Normalize Results
→ Deduplicate by Place ID
→ Save Source References
→ Return Competitor List
```

## WF-05: Place Details Collector

```text
Receive Place IDs
→ Check Existing Snapshot
→ Refresh When Needed
→ Retrieve Details
→ Normalize Rating, Hours and Review Count
→ Save Snapshot
```

## WF-06: Review Weakness Analyzer

```text
Load Review Samples
→ Remove Invalid Records
→ Send to Structured AI Extractor
→ Validate JSON
→ Aggregate Themes in Code Node
→ Calculate Confidence
→ Save Weakness Categories
```

AI output:

```json
{
  "themes": [
    {
      "category": "waiting_time",
      "sentiment": "negative",
      "severity": 4,
      "evidence": "Long waiting time during weekends"
    }
  ]
}
```

The AI should classify text.

Code should calculate counts and scores.

## WF-07: Demand Signal Collector

```text
Load Business Configuration
→ Generate Relevant Searches
→ Search Nearby Signals
→ Deduplicate
→ Group by Distance Ring
→ Calculate Density Metrics
→ Store Results
```

Distance rings:

- 0–1 km
- 1–3 km
- 3–5 km

## WF-08: Demographic Mapper

```text
Receive Coordinates
→ Identify Administrative Area
→ Load Available Official Dataset
→ Match Ward, Town, or Region
→ Calculate Population Proxies
→ Store Source Year and Geography
```

## WF-09: Upcoming Development Collector

```text
Scheduled Trigger
→ Retrieve Permitted Development Records
→ Normalize Projects
→ Match Projects to Area
→ Store Type and Completion Information
```

## WF-10: Location Scoring

```text
Load Metrics
→ Check Minimum Data Requirements
→ Calculate Component Scores
→ Apply Penalties
→ Calculate Confidence
→ Save Formula Version
```

## WF-11: Financial Scenario Engine

```text
Load User Inputs
→ Fill Missing Benchmarks
→ Conservative Scenario
→ Expected Scenario
→ Optimistic Scenario
→ Sensitivity Analysis
→ Save Results
```

## WF-12: AI Report Writer

```text
Load Verified Data
→ Remove Unsupported Fields
→ Build Prompt Package
→ Call AI Model
→ Validate Structured Output
→ Run Claim Checker
→ Save Report Narrative
```

## WF-13: Report Generator

```text
Load Report JSON
→ Render HTML
→ Add Maps and Charts
→ Generate PDF
→ Upload to Storage
→ Save Report URL
```

## WF-14: Location Comparison

```text
Load Analysis A
→ Load Analysis B
→ Confirm Same Business Type
→ Normalize Scores
→ Compare Components
→ Generate Recommendation
```

## WF-15: Weekly Monitoring

```text
Schedule Trigger
→ Load Watched Locations
→ Refresh Selected Sources
→ Compare with Previous Snapshot
→ Score Significance
→ Generate Alert
→ Send Email, WhatsApp, or Push Notification
```

---

# K — Knowledge Base

Create a versioned knowledge base containing:

- Category-specific cost assumptions
- Equipment requirements
- Staffing assumptions
- Business benchmarks
- Marketing ideas
- Review taxonomies
- Government schemes
- Customer personas
- Report templates
- Local-language phrases

Example:

```json
{
  "record_id": "cafe_staff_cost_ahmedabad_001",
  "business_type": "cafe",
  "city": "Ahmedabad",
  "valid_from": "2026-06-01",
  "source": "internal_research",
  "verified_by": "analyst_12",
  "confidence": 0.76
}
```

Do not use a vector database for financial calculations.

Use it for explanation, search, and report context.

---

# L — Location Scoring Model

## Generic opportunity score

```text
Opportunity Score =
25% Demand Potential
+ 20% Competition Gap
+ 15% Accessibility
+ 15% Financial Fit
+ 10% Growth Potential
+ 10% Unmet Customer Need
+ 5% Data Confidence
```

Weights should change by category.

## Demand Potential

Possible inputs:

- Residential density
- Commercial density
- Relevant institutions
- Target-customer proxies
- Complementary businesses
- Activity potential
- Development potential

## Competition Gap

Possible inputs:

- Number of competitors
- Distance distribution
- Business subtype coverage
- Competitor quality
- Review weaknesses
- Pricing gaps
- Opening-hour gaps

## Accessibility

Possible inputs:

- Road connectivity
- Parking
- Transit
- Travel time
- Visibility
- Floor access
- Delivery access

## Financial Fit

Possible inputs:

- Rent-to-revenue ratio
- Investment requirement
- Gross margin
- Break-even time
- Staffing cost
- Operating cost

## Risk penalties

```text
Final Score =
Opportunity Score
- Overcompetition Penalty
- Financial Stress Penalty
- Data Uncertainty Penalty
- Environmental Risk Penalty
- Regulatory Risk Penalty
```

## Scoring version

```json
{
  "formula_version": "cafe-opportunity-v1.0",
  "raw_score": 82,
  "penalties": 8,
  "final_score": 74
}
```

---

# M — AI Responsibilities

## Use AI for

- Review classification
- Review-theme extraction
- Translation
- Business-gap explanation
- Marketing recommendations
- Score explanation
- Report writing
- Thirty-day plan
- Natural-language conversation

## Do not use AI for

- Counting competitors
- Distance calculations
- Financial arithmetic
- Score calculation
- Scheme eligibility decisions
- Inventing demographics
- Making unsupported claims
- Deciding source reliability without rules

## Suggested model arrangement

| Task | Model |
|---|---|
| Review classification | Fast low-cost model |
| Translation | Multilingual model |
| Gap explanation | Strong reasoning model |
| Final report | Strong long-context model |
| Claim checker | Separate structured model call |

Create an AI model gateway in FastAPI so the platform is not tied to one provider.

---

# N — AI Agent Design

Create one Research Coordinator Agent.

## Agent tools

```text
collect_competitor_data
collect_area_signals
get_demographic_context
find_upcoming_developments
calculate_location_score
calculate_financial_scenarios
compare_locations
match_government_schemes
generate_report
```

## Agent system instruction

```text
You are a business-location research coordinator.

Use tools to retrieve verified information.

Never invent competitors, statistics, demographic data,
financial values, government schemes, or risk values.

Clearly separate:
1. observed facts,
2. official facts,
3. calculated metrics,
4. estimates,
5. recommendations.

Do not calculate scores yourself.
Use the scoring tool.

Do not guarantee business success.

When confidence is low, clearly state the limitation.

Return output matching the required JSON schema.
```

The agent should coordinate workflows, not directly control scoring formulas or the database.

---

# O — Report Structure

## Full report sections

1. Executive decision
2. Opportunity Score
3. Risk Score
4. Data confidence
5. Business and location summary
6. Competitor landscape
7. Competitor map
8. Review weakness analysis
9. Customer and demand indicators
10. Market gaps
11. Recommended micro-zones
12. Candidate property checklist
13. Revenue scenarios
14. Break-even estimate
15. Risk analysis
16. Marketing strategy
17. Thirty-day launch plan
18. Assumptions
19. Limitations
20. Data sources and dates

## Decision output

```json
{
  "decision": "PROMISING_WITH_CONDITIONS",
  "score": 74,
  "risk_score": 42,
  "confidence": 68,
  "summary": "The area shows strong demand but requires careful property selection because of competition and rental pressure.",
  "best_gap": "Late-night work-friendly premium café",
  "main_risk": "High rent and evening parking limitations",
  "next_action": "Compare three candidate properties and validate weekday and weekend activity."
}
```

## Decision labels

- Strong opportunity
- Promising with conditions
- Needs local validation
- High-risk opportunity
- Insufficient data

---

# P — Product Screens

## Public screens

- Landing page
- How it works
- Sample report
- Pricing
- Business-category pages
- Locality pages
- Login
- Registration

## User application

- Dashboard
- New analysis wizard
- Business-category selector
- Map and radius selector
- Assumption editor
- Processing status
- Full report
- Competitor map
- Location comparison
- Candidate property comparison
- Alerts
- Billing
- Account settings

## Admin application

- Users
- Organizations
- Analyses
- Failed workflows
- API usage
- AI cost
- Scoring configuration
- Business-category configuration
- Knowledge-base records
- Report review
- Payments
- Data freshness
- Audit logs

---

# Q — Quality Assurance

## Formula tests

Test:

- Competitor deduplication
- Distance rings
- Score boundaries
- Risk penalties
- Revenue arithmetic
- Break-even calculations
- Missing-data handling
- Financial assumptions
- Comparison normalization

## AI evaluations

Create reviewed examples for:

- Positive reviews
- Negative reviews
- Mixed-language reviews
- Gujarati
- Hindi
- Sarcasm
- Duplicate text
- Irrelevant reviews
- Low-data areas

Measure:

- Classification accuracy
- Unsupported-claim rate
- JSON validity
- Limitation disclosure
- Report consistency
- Translation quality

## Golden report testing

Maintain a set of manually approved reports.

After every formula, workflow, or prompt change:

1. Regenerate reports.
2. Compare scores.
3. Compare recommendations.
4. Check financial outputs.
5. Detect unsupported claims.
6. Review confidence labels.

## Pilot verification

Ask local business owners and consultants to assess:

- Competitor completeness
- Area accuracy
- Realism
- Recommendation usefulness
- Financial assumptions
- Missing information

---

# R — Revenue Model

## Suggested starting prices

| Product | Suggested price |
|---|---:|
| Free preview | ₹0 |
| Single report | ₹999–₹1,999 |
| Two-location comparison | ₹1,999–₹2,999 |
| Monitoring plan | ₹2,999/month |
| Consultant plan | ₹9,999/month |
| Custom feasibility report | ₹15,000+ |

These prices must be validated with customers.

## Free preview

Show:

- Competitor count
- Partial score
- One opportunity
- One major risk
- Blurred micro-zones

## Paid report

Unlock:

- Complete competitor analysis
- Gap Finder
- Financial scenarios
- Recommended micro-zones
- Marketing plan
- Thirty-day plan
- PDF
- Comparison
- Assumptions and evidence

## Unit-economic targets

```text
Direct cost per standard report: below ₹150
Gross margin: above 75%
Preview-to-paid conversion: above 8%
```

---

# S — Security, Privacy, and Compliance

## Required controls

- Keep API keys server-side.
- Encrypt credentials.
- Use separate development and production environments.
- Sign internal webhooks.
- Rate-limit users and IP addresses.
- Validate every request.
- Use tenant IDs.
- Maintain audit logs.
- Back up the database.
- Store minimum personal data.
- Support account deletion.
- Support data export.
- Remove secrets from logs.
- Do not expose n8n directly without authentication.
- Add role-based access.

## Report disclaimer

> This report is a decision-support tool based on available data, user-provided assumptions, and calculated estimates. It does not guarantee revenue, demand, regulatory approval, financing, property suitability, or business success. Users should independently verify legal, financial, property, and local-market conditions before investing.

Obtain legal review before production launch.

---

# T — Team

## Minimum serious team

| Role | Responsibility |
|---|---|
| Founder or product lead | Customer discovery and priorities |
| Full-stack developer | Frontend and backend |
| Data engineer | PostGIS, collectors, scoring |
| n8n and AI engineer | Workflows, prompts, model routing |
| UI/UX designer | Wizard, map, reports |
| Business analyst | Category assumptions and validation |
| Legal/accounting adviser | Compliance and disclaimers |

A technical founder may initially combine several roles.

---

# U — Infrastructure and Operations

## Local development

```text
Docker Compose
├── Next.js
├── FastAPI
├── PostgreSQL/PostGIS
├── Redis
├── n8n
├── MinIO
└── Worker Services
```

## Production MVP

```text
Load Balancer
├── Next.js Application
├── FastAPI API
├── n8n Main Instance
├── n8n Worker
├── PostgreSQL/PostGIS
├── Redis
└── S3-Compatible Storage
```

## Operational requirements

- Workflow retries
- Dead-letter handling
- Idempotent jobs
- API usage monitoring
- AI token monitoring
- Cost-per-report tracking
- Database backups
- Error alerts
- Source freshness alerts
- Workflow execution logs
- Service-health dashboard

---

# V — Validation Before Full Development

## Customer interviews

Interview:

- 10 people planning a business
- 5 existing business owners
- 3 commercial-property brokers
- 2 consultants
- 2 chartered accountants or finance advisers

Ask:

- How did you select your location?
- What information was difficult to obtain?
- Which mistakes did you make?
- Did you hire a consultant?
- What data would you trust?
- What would you pay for this report?
- Which part of the report would change your decision?

## Concierge prototype

Before full automation:

1. Create five reports manually.
2. Use real competitor and area data.
3. Present them to potential customers.
4. Ask whether the report changed their decision.
5. Charge at least one customer.
6. Record what information customers requested most.

Do not rely only on verbal interest.

Measure willingness to pay.

---

# W — Weekly Alerts

Possible alerts:

- New competitor
- Competitor closure
- Rating change
- Review-count spike
- New complaint pattern
- New property development
- New complementary business
- New government scheme
- Increased risk
- Reduced data confidence

## Alert score

```text
Alert Importance =
Change Magnitude
× Business Relevance
× Source Confidence
× Geographic Proximity
```

Only notify users above a defined threshold.

---

# X — Expansion Plan

## Category expansion sequence

1. Gym
2. Café
3. Salon
4. Clinic
5. Tuition centre
6. Cloud kitchen
7. Grocery store
8. Restaurant

The final sequence should be based on:

```text
Search Demand
× Willingness to Pay
× Data Availability
× Repeatability
÷ Category Complexity
```

## Geographic expansion

```text
Ahmedabad
→ Gandhinagar
→ Surat
→ Vadodara
→ Rajkot
→ Other Major Indian Cities
```

Expand only after data quality and category models are validated.

---

# Y — Sixteen-Week Roadmap

## Weeks 1–2: Validation

Deliverables:

- Customer interviews
- Five manual reports
- MVP scope
- Pricing test
- Initial scoring models
- Category configuration for first three businesses

Exit condition:

- At least three users say the report affected their decision.
- At least one user pays.

## Weeks 3–4: Foundation

Build:

- Repositories
- Environments
- Authentication
- PostgreSQL/PostGIS
- FastAPI
- n8n
- Redis
- Project and analysis models
- Basic dashboard
- Error monitoring

## Weeks 5–6: Competitor Intelligence

Build:

- Map input
- Search-grid generator
- Places collection
- Deduplication
- Competitor map
- Review-sample collection
- API cost tracking

## Weeks 7–8: Demand and Gap Finder

Build:

- Business-category configuration
- Demand-signal collection
- Review taxonomy
- Weakness extraction
- Gap Finder
- Confidence scoring

## Weeks 9–10: Scoring and Finance

Build:

- Opportunity Score
- Risk Score
- Financial scenarios
- Break-even model
- Assumption editor
- Sensitivity analysis

## Weeks 11–12: Report Product

Build:

- Report schema
- AI report writer
- Claim checker
- Interactive report
- PDF generator
- Source appendix

## Weeks 13–14: Commercial Features

Build:

- Razorpay
- Free preview
- Paid unlock
- Location comparison
- Notifications
- Admin cost dashboard
- Privacy and terms pages

## Weeks 15–16: Pilot and Launch

Complete:

- Pilot reports
- Formula testing
- AI evaluation
- Security review
- Load testing
- API-policy review
- Production deployment
- Launch campaign

---

# Z — Launch Checklist

## Product

- [ ] Business category selector works
- [ ] Business subtype selector works
- [ ] Location and radius work
- [ ] User assumptions are editable
- [ ] Report limitations are visible
- [ ] Comparison works
- [ ] Sample report exists
- [ ] PDF works

## Data

- [ ] Competitor collection tested
- [ ] Duplicates removed
- [ ] Source date stored
- [ ] Source year displayed
- [ ] Confidence implemented
- [ ] Data-refresh policy defined
- [ ] Development-data access reviewed

## AI

- [ ] Structured outputs
- [ ] Prompt versions
- [ ] Claim checker
- [ ] Hallucination tests
- [ ] Low-confidence fallback
- [ ] Cost limits
- [ ] Language tests

## Engineering

- [ ] Secrets protected
- [ ] Rate limits
- [ ] Queue
- [ ] Retries
- [ ] Idempotency
- [ ] Backups
- [ ] Error workflow
- [ ] Audit logs
- [ ] Monitoring

## Legal

- [ ] Privacy notice
- [ ] Terms of service
- [ ] Disclaimer
- [ ] Consent records
- [ ] Account deletion
- [ ] Data export
- [ ] Map attribution
- [ ] API storage review
- [ ] Compliance review

## Business

- [ ] Customer interviews
- [ ] Manual pilot reports
- [ ] First paid customer
- [ ] Pricing test
- [ ] Support process
- [ ] Cost dashboard
- [ ] Refund policy
- [ ] Launch channels

---

# Recommended Database Tables

```text
users
organizations
projects
business_categories
business_subtypes
business_configurations
analysis_jobs
locations
search_grids
source_records
places
place_snapshots
review_samples
review_themes
area_signals
demographic_regions
development_projects
candidate_properties
assumptions
financial_scenarios
score_versions
score_components
reports
report_claims
comparisons
alert_subscriptions
alerts
ai_runs
api_usage
payments
audit_logs
```

Common columns:

```text
id
organization_id
created_at
updated_at
source_version
```

---

# Suggested FastAPI Endpoints

```text
POST   /v1/analyses
GET    /v1/analyses/{analysis_id}
GET    /v1/analyses/{analysis_id}/status
GET    /v1/analyses/{analysis_id}/report

GET    /v1/business-categories
GET    /v1/business-categories/{category_id}/subtypes

POST   /v1/comparisons
GET    /v1/comparisons/{comparison_id}

POST   /v1/candidate-properties
GET    /v1/candidate-properties/{property_id}

POST   /v1/alerts
GET    /v1/alerts
DELETE /v1/alerts/{alert_id}

GET    /v1/usage
POST   /v1/webhooks/n8n/job-completed
POST   /v1/webhooks/razorpay
DELETE /v1/account
```

FastAPI should manage users, authorization, payments, jobs, and results.

n8n should manage data collection, processing, AI calls, reports, and alerts.

---

# Suggested MVP Budget

These are planning estimates and must be validated.

## Development

| Approach | Estimated range |
|---|---:|
| Technical founder plus freelancers | ₹4–8 lakh |
| Small experienced team | ₹10–20 lakh |
| Agency-built production MVP | ₹15–30 lakh |

## Monthly operating cost

| Category | Planning range |
|---|---:|
| Hosting and database | ₹10,000–₹30,000 |
| Maps and external APIs | ₹10,000–₹50,000 |
| AI models | ₹5,000–₹30,000 |
| Monitoring, email, and storage | ₹3,000–₹15,000 |
| Total | ₹28,000–₹1,25,000 |

Actual costs depend on:

- Number of reports
- Search radius
- Place-detail requests
- AI model
- Alert frequency
- Data refresh
- Report size

---

# Recommended First Commercial MVP

Build a multi-category platform foundation, but launch with only three tested categories:

1. Gym and fitness studio
2. Café and small restaurant
3. Salon and beauty studio

The first public version should allow a user to:

1. Select one of the supported categories.
2. Choose a subtype.
3. Enter an Ahmedabad location.
4. Set a radius.
5. Enter investment and rent assumptions.
6. View competitors and nearby signals.
7. Receive a Gap Finder result.
8. Receive an Opportunity Score and Risk Score.
9. View three financial scenarios.
10. Receive three recommended micro-zones.
11. Download a transparent report.
12. Compare two locations.

The technical design should support adding new categories through configuration rather than rebuilding the platform.

---

# Final Product Vision

```text
Business Location Intelligence Platform
│
├── Gym Analyzer
├── Café Analyzer
├── Salon Analyzer
├── Clinic Analyzer
├── Restaurant Analyzer
├── Tuition Centre Analyzer
├── Grocery Analyzer
├── Cloud Kitchen Analyzer
└── Future Business Categories
```

The long-term product is:

> A category-specific location intelligence platform for entrepreneurs, consultants, franchise owners, and small businesses across India.

The competitive advantage will come from:

- India-specific data
- Category-specific scoring
- Transparent calculations
- Historical location records
- Local-language support
- Better market-gap detection
- Practical financial models
- Clear evidence and confidence labels
- Useful reports that lead to action

---

# Immediate Next Steps

1. Select the first three business categories.
2. Select the first city.
3. Interview at least 20 potential users.
4. Produce five reports manually.
5. Validate willingness to pay.
6. Finalize the category configuration schema.
7. Build the analysis intake workflow.
8. Build the competitor collector.
9. Build the scoring and finance engines.
10. Launch a controlled paid pilot.

---

## Final Recommendation

Do not begin by building every feature, city, and business category.

Build the shared platform architecture first, launch with three categories in one city, validate customer demand, improve the scoring models, and then expand category by category and city by city.
