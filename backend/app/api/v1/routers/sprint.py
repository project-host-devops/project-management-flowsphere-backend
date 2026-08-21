from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth_dependencies import get_current_user
from app.db.session import get_db
from app.schemas.sprint_schema import SprintCreate, SprintResponse, SprintUpdate
from app.services.sprint_service import SprintService

router = APIRouter(prefix="/sprints", tags=["Sprints"])


@router.post("/", response_model=SprintResponse, status_code=status.HTTP_201_CREATED)
async def create_sprint(
    payload: SprintCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = SprintService(db)
    return await service.create(payload, current_user.id)


@router.get("/", response_model=list[SprintResponse])
async def get_sprints(
    project_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = SprintService(db)
    return await service.list(project_id)


@router.get("/{sprint_id}", response_model=SprintResponse)
async def get_sprint(
    sprint_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await SprintService(db).get(sprint_id)


@router.put("/{sprint_id}", response_model=SprintResponse)
async def update_sprint(
    sprint_id: UUID,
    payload: SprintUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await SprintService(db).update(sprint_id, payload, current_user.id)


@router.post("/{sprint_id}/start", response_model=SprintResponse)
async def start_sprint(
    sprint_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await SprintService(db).start(sprint_id, current_user.id)


@router.post("/{sprint_id}/close", response_model=SprintResponse)
async def close_sprint(
    sprint_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await SprintService(db).close(sprint_id, current_user.id)
