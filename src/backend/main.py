from fastapi import FastAPI
from backend.api.user_routes import router as user_router
from backend.db import get_conn
from backend.migrate import apply_migrations
from backend.api.auth_routes import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MyFirstProject API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_router)
app.include_router(auth_router)

@app.on_event("startup")
def on_startup():
    conn = get_conn()
    try:
        apply_migrations(conn)
    finally:
        conn.close()