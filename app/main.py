from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import chat, main
from pathlib import Path

app = FastAPI(
    title="Conversational Support System",
    description="An empathetic chatbot for emotional support",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files from the root-level static folder
static_path = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Include routers
app.include_router(main.router)  # This will handle the landing page and chat page
app.include_router(chat.router, prefix="/api")  # This will handle the chat API endpoints
