import os
import shutil
from src.app.tasks.indexing import index_all, reset_index
from src.core.models.base import EntityStatus, User
from src.core.services.role import RoleService, setup_roles
from src.core.services.user import UserService
from src.core.services.workspace import WorkspaceService
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from create_llama.backend.app.settings import init_settings
from create_llama.backend.app.api.routers.chat import chat_router
from src.app.constants import ENV_FILE_PATH
from src.core.config.postgres import get_db
from src.core.services.mail import EmailTemplateService, EmailTypeService
from src.utils.logger import get_logger
from src.app.routers.management.config import config_router
from src.app.routers.management.files import files_router
from src.app.routers.management.tools import tools_router
from src.app.routers.auth.accounts import accounts_router
from src.app.routers.chat.threads import threads_router
from src.app.routers.chat.workspace import workspace_router
from fastapi.middleware.cors import CORSMiddleware
from src.llm.env_config import get_config

load_dotenv(
    dotenv_path=ENV_FILE_PATH,
)

init_settings()

app = FastAPI(
    title="Edconrad Chatboat",
    description="Edconrad Chatboat is an AI RAG chatbot.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)


environment = os.getenv("ENVIRONMENT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add chat router from create_llama/backend
app.include_router(config_router, prefix="/api/management/config", tags=["Management"])
app.include_router(files_router, prefix="/api/management/files", tags=["Management"])
app.include_router(tools_router, prefix="/api/management/tools", tags=["Management"])
app.include_router(accounts_router, prefix="/api/auth/accounts", tags=["Auth"])
app.include_router(threads_router, prefix="/api/chat/threads", tags=["Thread"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(workspace_router, prefix="/api/workspaces", tags=["Workspaces"])

@app.get("/")
async def redirect():

    config = get_config()
    if config.configured:
        # system is configured - / points to chat UI
        return FileResponse("static/index.html")
    else:
        # system is not configured - redirect to onboarding page
        return RedirectResponse(url="/admin/#new")


app.mount("/api/data", StaticFiles(directory="data"), name="static")
app.mount("", StaticFiles(directory="static", html=True), name="static")

# Customize Swagger UI
app.openapi_schema = app.openapi()
app.openapi_schema["info"] = {
    "title": "Edconrad Chatbot",
    "version": "1.0.0",
    "description": "Edconrad Chatboat is an AI RAG chatbot.",
    "contact": {
        "name": "WhatNow.is Support",
        "url": "https://whatnow.is/support",
        "email": "support@whatnow.is",
    }
}

def delete_all_converted_csv(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return

    # Loop through all files and folders in the specified directory
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Delete the file or link
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Delete the directory and its contents
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")


@app.on_event("startup")
async def startup(
):
    async for db in get_db():
        # Get the current directory
        templates_directory = os.path.join(os.getcwd(), 'src', 'templates')

        # Call the populate methods
        email_type_service = EmailTypeService(db_session=db)
        email_template_service = EmailTemplateService(db_session=db)
        role_service = RoleService(db_session = db)

        await email_type_service.populate_email_types()
        await email_template_service.populate_email_templates(templates_directory)
        await setup_roles(role_service)

        async def create_admin():
            obj_in = User(
                first_name = "Byamasu",
                last_name = "Patrick",
                sex = "Male",
                email = "patrick@whatnow.is",
                phone_number = "+265996668149",
                status = EntityStatus.Active
            )
            user_service = UserService(db_session = db)
            workspace_service = WorkspaceService(db_session = db)

            user, is_created = await user_service.create_default_super_admin_account_if_not_exists(obj_in, "Patrick2020")
            
            workspace = await workspace_service.create_default_workspace_if_not_exists(user)
            if is_created:
                await workspace_service.add_user_to_workspace(workspace.id, user.id)
                await workspace_service.db_session.commit()

        await create_admin()


    get_logger().info("Successfully populated default email templates and types")

    if os.getenv("REFRESH_EMBEDDING", "False").lower() == "true":
        # delete_all_converted_csv("tmp/converted_csv")
        reset_index()
        get_logger().info("Successfully upserted data to chromadb")


if __name__ == "__main__":
    app_host = os.getenv("APP_HOST", "0.0.0.0")
    app_port = int(os.getenv("APP_PORT", "8080"))
    reload = environment == "dev"

    uvicorn.run(app="main:app", host=app_host, port=app_port, reload=reload)
