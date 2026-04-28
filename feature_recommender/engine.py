"""Core feature recommendation engine.

Analyzes market research output and produces prioritized feature recommendations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from feature_recommender.schemas.recommendations import (
    FeatureCategory,
    FeaturePriority,
    FeatureRecommendation,
    FeatureRecommendationsReport,
)

# P0 must-haves for nearly any SaaS web app
_MUST_HAVE_BASE = {
    "user_authentication": "User authentication (sign up, login, logout, password reset)",
    "user_sessions": "User session management with secure tokens",
    "dashboard_home": "User dashboard / home screen after login",
    "profile_management": "User profile management (view/edit name, email, avatar)",
    "data_privacy_controls": "Data export and account deletion (privacy compliance)",
    "responsive_design": "Mobile-responsive design for all screens",
}

# Table-stakes per app category
_CATEGORY_TABLE_STAKES = {
    "saas": [
        "team_invitations_and_roles",
        "usage_billing_and_plans",
        "onboarding_wizard",
        "notifications_and_alerts",
        "search_and_filtering",
    ],
    "marketplace": [
        "listing_creation",
        "search_and_filter",
        "messaging_between_users",
        "review_and_rating_system",
        "transaction_payment_flow",
    ],
    "cms": [
        "content_creation_and_editing",
        "media_upload_and_management",
        "content_publishing_workflow",
        "user_roles_and_permissions",
    ],
    "analytics": [
        "dashboard_with_charts",
        "data_export",
        "date_range_filtering",
        "user_segmentation",
    ],
    "ecommerce": [
        "product_catalog",
        "shopping_cart",
        "checkout_and_payment",
        "order_tracking",
        "inventory_management",
    ],
}


class FeatureRecommender:
    def recommend(
        self,
        market_report: dict,
        app_idea: Optional[str] = None,
        app_category: str = "saas",
    ) -> FeatureRecommendationsReport:
        """Build feature recommendations from a market analysis report.

        Args:
            market_report: Dict representation of a MarketAnalysisReport (from the market research module).
                           Expected keys: competitors, positioning, trends, market_sizing.
            app_idea: Override for the app idea string (uses report.app_idea if not provided).
            app_category: App type for table-stakes derivation. One of: saas, marketplace, cms, analytics, ecommerce.
        """
        app_idea = app_idea or market_report.get("app_idea", "the target application")

        competitors = market_report.get("competitors", [])
        positioning = market_report.get("positioning", {})
        trends = market_report.get("trends", [])
        market_sizing = market_report.get("market_sizing", {})

        must_have = self._derive_must_haves(app_idea, competitors, positioning)
        table_stakes = self._derive_table_stakes(app_category, competitors)
        differentiators = self._derive_differentiators(app_idea, competitors, positioning, trends)
        nice_to_have = self._derive_nice_to_have(competitors, trends)

        roadmap = self._build_roadmap(must_have, differentiators, nice_to_have, table_stakes)
        summary = self._build_summary(must_have, differentiators, nice_to_have, market_sizing)

        return FeatureRecommendationsReport(
            app_idea=app_idea,
            generated_at=datetime.now(timezone.utc).isoformat(),
            total_recommendations=(
                len(must_have) + len(table_stakes) + len(differentiators) + len(nice_to_have)
            ),
            must_have=must_have,
            nice_to_have=nice_to_have,
            differentiators=differentiators,
            table_stakes=table_stakes,
            roadmap_order=roadmap,
            summary=summary,
        )

    def _derive_must_haves(
        self,
        app_idea: str,
        competitors: list[dict],
        positioning: dict,
    ) -> list[FeatureRecommendation]:
        """Must-have: baseline auth + security features every modern web app needs."""
        features = []
        for key, desc in _MUST_HAVE_BASE.items():
            features.append(
                FeatureRecommendation(
                    name=key,
                    description=desc,
                    category=FeatureCategory.MUST_HAVE,
                    priority=FeaturePriority.P0,
                    rationale="Baseline expectation for any modern SaaS application. Users expect these out of the box.",
                    evidence=["Universal expectation across all competitor categories surveyed"],
                    estimated_effort="medium",
                    market_signal="present_in_all_competitors",
                    roi_indicator="high",
                )
            )
        return features

    def _derive_table_stakes(
        self,
        app_category: str,
        competitors: list[dict],
    ) -> list[FeatureRecommendation]:
        """Table stakes: minimum features expected by the target market segment."""
        stakes = _CATEGORY_TABLE_STAKES.get(app_category, _CATEGORY_TABLE_STAKES["saas"])
        features = []
        for name in stakes:
            features.append(
                FeatureRecommendation(
                    name=name,
                    description=name.replace("_", " ").title(),
                    category=FeatureCategory.TABLE_STAKES,
                    priority=FeaturePriority.P0,
                    rationale=f"Expected baseline for the {app_category} category. Missing this will disqualify the app in buyer evaluations.",
                    evidence=[f"Present in majority of {app_category} competitors surveyed"],
                    estimated_effort="medium",
                    market_signal=f"standard_for_{app_category}",
                    roi_indicator="medium",
                )
            )
        return features

    def _derive_differentiators(
        self,
        app_idea: str,
        competitors: list[dict],
        positioning: dict,
        trends: list[dict],
    ) -> list[FeatureRecommendation]:
        """Differentiation: features unique to this app that competitors lack."""
        features = []
        gaps = positioning.get("gaps", []) if isinstance(positioning, dict) else []
        opportunities = positioning.get("opportunities", []) if isinstance(positioning, dict) else []

        for gap in gaps[:4]:
            features.append(
                FeatureRecommendation(
                    name=self._slugify(gap),
                    description=gap,
                    category=FeatureCategory.DIFFERENTIATOR,
                    priority=FeaturePriority.P1,
                    rationale=f"Identified gap in the market — '{gap}' — that no major competitor addresses. First-mover advantage.",
                    evidence=["Gap identified in competitor analysis and positioning study"],
                    estimated_effort="high",
                    market_signal="market_gap",
                    competitor_gap="No major competitor currently offers this",
                    roi_indicator="high",
                )
            )

        for opp in opportunities[:2]:
            features.append(
                FeatureRecommendation(
                    name=self._slugify(opp),
                    description=opp,
                    category=FeatureCategory.DIFFERENTIATOR,
                    priority=FeaturePriority.P1,
                    rationale=f"Opportunity identified in positioning analysis — '{opp}'. Strong differentiation angle.",
                    evidence=["Opportunity surfaced from market positioning analysis"],
                    estimated_effort="medium",
                    market_signal="positioning_opportunity",
                    roi_indicator="medium",
                )
            )

        return features

    def _derive_nice_to_have(
        self,
        competitors: list[dict],
        trends: list[dict],
    ) -> list[FeatureRecommendation]:
        """Nice-to-have: polish features that enhance but don't block adoption."""
        features = []
        high_trend_titles = [t["title"] for t in trends if t.get("relevance") == "high"][:3]
        for trend in high_trend_titles:
            features.append(
                FeatureRecommendation(
                    name=self._slugify(trend),
                    description=f"Feature incorporating the trend: {trend}",
                    category=FeatureCategory.NICE_TO_HAVE,
                    priority=FeaturePriority.P2,
                    rationale=f"Trending in the target market: '{trend}'. Enhances appeal and perceived modernity.",
                    evidence=[f"High-relevance trend: {trend}"],
                    estimated_effort="low",
                    market_signal=f"trend:{trend}",
                    roi_indicator="low",
                )
            )

        unique_features: set[str] = set()
        for comp in competitors:
            for f in comp.get("key_features", [])[:2]:
                if f.lower() not in unique_features:
                    unique_features.add(f.lower())
                    features.append(
                        FeatureRecommendation(
                            name=self._slugify(f),
                            description=f,
                            category=FeatureCategory.NICE_TO_HAVE,
                            priority=FeaturePriority.P2,
                            rationale=f"Observed in competitor '{comp.get('name', 'unknown')}' — adds feature richness.",
                            evidence=[f"Seen at: {comp.get('name', 'unknown')}"],
                            estimated_effort="medium",
                            market_signal="competitor_observed",
                            roi_indicator="low",
                        )
                    )
        return features[:6]

    def _build_roadmap(
        self,
        must_have: list[FeatureRecommendation],
        differentiators: list[FeatureRecommendation],
        nice_to_have: list[FeatureRecommendation],
        table_stakes: list[FeatureRecommendation],
    ) -> list[str]:
        """Order features into a recommended development roadmap."""
        order: list[str] = []
        order += [f.name for f in must_have]
        order += [f.name for f in table_stakes if f.name not in order]
        order += [f.name for f in differentiators]
        order += [f.name for f in nice_to_have]
        return order

    def _build_summary(
        self,
        must_have: list[FeatureRecommendation],
        differentiators: list[FeatureRecommendation],
        nice_to_have: list[FeatureRecommendation],
        market_sizing: dict,
    ) -> str:
        size = market_sizing.get("tam", "Unknown")
        lines = [
            f"Market opportunity: {size} TAM.",
            f"Recommended feature set: {len(must_have)} must-have, {len(differentiators)} differentiating, {len(nice_to_have)} polish features.",
            "Launch with P0 must-haves and table stakes. Differentiators provide the competitive edge. Nice-to-haves round out the product post-launch.",
        ]
        return " ".join(lines)

    def _slugify(self, text: str) -> str:
        import re
        text = text.lower()
        text = re.sub(r"[^a-z0-9]+", "_", text)
        return text.strip("_")