import os

from fastapi import FastAPI
from backend.api.auth_routes import router as auth_router
from fastapi.middleware.cors import CORSMiddleware


def _get_allowed_origins() -> list[str]:
    default_origins = ",".join(
        [
            "http://localhost:5173",
            "http://localhost:5175",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5175",
        ]
    )
    raw_origins = os.getenv("CORS_ALLOW_ORIGINS", default_origins)
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


app = FastAPI(title="MyFirstProject API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
