from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, clients, backups


app = FastAPI(
    title="Backup Status API",
    description="Track backup job statuses across multiple SaaS clients.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(backups.router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
