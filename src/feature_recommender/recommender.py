"""Feature recommendation engine — wraps feature_recommender.engine with typed interface."""
from __future__ import annotations

from feature_recommender.engine import FeatureRecommender as _Engine
from feature_recommender.schemas.recommendations import (
    FeatureCategory,
    FeaturePriority,
    FeatureRecommendation,
    FeatureRecommendationsReport,
)
from market_research.models import MarketAnalysisReport

__all__ = [
    "FeatureRecommender",
    "FeatureRecommendationsReport",
    "FeatureRecommendation",
    "FeaturePriority",
    "FeatureCategory",
]


class FeatureRecommender:
    """Feature recommendation engine that uses market research data.

    Supports two usage modes:
    1. With MarketAnalysisReport object (recommended): full market-aware recommendations
    2. With dict (market_report as dict): compatibility mode for pipeline integration
    """

    def __init__(self):
        self._engine = _Engine()

    def recommend(
        self,
        market_report: MarketAnalysisReport | dict,
        app_idea: str | None = None,
        app_category: str = "saas",
    ) -> FeatureRecommendationsReport:
        """Generate prioritized feature recommendations.

        Args:
            market_report: MarketAnalysisReport object or dict from the market research module.
            app_idea: Override app idea string.
            app_category: App type for table-stakes derivation (saas, marketplace, cms, analytics, ecommerce).
        """
        if isinstance(market_report, MarketAnalysisReport):
            report_dict = market_report.to_dict()
        else:
            report_dict = market_report

        return self._engine.recommend(
            market_report=report_dict,
            app_idea=app_idea,
            app_category=app_category,
        )

    def generate(
        self,
        app_idea: str,
        market_report: MarketAnalysisReport | None = None,
        app_category: str = "saas",
    ) -> FeatureRecommendationsReport:
        """Generate recommendations with optional market data.

        Args:
            app_idea: The application concept.
            market_report: Optional MarketAnalysisReport for market-aware recommendations.
            app_category: App type for table-stakes derivation.
        """
        report_dict = market_report.to_dict() if market_report else {"app_idea": app_idea}
        return self._engine.recommend(
            market_report=report_dict,
            app_idea=app_idea,
            app_category=app_category,
        )
