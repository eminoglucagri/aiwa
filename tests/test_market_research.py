"""Tests for market research module."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from market_research.report import (
    MarketAnalysisReport,
    CompetitorProfile,
    MarketSizing,
    Trend,
    PositioningAnalysis,
)


def test_competitor_profile_fields():
    c = CompetitorProfile(name="TestCorp", website="https://testcorp.com")
    assert c.name == "TestCorp"
    assert c.website == "https://testcorp.com"
    assert c.pricing == ""
    assert c.key_features == []


def test_market_sizing_default():
    ms = MarketSizing()
    assert ms.tam == ""
    assert ms.sam == ""
    assert ms.som == ""


def test_trend_fields():
    t = Trend(title="AI Integration", description="AI-powered features", relevance="high")
    assert t.title == "AI Integration"
    assert t.relevance == "high"


def test_positioning_analysis_default():
    pa = PositioningAnalysis()
    assert pa.opportunities == []
    assert pa.gaps == []
    assert pa.swot == {}


def test_market_analysis_report_to_dict():
    report = MarketAnalysisReport(
        app_idea="SaaS app",
        target_market="SMB",
        competitors=[
            CompetitorProfile(
                name="CompetitorA",
                website="https://compA.com",
                pricing="$99/mo",
                key_features=["Feature1", "Feature2"],
            )
        ],
        market_sizing=MarketSizing(tam="$10B", sam="$1B", som="$100M"),
        trends=[Trend(title="No-code", description="Low-code trend", relevance="high")],
        positioning=PositioningAnalysis(opportunities=["Mobile-first"], gaps=["Offline support"]),
    )

    d = report.to_dict()
    assert d["app_idea"] == "SaaS app"
    assert d["target_market"] == "SMB"
    assert len(d["competitors"]) == 1
    assert d["competitors"][0]["name"] == "CompetitorA"
    assert d["market_sizing"]["tam"] == "$10B"
    assert len(d["trends"]) == 1


def test_market_analysis_report_to_markdown():
    report = MarketAnalysisReport(
        app_idea="TestApp",
        target_market="Enterprise",
    )
    md = report.to_markdown()
    assert "TestApp" in md
    assert "Enterprise" in md
    assert "# Market Analysis Report" in md


def test_market_analysis_report_executive_summary():
    report = MarketAnalysisReport(
        app_idea="App1",
        target_market="Market1",
        competitors=[
            CompetitorProfile(name="C1", website="https://c1.com"),
            CompetitorProfile(name="C2", website="https://c2.com"),
        ],
        market_sizing=MarketSizing(tam="$5B"),
        trends=[Trend(title="T1", description="D1")],
        positioning=PositioningAnalysis(recommendation="Go mobile-first"),
    )
    summary = report._executive_summary()
    assert "2 competitor" in summary
    assert "$5B" in summary
    assert "1 relevant trend" in summary
    assert "Go mobile-first" in summary