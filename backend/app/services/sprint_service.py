from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_model import Project
from app.models.sprint_model import Sprint, SprintStatus
from app.repositories.sprint_repository import SprintRepository
from app.schemas.sprint_schema import SprintCreate, SprintUpdate


class SprintService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = SprintRepository(session)

    def _status_equals(self, sprint: Sprint, status: SprintStatus) -> bool:
        """Compare sprint.status to a SprintStatus member, handling both string and Enum values."""
        current = sprint.status
        # If stored as an Enum member
        if isinstance(current, SprintStatus):
            return current == status
        # If stored as a string value
        return current == status.value

    async def _validate_project(self, project_id: UUID) -> None:
        project = await self.session.scalar(
            select(Project).where(Project.id == project_id)
        )
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

    async def create(self, payload: SprintCreate, user_id: UUID) -> Sprint:
        await self._validate_project(payload.project_id)

        existing = await self.repository.get_by_project_and_name(
            payload.project_id, payload.name
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Sprint with this name already exists in the project",
            )

        return await self.repository.create(payload, user_id)

    async def get(self, sprint_id: UUID) -> Sprint:
        sprint = await self.repository.get_by_id(sprint_id)
        if not sprint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sprint not found",
            )
        return sprint

    async def list(self, project_id: UUID | None = None) -> list[Sprint]:
        if project_id:
            await self._validate_project(project_id)
        return await self.repository.list(project_id)

    async def update(
        self, sprint_id: UUID, payload: SprintUpdate, user_id: UUID
    ) -> Sprint:
        sprint = await self.get(sprint_id)

        if self._status_equals(sprint, SprintStatus.COMPLETED) or self._status_equals(
            sprint, SprintStatus.CLOSED
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Completed or closed sprints cannot be updated",
            )

        data = payload.model_dump(exclude_unset=True)
        start_date = data.get("start_date", sprint.start_date)
        end_date = data.get("end_date", sprint.end_date)
        if end_date < start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be greater than or equal to start date",
            )

        if "name" in data:
            existing = await self.repository.get_by_project_and_name(
                sprint.project_id, data["name"]
            )
            if existing and existing.id != sprint.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Sprint with this name already exists in the project",
                )

        return await self.repository.update(sprint, user_id, **data)

    async def start(self, sprint_id: UUID, user_id: UUID) -> Sprint:
        sprint = await self.get(sprint_id)

        if not self._status_equals(sprint, SprintStatus.PLANNED):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only Planned sprints can be started",
            )

        active = await self.repository.get_active_by_project(sprint.project_id)
        if active and active.id != sprint.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This project already has an active sprint",
            )

        return await self.repository.update(
            sprint, user_id, status=SprintStatus.ACTIVE.value
        )

    async def close(self, sprint_id: UUID, user_id: UUID) -> Sprint:
        sprint = await self.get(sprint_id)

        if not self._status_equals(sprint, SprintStatus.ACTIVE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only Active sprints can be completed",
            )

        return await self.repository.update(
            sprint, user_id, status=SprintStatus.COMPLETED.value
        )