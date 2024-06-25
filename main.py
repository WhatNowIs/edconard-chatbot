import os
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from create_llama.backend.app.settings import init_settings
from create_llama.backend.app.api.routers.chat import chat_router
from src.app.constants import ENV_FILE_PATH
from src.core.dbconfig.postgres import get_db
from src.core.services.mail import EmailTemplateService, EmailTypeService
from src.utils.logger import get_logger
from src.app.routers.management.config import config_router
from src.app.routers.management.files import files_router
from src.app.routers.management.tools import tools_router
from src.app.routers.auth.accounts import accounts_router
from src.app.routers.chat.threads import threads_router
from fastapi.middleware.cors import CORSMiddleware
from src.llm.env_config import get_config

load_dotenv(
    dotenv_path=ENV_FILE_PATH,
)

app = FastAPI(
    title="Edconrad Chatboat",
    description="Edconrad Chatboat is an AI RAG chatbot.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)

init_settings()

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

@app.on_event("startup")
async def startup(
):
    async for db in get_db():
        # Get the current directory
        templates_directory = os.path.join(os.getcwd(), 'src', 'templates')

        # Call the populate methods
        email_type_service = EmailTypeService(db_session=db)
        email_template_service = EmailTemplateService(db_session=db)

        await email_type_service.populate_email_types()
        await email_template_service.populate_email_templates(templates_directory)

    get_logger().info("Successfully populated default email templates and types")


if __name__ == "__main__":
    app_host = os.getenv("APP_HOST", "0.0.0.0")
    app_port = int(os.getenv("APP_PORT", "8000"))
    reload = environment == "dev"

    uvicorn.run(app="main:app", host=app_host, port=app_port, reload=reload)
