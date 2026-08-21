from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sprint_model import Sprint, SprintStatus
from app.repositories.base_repository import BaseRepository
from app.schemas.sprint_schema import SprintCreate


class SprintRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_id(self, sprint_id: UUID) -> Sprint | None:
        return await self.session.scalar(
            select(Sprint).where(Sprint.id == sprint_id)
        )

    async def get_by_project_and_name(
        self, project_id: UUID, name: str
    ) -> Sprint | None:
        return await self.session.scalar(
            select(Sprint).where(
                Sprint.project_id == project_id,
                Sprint.name == name,
            )
        )

    async def get_active_by_project(self, project_id: UUID) -> Sprint | None:
        return await self.session.scalar(
            select(Sprint).where(
                Sprint.project_id == project_id,
                Sprint.status == SprintStatus.ACTIVE.value,
            )
        )

    async def list(self, project_id: UUID | None = None) -> list[Sprint]:
        stmt = select(Sprint).order_by(Sprint.start_date.desc(), Sprint.created_at.desc())
        if project_id:
            stmt = stmt.where(Sprint.project_id == project_id)
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def create(self, payload: SprintCreate, user_id: UUID) -> Sprint:
        sprint = Sprint(
            project_id=payload.project_id,
            name=payload.name,
            goal=payload.goal,
            start_date=payload.start_date,
            end_date=payload.end_date,
            status=SprintStatus.PLANNED.value,
            created_by=user_id,
            updated_by=user_id,
        )
        self.session.add(sprint)
        await self.session.flush()
        await self.session.refresh(sprint)
        return sprint

    async def update(self, sprint: Sprint, user_id: UUID, **kwargs) -> Sprint:
        for key, value in kwargs.items():
            if value is not None and hasattr(sprint, key):
                setattr(sprint, key, value)
        sprint.updated_by = user_id
        await self.session.flush()
        await self.session.refresh(sprint)
        return sprint
