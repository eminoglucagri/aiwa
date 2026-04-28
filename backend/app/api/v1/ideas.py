from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db
from ...db.models import Idea
from ...schemas.ideas import (
    IdeaCreate,
    IdeaSubmitResponse,
    IdeaResponse,
    IdeaListResponse,
    IdeaListItem,
    AnalysisReport,
)
from ...core.security import get_current_user

router = APIRouter(prefix="/ideas", tags=["ideas"])


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def submit_idea(
    idea_data: IdeaCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IdeaSubmitResponse:
    now = datetime.now(timezone.utc)
    idea = Idea(
        user_id=current_user["sub"],
        title=idea_data.title,
        description=idea_data.description,
        constraints=idea_data.constraints.model_dump() if idea_data.constraints else {},
        preferences=idea_data.preferences.model_dump() if idea_data.preferences else {},
        status="analyzing",
        created_at=now,
    )
    db.add(idea)
    await db.commit()
    await db.refresh(idea)

    return IdeaSubmitResponse(
        idea_id=str(idea.id),
        status="analyzing",
        submitted_at=now,
        estimated_completion_seconds=120,
    )


@router.get("/{idea_id}")
async def get_idea(
    idea_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IdeaResponse:
    result = await db.execute(
        select(Idea).where(Idea.id == idea_id, Idea.user_id == current_user["sub"])
    )
    idea = result.scalar_one_or_none()

    if not idea:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found")

    analysis = None
    if idea.analysis:
        analysis = AnalysisReport(**idea.analysis)

    return IdeaResponse(
        idea_id=str(idea.id),
        title=idea.title,
        description=idea.description,
        status=idea.status,
        submitted_at=idea.created_at,
        completed_at=idea.completed_at,
        analysis=analysis,
    )


@router.get("")
async def list_ideas(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> IdeaListResponse:
    query = select(Idea).where(Idea.user_id == current_user["sub"])
    count_query = select(func.count()).select_from(Idea).where(Idea.user_id == current_user["sub"])

    if status_filter:
        query = query.where(Idea.status == status_filter)
        count_query = count_query.where(Idea.status == status_filter)

    query = query.order_by(Idea.created_at.desc()).offset(offset).limit(limit)

    result = await db.execute(query)
    ideas = result.scalars().all()

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    return IdeaListResponse(
        ideas=[
            IdeaListItem(
                idea_id=str(i.id),
                title=i.title,
                status=i.status,
                submitted_at=i.created_at,
                completed_at=i.completed_at,
            )
            for i in ideas
        ],
        total=total,
        limit=limit,
        offset=offset,
    )