from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import research, discord

app = FastAPI(title="Company Research Assistant API")

# CORS - allow the Next.js frontend to call this backend.
# Tighten allow_origins to your actual frontend domain before final submission.
#
# BUG FIX: allow_origins=["*"] combined with allow_credentials=True is an
# invalid CORS configuration per spec - browsers will reject responses that
# echo back a wildcard origin on a request made with credentials, so any
# fetch() from the frontend using `credentials: "include"` would silently
# fail. This app has no authentication or cookies (per the assignment's
# "No authentication required" constraint), so credentialed requests are
# never needed - allow_credentials is now False, which also makes the
# wildcard origin valid again.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(research.router, prefix="/api")
app.include_router(discord.router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}