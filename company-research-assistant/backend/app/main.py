from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import research, discord

app = FastAPI(title="Company Research Assistant API")

# CORS - allow the Next.js frontend to call this backend.
# Tighten allow_origins to your actual frontend domain before final submission.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(research.router, prefix="/api")
app.include_router(discord.router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}