import pytest
from pydantic import ValidationError
from app.schemas.ideas import (
    IdeaCreate,
    IdeaSubmitResponse,
    EstimatedEffort,
    TechFeasibility,
    AnalysisReport,
    RecommendedStack,
)


def test_idea_create_valid():
    idea = IdeaCreate(
        title="My App",
        description="A web app that does things",
    )
    assert idea.title == "My App"
    assert idea.description == "A web app that does things"


def test_idea_create_title_max_length():
    with pytest.raises(ValidationError):
        IdeaCreate(title="x" * 121, description="desc")


def test_idea_create_description_max_length():
    with pytest.raises(ValidationError):
        IdeaCreate(title="title", description="x" * 10001)


def test_estimated_effort_valid():
    effort = EstimatedEffort(min=10, max=20, confidence="medium")
    assert effort.min == 10
    assert effort.max == 20
    assert effort.confidence == "medium"


def test_estimated_effort_invalid_confidence():
    with pytest.raises(ValidationError):
        EstimatedEffort(min=10, max=20, confidence="very_high")


def test_tech_feasibility_valid():
    tf = TechFeasibility(
        verdict="feasible",
        challenges=["challenge1"],
        suggestions=["suggestion1"],
    )
    assert tf.verdict == "feasible"


def test_analysis_report_full():
    tf = TechFeasibility(verdict="feasible", challenges=[], suggestions=[])
    effort = EstimatedEffort(min=5, max=10, confidence="high")
    stack = RecommendedStack(
        frontend="React",
        backend=None,
        database="NeonDB",
        deployment="Vercel",
    )
    report = AnalysisReport(
        scope_score="medium",
        complexity_score="moderate",
        tech_feasibility=tf,
        estimated_effort_hours=effort,
        recommended_stack=stack,
        feature_breakdown=[],
        risks=[],
        summary="Test summary.",
    )
    assert report.scope_score == "medium"
    assert report.summary == "Test summary."