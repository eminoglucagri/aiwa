# Feature Recommendation & Differentiation Engine — AIWA-16

**Document:** AIWA Feature Recommender v1.0
**Date:** 2026-04-28
**Status:** Implemented
**Issue:** AIWA-16

---

## 1. Overview

Given market research output (competitors, trends, gaps) and an app idea, the engine generates structured feature recommendations in four priority tiers:

1. **Must-have** — features the market expects (>60% of competitors offer)
2. **Nice-to-have** — features that add polish but aren't deal-breakers
3. **Differentiators** — features that address competitor gaps and market opportunities
4. **Optional** — stretch goals driven by emerging trends

Output is a `FeatureRecommendationSet` with rationale, effort estimates, and impact scores.

---

## 2. Module Interface

```python
from market_research import MarketResearcher, MarketAnalysisReport
from feature_recommender import FeatureRecommender

# Option A: with market research data
report: MarketAnalysisReport = await MarketResearcher().analyze(
    app_idea="AI-powered appointment scheduling",
    target_market="small healthcare clinics in the US",
)
recommender = FeatureRecommender(market_report=report)
recommendations = recommender.generate(app_idea="AI-powered appointment scheduling")

# Option B: without market data (generic recommendations)
recommender = FeatureRecommender(market_report=None)
recommendations = recommender.generate(app_idea="SaaS project management tool")
```

---

## 3. Output Schema

### FeatureRecommendationSet

| Field | Type | Description |
|---|---|---|
| `app_idea` | `str` | Application concept |
| `generated_at` | `datetime` | Timestamp |
| `must_have` | `list[FeatureRecommendation]` | Core features |
| `nice_to_have` | `list[FeatureRecommendation]` | Polish features |
| `differentiators` | `list[FeatureRecommendation]` | Differentiation features |
| `optional` | `list[FeatureRecommendation]` | Stretch features |
| `prioritization_notes` | `str` | Markdown guide |
| `warning` | `str | None` | Issues with input data |

### FeatureRecommendation

| Field | Type | Description |
|---|---|---|
| `name` | `str` | Feature name |
| `priority` | `FeaturePriority` | MUST_HAVE / NICE_TO_HAVE / DIFFERENTIATOR / OPTIONAL |
| `rationale` | `str` | Why this feature matters |
| `source` | `str` | Competitor / trend / gap this came from |
| `estimated_effort` | `str` | low / medium / high |
| `impact_score` | `int` | 1–10 scale |

---

## 4. Scoring Logic

### Must-have (Impact 8–9, Effort: medium)

Features that ≥60% of competitors offer are must-haves — users expect them and will churn without them. The engine also adds platform-standard must-haves (auth, data persistence, responsive design) regardless of market data.

### Nice-to-have (Impact 5, Effort: low)

Features that 30–60% of competitors offer. Adds polish without being table stakes. Trend-driven features with high relevance also qualify here (effort: high, impact: 7) since they're not yet market-standard.

### Differentiators (Impact 8–10, Effort: medium–high)

Features derived from:
- Competitor gaps (weaknesses in competitor analysis)
- Market opportunities (pricing white space, underserved verticals)
- Platform AI-automation strategy as default differentiator

### Optional (Impact 3, Effort: medium)

Medium-relevance trend items and stretch goals for post-v1.0 releases.

---

## 5. Prioritization Guide

Generated automatically in `prioritization_notes`:

1. **MVP**: Must-have features only — gets to a trusted, usable product
2. **v1.0**: Must-have + Differentiators — competitive, differentiated product
3. **Post-v1.0**: Nice-to-have based on user feedback
4. **Future**: Optional features from emerging trends

---

## 6. Integration with Pipeline

```
POST /projects/{id}/ideate
  → MarketResearcher.analyze(app_idea, target_market) → MarketAnalysisReport
  → FeatureRecommender(market_report=report).generate(app_idea) → FeatureRecommendationSet
  → Store both in DB
  → Return to Web UI
  → Downstream: BackendAPIGenerator uses FeatureRecommendationSet to build endpoints
```

---

## 7. Dependencies

- `market_research` module (optional — engine works with `market_report=None` for generic recommendations)
- No external APIs required
