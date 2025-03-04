import src.schema as dto
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.routers.auth.accounts import get_session
from src.core.config.postgres import get_db
from src.core.models.base import Workspace
from src.core.services.workspace import WorkspaceService
from src.schema import WorkspaceCreate
from src.utils.logger import get_logger

workspace_router = APIRouter()

def get_workspace_service(db: AsyncSession = Depends(get_db)) -> WorkspaceService:
    return WorkspaceService(db)

@workspace_router.post("/", response_model=dto.Workspace)
async def create_workspace(
    data: WorkspaceCreate,
    session: dict = Depends(get_session),
    workspace_service: WorkspaceService = Depends(get_workspace_service)
):
    if "sub" in session:
        user_id = session["sub"]
        workspace = Workspace(name=data.name)
        created_workspace = await workspace_service.create(workspace)
        await workspace_service.add_user_to_workspace(created_workspace.id, user_id)
        await workspace_service.db_session.commit()

        return dto.Workspace.model_validate(created_workspace)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized to create a workspace",
    )

@workspace_router.post("/{workspace_id}/users/{user_id}")
async def add_user_to_workspace(
    workspace_id: str,
    user_id: str,
    session: dict = Depends(get_session),
    workspace_service: WorkspaceService = Depends(get_workspace_service)
):
    if "sub" in session:
        await workspace_service.add_user(workspace_id, user_id)
        return {"message": f"User {user_id} added to workspace {workspace_id}."}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized to add user to workspace",
    )

@workspace_router.delete("/{workspace_id}/users/{user_id}")
async def remove_user_from_workspace(
    workspace_id: str,
    user_id: str,
    session: dict = Depends(get_session),
    workspace_service: WorkspaceService = Depends(get_workspace_service)
):
    if "sub" in session:
        await workspace_service.remove_user_from_workspace(workspace_id, user_id)
        return {"message": f"User {user_id} removed from workspace {workspace_id}."}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized to remove user from workspace",
    )

@workspace_router.post("/{workspace_id}/threads/{thread_id}")
async def add_thread_to_workspace(
    workspace_id: str,
    thread_id: str,
    session: dict = Depends(get_session),
    workspace_service: WorkspaceService = Depends(get_workspace_service)
):
    if "sub" in session:
        await workspace_service.add_thread_to_workspace(workspace_id, thread_id)
        return {"message": f"Thread {thread_id} added to workspace {workspace_id}."}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized to add thread to workspace",
    )

@workspace_router.delete("/{workspace_id}/threads/{thread_id}")
async def remove_thread_from_workspace(
    workspace_id: str,
    thread_id: str,
    session: dict = Depends(get_session),
    workspace_service: WorkspaceService = Depends(get_workspace_service)
):
    if "sub" in session:
        await workspace_service.remove_thread_from_workspace(workspace_id, thread_id)
        return {"message": f"Thread {thread_id} removed from workspace {workspace_id}."}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized to remove thread from workspace",
    )

@workspace_router.get("/", response_model=List[dto.Workspace])
async def fetch_workspaces(
    session: dict = Depends(get_session),
    workspace_service: WorkspaceService = Depends(get_workspace_service)
):
    if "sub" in session:
        user_id = session["sub"]
        workspaces = await workspace_service.get_all_by_user_id(user_id)
        return [dto.Workspace.model_validate(workspace) for workspace in workspaces]

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized to access workspaces",
    )

@workspace_router.get("/{workspace_id}/users", response_model=List[dto.UserModel])
async def fetch_users_from_workspace(
    workspace_id: str,
    session: dict = Depends(get_session),
    workspace_service: WorkspaceService = Depends(get_workspace_service)
):
    if "sub" in session:
        user_id = session['sub']
        users = await workspace_service.get_users_by_workspace_id(user_id, workspace_id)

        get_logger().info([user.to_dict() for user in users])
        
        return [dto.UserModel(**user.to_dict()) for user in users]

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized to access workspace users",
    )
