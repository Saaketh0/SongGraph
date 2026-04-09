from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.graph import router as graph_router
from app.api.routes.health import router as health_router
from app.api.routes.search import router as search_router
from app.api.routes.songs import router as songs_router
from app.core.config import get_settings


settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(graph_router, prefix="/api")
app.include_router(songs_router, prefix="/api")


@app.get("/")
def root() -> dict[str, str]:
    return {"message": f"{settings.app_name} is running"}
