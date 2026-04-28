# Market Research Automation — AIWA-15

**Document:** AIWA Market Research Automation v1.0
**Date:** 2026-04-28
**Status:** Implementation in progress
**Issue:** AIWA-15

---

## 1. Overview

The market research automation module takes an **app idea** and **target market** as input and produces a structured market analysis report covering:

1. Competitor identification and feature comparison
2. Market sizing and trend analysis
3. Positioning opportunities and gaps

The module integrates with web search and public data sources to gather intelligence. Output is a structured report that feeds into the platform's idea-validation pipeline.

---

## 2. Module Interface

```python
from market_research import MarketResearcher

researcher = MarketResearcher()
report = await researcher.analyze(
    app_idea="AI-powered appointment scheduling for small clinics",
    target_market="small healthcare clinics in the US",
    regions=["US"],
)
```

### Output Schema (`MarketAnalysisReport`)

| Field | Type | Description |
|---|---|---|
| `app_idea` | `str` | Original app idea |
| `target_market` | `str` | Target market description |
| `generated_at` | `datetime` | Timestamp |
| `competitors` | `list[CompetitorProfile]` | Identified competitors |
| `market_sizing` | `MarketSizing` | TAM/SAM/SOM, growth rate |
| `trends` | `list[Trend]` | Relevant market trends |
| `positioning` | `PositioningAnalysis` | Opportunities and gaps |
| `sources` | `list[str]` | URLs/data sources cited |

### Sub-schemas

```python
@dataclass
class CompetitorProfile:
    name: str
    website: str
    pricing: str
    key_features: list[str]
    strengths: list[str]
    weaknesses: list[str]
    market_position: str
    estimated_users: str

@dataclass
class MarketSizing:
    tam: str   # Total Addressable Market
    sam: str   # Serviceable Available Market
    som: str   # Serviceable Obtainable Market
    growth_rate: str
    source: str

@dataclass
class Trend:
    title: str
    description: str
    relevance: str  # high/medium/low
    source: str

@dataclass
class PositioningAnalysis:
    opportunities: list[str]
    gaps: list[str]
    swot: dict[str, list[str]]  # strengths/weaknesses/opportunities/threats
    recommendation: str
```

---

## 3. Data Sources & Tools

| Data Need | Source | Method |
|---|---|---|
| Competitor identification | Web search (DuckDuckGo/Bing) | `requests` + search engine results |
| Competitor features | Company websites, Crunchbase, G2 | `requests` scraping public pages |
| Market sizing | Statista, Grand View Research, MarketsandMarkets | Public reports via web search |
| Market trends | Google Trends, industry publications | Web search + trend APIs |
| Pricing intelligence | G2, Capterra, competitor pricing pages | Web search + scraping |

---

## 4. Architecture

```
market_research/
├── __init__.py          — Package exports
├── researcher.py         — MarketResearcher orchestrator class
├── competitor.py         — Competitor identification & analysis
├── market_sizing.py      — TAM/SAM/SOM extraction
├── trends.py             — Trend detection
├── positioning.py        — Gap/opportunity analysis
├── web_search.py         — Web search abstraction layer
└── report.py             — Report generation and formatting
```

### 4.1 `MarketResearcher` Orchestrator

`analyze()` runs three sub-pipelines concurrently, then merges results into a `MarketAnalysisReport`.

### 4.2 Web Search Abstraction

Primary: `WebSearch` class wraps `requests` against DuckDuckGo HTML (no API key required).
Fallback: Bing Search API via `BING_API_KEY` env var.

### 4.3 Rate Limiting

- 1 request/second to avoid rate limits
- Exponential backoff on 429 responses (up to 3 retries)
- Results cached in Redis with 24h TTL per query hash

---

## 5. Competitor Analysis Pipeline

1. **Seed search**: Query search engine for `{app_idea} competitors` and `{target_market} software`
2. **Expand**: Extract company names from top 10 results, search each individually
3. **Profile**: For each competitor, search for pricing, key features, and market position
4. **Compare**: Build feature matrix from profiles

---

## 6. Market Sizing Pipeline

1. Search for `{target_market} market size 2024 2025`
2. Search for `{target_market} growth rate CAGR`
3. Extract figures — prefer Statista, Grand View Research, MarketsandMarkets
4. Derive TAM → SAM → SOM using platform-defined heuristics:
   - SAM = TAM × 0.40 (assuming 40% addressable by current product scope)
   - SOM = SAM × 0.10 (assuming 10% penetration in first 2 years)

---

## 7. Trend Analysis Pipeline

1. Search for `{target_market} trends 2025 2026`
2. Search for `{app_idea_category} industry news`
3. Query Google Trends for key terms
4. Classify relevance (high/medium/low) based on search result prominence

---

## 8. Positioning Pipeline

1. **Gaps**: Features/complaints identified in competitor weaknesses that the app idea addresses
2. **Opportunities**: Underserved segments, pricing white space, geographic gaps
3. **SWOT**: Derived from combined competitor + trend analysis
4. **Recommendation**: Summary sentence on market entry feasibility and differentiation angle

---

## 9. Report Output

The module produces two output formats:

1. **Structured dict** (machine-readable, stored in DB as JSONB)
2. **Markdown report** (human-readable, displayed in Web UI)

```markdown
# Market Analysis Report

## Executive Summary
[One-paragraph overview]

## Competitor Landscape
[Table of competitors with features, pricing, strengths, weaknesses]

## Market Sizing
- **TAM**: $X
- **SAM**: $Y
- **SOM**: $Z
- **Growth Rate**: ~X%/year
- **Source**: [link]

## Market Trends
[Bullet list of trends with relevance]

## Positioning Opportunities
### Opportunities
- ...

### Gaps
- ...

### SWOT Analysis
**Strengths**: ...
**Weaknesses**: ...
**Opportunities**: ...
**Threats**: ...

## Recommendation
[Feasibility assessment and differentiation angle]

## Sources
- [link 1]
- [link 2]
```

---

## 10. Integration with Control Plane

The module is instantiated by the Control Plane API and called within the project ideation pipeline:

```
POST /projects/{id}/ideate
  → MarketResearcher.analyze(app_idea, target_market)
  → Store MarketAnalysisReport in DB
  → Return report to Web UI
```

---

## 11. Dependencies

- `httpx` — async HTTP client for web requests
- `beautifulsoup4` — HTML parsing for competitor pages
- `markdown` — markdown report generation
- `redis` — result caching (optional)

No external paid APIs required for MVP. All data sourced from public web search and free-tier sources.

---

## 12. Error Handling

| Scenario | Behavior |
|---|---|
| Web search returns no results | Return partial report with `competitors: []` and `warning: "Limited data found"` |
| Rate limited (429) | Retry with backoff up to 3x, then fail gracefully |
| Target market too narrow | Warn and broaden search automatically |
| All sources fail | Return empty report with `error` field set |

---

## 13. Open Questions

| Question | Status | Notes |
|---|---|---|
| Google Search API vs. scraping | Open | Free tier is limited; DuckDuckGo scraping may be fragile |
| Market sizing accuracy | Open | TAM figures from public reports are estimates; note confidence level |
| Competitor data freshness | Open | Cache results for 7 days; flag data age in report |
| Integration with idea-to-code pipeline | Open | Decide whether this runs as standalone or inside agent worker |
