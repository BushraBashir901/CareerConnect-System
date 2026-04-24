from app.api.v1.router import router as api_router
from app.api.v1.endpoints.chat_ws_api import router as ws_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

app = FastAPI()

# Add CORS middleware first
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include WebSocket router separately to avoid authentication issues
app.include_router(ws_router, prefix="/api/v1/ws", tags=["websocket"])

# Include main API router
app.include_router(api_router)