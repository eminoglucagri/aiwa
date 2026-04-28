from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class CompetitorProfile:
    name: str
    website: str
    pricing: str = ""
    key_features: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    market_position: str = ""
    estimated_users: str = ""


@dataclass
class MarketSizing:
    tam: str = ""
    sam: str = ""
    som: str = ""
    growth_rate: str = ""
    source: str = ""


@dataclass
class Trend:
    title: str
    description: str
    relevance: str = "medium"
    source: str = ""


@dataclass
class PositioningAnalysis:
    opportunities: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    swot: dict[str, list[str]] = field(default_factory=dict)
    recommendation: str = ""


@dataclass
class MarketAnalysisReport:
    app_idea: str
    target_market: str
    generated_at: datetime = field(default_factory=datetime.utcnow)
    competitors: list[CompetitorProfile] = field(default_factory=list)
    market_sizing: MarketSizing = field(default_factory=MarketSizing)
    trends: list[Trend] = field(default_factory=list)
    positioning: PositioningAnalysis = field(default_factory=PositioningAnalysis)
    sources: list[str] = field(default_factory=list)
    warning: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "app_idea": self.app_idea,
            "target_market": self.target_market,
            "generated_at": self.generated_at.isoformat(),
            "competitors": [
                {
                    "name": c.name,
                    "website": c.website,
                    "pricing": c.pricing,
                    "key_features": c.key_features,
                    "strengths": c.strengths,
                    "weaknesses": c.weaknesses,
                    "market_position": c.market_position,
                    "estimated_users": c.estimated_users,
                }
                for c in self.competitors
            ],
            "market_sizing": {
                "tam": self.market_sizing.tam,
                "sam": self.market_sizing.sam,
                "som": self.market_sizing.som,
                "growth_rate": self.market_sizing.growth_rate,
                "source": self.market_sizing.source,
            },
            "trends": [
                {
                    "title": t.title,
                    "description": t.description,
                    "relevance": t.relevance,
                    "source": t.source,
                }
                for t in self.trends
            ],
            "positioning": {
                "opportunities": self.positioning.opportunities,
                "gaps": self.positioning.gaps,
                "swot": self.positioning.swot,
                "recommendation": self.positioning.recommendation,
            },
            "sources": self.sources,
            "warning": self.warning,
            "error": self.error,
        }

    def to_markdown(self) -> str:
        lines = [
            "# Market Analysis Report",
            "",
            f"**App Idea:** {self.app_idea}",
            f"**Target Market:** {self.target_market}",
            f"**Generated:** {self.generated_at.strftime('%Y-%m-%d %H:%M UTC')}",
            "",
        ]

        if self.warning:
            lines.extend(["> **Warning:** " + self.warning, ""])
        if self.error:
            lines.extend(["> **Error:** " + self.error, ""])

        lines.extend([
            "## Executive Summary",
            self._executive_summary(),
            "",
            "## Competitor Landscape",
        ])

        if self.competitors:
            lines.append("| Competitor | Pricing | Key Features | Strengths | Weaknesses |")
            lines.append("|---|---|---|---|---|")
            for c in self.competitors:
                features = ", ".join(c.key_features) if c.key_features else "—"
                strengths = ", ".join(c.strengths) if c.strengths else "—"
                weaknesses = ", ".join(c.weaknesses) if c.weaknesses else "—"
                lines.append(
                    f"| [{c.name}]({c.website}) | {c.pricing or '—'} | {features} | {strengths} | {weaknesses} |"
                )
        else:
            lines.append("No competitors identified.")

        lines.extend(["", "## Market Sizing"])
        ms = self.market_sizing
        if ms.tam:
            lines.append(f"- **TAM:** {ms.tam}")
        if ms.sam:
            lines.append(f"- **SAM:** {ms.sam}")
        if ms.som:
            lines.append(f"- **SOM:** {ms.som}")
        if ms.growth_rate:
            lines.append(f"- **Growth Rate:** {ms.growth_rate}")
        if ms.source:
            lines.append(f"- **Source:** [{ms.source}]({ms.source})")
        if not ms.tam:
            lines.append("Market sizing data unavailable.")

        lines.extend(["", "## Market Trends"])
        if self.trends:
            for t in self.trends:
                badge = f"[{t.relevance.upper()}]" if t.relevance else ""
                lines.append(f"- **{t.title}** {badge}")
                lines.append(f"  {t.description}")
                if t.source:
                    lines.append(f"  Source: [{t.source}]({t.source})")
        else:
            lines.append("No trends identified.")

        pa = self.positioning
        lines.extend(["", "## Positioning Opportunities"])
        if pa.opportunities:
            lines.append("### Opportunities")
            for o in pa.opportunities:
                lines.append(f"- {o}")
        if pa.gaps:
            lines.append("### Gaps")
            for g in pa.gaps:
                lines.append(f"- {g}")
        if pa.swot:
            lines.append("### SWOT Analysis")
            for quadrant, items in pa.swot.items():
                if items:
                    lines.append(f"**{quadrant.title()}:** {', '.join(items)}")
        if pa.recommendation:
            lines.extend(["", "## Recommendation", pa.recommendation])

        if self.sources:
            lines.extend(["", "## Sources"])
            for s in self.sources:
                lines.append(f"- [{s}]({s})")

        return "\n".join(lines)

    def _executive_summary(self) -> str:
        competitor_count = len(self.competitors)
        ms = self.market_sizing
        sizing_text = f"TAM of {ms.tam}" if ms.tam else "undetermined market size"
        trend_count = len(self.trends)
        rec = self.positioning.recommendation
        if rec:
            return f"Analysis of {self.target_market} for the app idea \"{self.app_idea}\" identified {competitor_count} competitor(s) with a {sizing_text}. {trend_count} relevant trend(s) were found. {rec}"
        return f"Analysis of {self.target_market} for the app idea \"{self.app_idea}\" identified {competitor_count} competitor(s) with a {sizing_text}. {trend_count} relevant trend(s) were found."
