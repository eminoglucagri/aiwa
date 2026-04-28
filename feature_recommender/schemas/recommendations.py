"""Output schemas for feature recommendations."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class FeaturePriority(Enum):
    P0 = "P0"  # Must-have — launch blocker without these
    P1 = "P1"  # High — strong differentiation, high adoption
    P2 = "P2"  # Medium — nice-to-have, adds polish
    P3 = "P3"  # Low — future roadmap candidates


class FeatureCategory(Enum):
    MUST_HAVE = "must-have"  # Industry baseline; missing = disqualified
    NICE_TO_HAVE = "nice-to-have"  # Standard convenience features
    DIFFERENTIATOR = "differentiator"  # Unique advantages
    TABLE_STAKES = "table-stakes"  # Minimum expected by market


@dataclass
class FeatureRecommendation:
    name: str
    description: str
    category: FeatureCategory
    priority: FeaturePriority
    rationale: str
    evidence: list[str] = field(default_factory=list)  # competitor citations, market data
    estimated_effort: str = "medium"  # low / medium / high
    market_signal: str = ""  # what in the market data led to this recommendation
    competitor_gap: Optional[str] = None  # which competitor lacks this
    roi_indicator: str = "medium"  # low / medium / high

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "priority": self.priority.value,
            "rationale": self.rationale,
            "evidence": self.evidence,
            "estimated_effort": self.estimated_effort,
            "market_signal": self.market_signal,
            "competitor_gap": self.competitor_gap,
            "roi_indicator": self.roi_indicator,
        }


@dataclass
class FeatureRecommendationsReport:
    app_idea: str
    generated_at: str
    total_recommendations: int
    must_have: list[FeatureRecommendation] = field(default_factory=list)
    nice_to_have: list[FeatureRecommendation] = field(default_factory=list)
    differentiators: list[FeatureRecommendation] = field(default_factory=list)
    table_stakes: list[FeatureRecommendation] = field(default_factory=list)
    roadmap_order: list[str] = field(default_factory=list)  # ordered list of feature names
    summary: str = ""

    def to_dict(self) -> dict:
        return {
            "app_idea": self.app_idea,
            "generated_at": self.generated_at,
            "total_recommendations": self.total_recommendations,
            "must_have": [f.to_dict() for f in self.must_have],
            "nice_to_have": [f.to_dict() for f in self.nice_to_have],
            "differentiators": [f.to_dict() for f in self.differentiators],
            "table_stakes": [f.to_dict() for f in self.table_stakes],
            "roadmap_order": self.roadmap_order,
            "summary": self.summary,
        }

    def to_markdown(self) -> str:
        lines = [
            "# Feature Recommendation Report",
            f"**App Idea:** {self.app_idea}",
            f"**Generated:** {self.generated_at}",
            f"**Total Recommendations:** {self.total_recommendations}",
            "",
        ]
        if self.summary:
            lines += [f"## Summary\n{self.summary}\n"]

        for features, label in [
            (self.must_have, "## Must-Have (P0 — Launch Blockers)"),
            (self.differentiators, "## Differentiators (P1 — Competitive Edge)"),
            (self.nice_to_have, "## Nice-to-Have (P2 — Polish)"),
            (self.table_stakes, "## Table Stakes (Minimum Market Expectations)"),
        ]:
            if not features:
                continue
            lines.append(f"\n{label}\n")
            for f in features:
                lines.append(
                    f"- **{f.name}** [{f.category.value}, {f.priority.value}] — {f.rationale}"
                )
                if f.competitor_gap:
                    lines.append(f"  - Gap: {f.competitor_gap}")
                if f.evidence:
                    lines.append(f"  - Evidence: {', '.join(f.evidence)}")

        lines.append("\n## Recommended Roadmap Order\n")
        for i, name in enumerate(self.roadmap_order, 1):
            lines.append(f"{i}. {name}")

        return "\n".join(lines)