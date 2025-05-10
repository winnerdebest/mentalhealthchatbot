from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pathlib import Path

router = APIRouter()

# Get the static path for reading HTML files
static_path = Path(__file__).parent.parent.parent / "static"

@router.get("/", response_class=HTMLResponse)
async def landing_page():
    with open(static_path / "landing.html") as f:
        return f.read()

@router.get("/about", response_class=HTMLResponse)
async def about_page():
    with open(static_path / "about.html") as f:
        return f.read()

@router.get("/chat", response_class=HTMLResponse)
async def chat_page():
    with open(static_path / "index.html") as f:
        return f.read() 