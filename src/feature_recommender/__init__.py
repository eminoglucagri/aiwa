"""Feature recommendation and differentiation engine."""
from __future__ import annotations

import sys
from pathlib import Path

# Add project root so the sibling feature_recommender package is importable
_ROOT = Path(__file__).resolve().parents[2]
if _ROOT.as_posix() not in sys.path:
    sys.path.insert(0, _ROOT.as_posix())

from feature_recommender.engine import FeatureRecommender as _Engine
from feature_recommender.schemas.recommendations import (
    FeatureCategory,
    FeaturePriority,
    FeatureRecommendation,
    FeatureRecommendationsReport,
)
from market_research import MarketAnalysisReport

__all__ = [
    "FeatureRecommender",
    "FeatureRecommendationsReport",
    "FeatureRecommendation",
    "FeaturePriority",
    "FeatureCategory",
]


class FeatureRecommender:
    """Feature recommendation engine that uses market research data."""

    def __init__(self):
        self._engine = _Engine()

    def recommend(
        self,
        market_report: MarketAnalysisReport | dict,
        app_idea: str | None = None,
        app_category: str = "saas",
    ) -> FeatureRecommendationsReport:
        report_dict = market_report.to_dict() if isinstance(market_report, MarketAnalysisReport) else market_report
        return self._engine.recommend(market_report=report_dict, app_idea=app_idea, app_category=app_category)

    def generate(
        self,
        app_idea: str,
        market_report: MarketAnalysisReport | None = None,
        app_category: str = "saas",
    ) -> FeatureRecommendationsReport:
        report_dict = market_report.to_dict() if market_report else {"app_idea": app_idea}
        return self._engine.recommend(market_report=report_dict, app_idea=app_idea, app_category=app_category)
