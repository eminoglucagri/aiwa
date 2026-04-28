from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class Constraints(BaseModel):
    deadline: Optional[str] = None
    budget_tier: Optional[str] = Field(None, pattern="^(free|starter|pro|enterprise)$")
    team_size: Optional[int] = Field(None, ge=1, le=100)
    must_haves: Optional[List[str]] = None
    nice_to_haves: Optional[List[str]] = None


class Preferences(BaseModel):
    tech_stack: Optional[List[str]] = None
    deployment_target: Optional[str] = Field(None, pattern="^(vercel|cloudflare|railway|self_hosted)$")
    style: Optional[str] = Field(None, pattern="^(minimal|modern|playful|corporate)$")


class IdeaCreate(BaseModel):
    title: str = Field(..., max_length=120)
    description: str = Field(..., max_length=10000)
    constraints: Optional[Constraints] = None
    preferences: Optional[Preferences] = None


class IdeaSubmitResponse(BaseModel):
    idea_id: str
    status: str = "analyzing"
    submitted_at: datetime
    estimated_completion_seconds: int = 120


class EstimatedEffort(BaseModel):
    min: int
    max: int
    confidence: str = Field(..., pattern="^(low|medium|high)$")


class TechFeasibility(BaseModel):
    verdict: str = Field(..., pattern="^(feasible|risky|not_feasible)$")
    challenges: List[str] = []
    suggestions: List[str] = []


class RecommendedStack(BaseModel):
    frontend: str
    backend: Optional[str] = None
    database: Optional[str] = None
    deployment: str


class FeatureBreakdownItem(BaseModel):
    feature: str
    estimated_hours: int
    priority: str = Field(..., pattern="^(must|should|could)$")


class RiskItem(BaseModel):
    description: str
    severity: str = Field(..., pattern="^(low|medium|high)$")
    mitigation: str


class AnalysisReport(BaseModel):
    scope_score: str = Field(..., pattern="^(small|medium|large|xlarge)$")
    complexity_score: str = Field(..., pattern="^(simple|moderate|complex|very_complex)$")
    tech_feasibility: TechFeasibility
    estimated_effort_hours: EstimatedEffort
    recommended_stack: RecommendedStack
    feature_breakdown: List[FeatureBreakdownItem] = []
    risks: List[RiskItem] = []
    summary: str


class IdeaResponse(BaseModel):
    idea_id: str
    title: str
    description: str
    status: str
    submitted_at: datetime
    completed_at: Optional[datetime] = None
    analysis: Optional[AnalysisReport] = None


class IdeaListItem(BaseModel):
    idea_id: str
    title: str
    status: str
    submitted_at: datetime
    completed_at: Optional[datetime] = None


class IdeaListResponse(BaseModel):
    ideas: List[IdeaListItem]
    total: int
    limit: int
    offset: int