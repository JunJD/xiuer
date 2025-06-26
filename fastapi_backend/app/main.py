from fastapi import FastAPI
from .schemas.users import UserCreate, UserRead, UserUpdate
from .services.users import auth_backend, fastapi_users, AUTH_URL_PATH
from fastapi.middleware.cors import CORSMiddleware
from .utils import simple_generate_unique_route_id
from app.routes.items import router as items_router
from app.routes.keywords import router as keywords_router
from app.routes.webhook import router as webhook_router
from app.routes.notes import router as notes_router
from app.routes.tasks import router as tasks_router
from app.config import settings

app = FastAPI(
    generate_unique_id_function=simple_generate_unique_route_id,
    openapi_url=settings.OPENAPI_URL,
)

# Middleware for CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication and user management routes
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix=f"/{AUTH_URL_PATH}/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix=f"/{AUTH_URL_PATH}",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix=f"/{AUTH_URL_PATH}",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix=f"/{AUTH_URL_PATH}",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# Include items routes
app.include_router(items_router, prefix="/items")

# Include keywords management routes
app.include_router(keywords_router, prefix="/api/keywords", tags=["keywords"])

# Include webhook routes (数据接收和处理)
app.include_router(webhook_router, prefix="/api/webhook", tags=["webhook"])

# Include notes routes (笔记查询)
app.include_router(notes_router, prefix="/api/notes", tags=["notes"])

# Include tasks routes (任务管理)
app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])
