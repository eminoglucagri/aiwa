"""Tests for feature recommender module."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from feature_recommender.recommender import FeatureRecommender


def test_feature_recommender_init():
    fr = FeatureRecommender()
    assert fr is not None


def test_recommend_with_dict():
    fr = FeatureRecommender()
    report = {
        "app_idea": "SaaS app",
        "target_market": "SMB",
        "competitors": [],
        "market_sizing": {},
        "trends": [],
        "positioning": {},
        "sources": [],
    }
    result = fr.recommend(report, app_idea="SaaS app", app_category="saas")
    assert result is not None


def test_recommend_with_string_app_idea():
    fr = FeatureRecommender()
    report = {"app_idea": "Test app", "target_market": "Consumers"}
    result = fr.recommend(report, app_idea="Test app")
    assert result is not None


def test_generate_with_idea_only():
    fr = FeatureRecommender()
    result = fr.generate(app_idea="E-commerce platform")
    assert result is not None