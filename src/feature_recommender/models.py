"""Output schemas re-exported from sibling feature_recommender package."""
from __future__ import annotations

from feature_recommender.schemas.recommendations import (
    FeatureCategory,
    FeaturePriority,
    FeatureRecommendation,
    FeatureRecommendationsReport,
)

__all__ = ["FeatureCategory", "FeaturePriority", "FeatureRecommendation", "FeatureRecommendationsReport"]
