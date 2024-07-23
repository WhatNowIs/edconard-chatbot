from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from src.core.models.base import Thread, User, Workspace
from src.core.services.service import Service
from src.utils.logger import get_logger

class WorkspaceService(Service):
    def __init__(self, db_session: AsyncSession):
        super().__init__(Workspace, db_session)
        self.logger = get_logger()

    async def create(self, workspace_in: Workspace) -> Workspace:
        self.logger.info(f"Creating a new workspace with name: {workspace_in.name}")
        workspace_in.created_at = datetime.utcnow()
        async with self.db_session as session:
            session.add(workspace_in)
            await session.commit()
            await session.refresh(workspace_in)
        self.logger.info(f"Created workspace with id: {workspace_in.id}")
        return workspace_in

    async def add_user_to_workspace(self, workspace_id: str, user_id: str) -> None:
        self.logger.info(f"Adding user {user_id} to workspace {workspace_id}")
        async with self.db_session as session:
            workspace = await self.get(workspace_id)
            user = await session.get(User, user_id)
            workspace.users.append(user)
            await session.commit()
        self.logger.info(f"Added user {user_id} to workspace {workspace_id}")

    async def remove_user_from_workspace(self, workspace_id: str, user_id: str) -> None:
        self.logger.info(f"Removing user {user_id} from workspace {workspace_id}")
        async with self.db_session as session:
            workspace = await self.get(workspace_id)
            user = await session.get(User, user_id)
            workspace.users.remove(user)
            await session.commit()
        self.logger.info(f"Removed user {user_id} from workspace {workspace_id}")

    async def add_thread_to_workspace(self, workspace_id: str, thread_id: str) -> None:
        self.logger.info(f"Adding thread {thread_id} to workspace {workspace_id}")
        async with self.db_session as session:
            workspace = await self.get(workspace_id)
            thread = await session.get(Thread, thread_id)
            workspace.threads.append(thread)
            await session.commit()
        self.logger.info(f"Added thread {thread_id} to workspace {workspace_id}")

    async def remove_thread_from_workspace(self, workspace_id: str, thread_id: str) -> None:
        self.logger.info(f"Removing thread {thread_id} from workspace {workspace_id}")
        async with self.db_session as session:
            workspace = await self.get(workspace_id)
            thread = await session.get(Thread, thread_id)
            workspace.threads.remove(thread)
            await session.commit()
        self.logger.info(f"Removed thread {thread_id} from workspace {workspace_id}")
