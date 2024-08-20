from typing import List
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.core.models.base import Thread, User, Workspace
from src.core.services.service import Service
from src.utils.logger import get_logger

class WorkspaceService(Service):
    def __init__(self, db_session: AsyncSession):
        super().__init__(Workspace, db_session)
        self.logger = get_logger()

    async def create(self, workspace: Workspace) -> Workspace:
        self.logger.info(f"Creating workspace: {workspace.name}")
        self.db_session.add(workspace)
        await self.db_session.flush()
        await self.db_session.refresh(workspace)
        return workspace
    
    async def create_default_workspace_if_not_exists(self, user: User) -> Workspace:
        self.logger.info(f"Creating default workspace for user {user.id}")

        try:
            default_workspace = await self.db_session.execute(
                select(Workspace).filter(Workspace.name == "default")
            )
            default_workspace = default_workspace.scalar_one_or_none()

            if not default_workspace:
                default_workspace = Workspace(name="default")
                self.db_session.add(default_workspace)
                await self.db_session.flush()
                await self.db_session.refresh(default_workspace)
                self.logger.info(f"Created default workspace for user {user.id}")
            else:
                self.logger.info(f"Default workspace already exists")

            return default_workspace

        except Exception as e:
            self.logger.error(f"Error creating default workspace for user {user.id}: {e}")
            raise

    async def add_user_to_workspace(self, workspace_id: str, user_id: str) -> None:
        self.logger.info(f"Adding user {user_id} to workspace {workspace_id}")
        try:
            async with self.db_session.begin_nested():
                workspace = await self.db_session.execute(
                    select(Workspace).options(selectinload(Workspace.users)).where(Workspace.id == workspace_id)
                )
                workspace = workspace.scalar_one_or_none()

                user = await self.db_session.get(User, user_id)
                
                if user and workspace:
                    workspace.users.append(user)
                    self.logger.info(f"Added user {user_id} to workspace {workspace_id}")
                else:
                    self.logger.error(f"Workspace or user not found: workspace_id={workspace_id}, user_id={user_id}")
                    raise ValueError("Workspace or User not found")
        except Exception as e:
            self.logger.error(f"Failed to add user {user_id} to workspace {workspace_id}: {e}")
            raise

    async def remove_user_from_workspace(self, workspace_id: str, user_id: str) -> None:
        self.logger.info(f"Removing user {user_id} from workspace {workspace_id}")
        async with self.db_session.begin():
            workspace = await self.get(workspace_id)
            user = await self.db_session.get(User, user_id)
            if user and workspace:
                workspace.users.remove(user)
                await self.db_session.commit()
        self.logger.info(f"Removed user {user_id} from workspace {workspace_id}")

    async def add_thread_to_workspace(self, workspace_id: str, thread_id: str) -> None:
        self.logger.info(f"Adding thread {thread_id} to workspace {workspace_id}")
        async with self.db_session.begin():
            workspace = await self.get(workspace_id)
            thread = await self.db_session.get(Thread, thread_id)
            if thread and workspace:
                workspace.threads.append(thread)
                await self.db_session.commit()
        self.logger.info(f"Added thread {thread_id} to workspace {workspace_id}")

    async def remove_thread_from_workspace(self, workspace_id: str, thread_id: str) -> None:
        self.logger.info(f"Removing thread {thread_id} from workspace {workspace_id}")
        async with self.db_session.begin():
            workspace = await self.get(workspace_id)
            thread = await self.db_session.get(Thread, thread_id)
            if thread and workspace:
                workspace.threads.remove(thread)
                await self.db_session.commit()
        self.logger.info(f"Removed thread {thread_id} from workspace {workspace_id}")

    async def get_all_by_user_id(self, user_id: str) -> List[Workspace]:
        self.logger.info(f"Fetching all workspaces for user {user_id}")
        async with self.db_session.begin():
            result = await self.db_session.execute(
                select(Workspace).join(Workspace.users).filter(User.id == user_id)
            )
            workspaces = result.scalars().all()
        self.logger.info(f"Fetched {len(workspaces)} workspaces for user {user_id}")
        return workspaces