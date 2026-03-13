from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from data.data import init_db
import time
import os

init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://bfdc-176-221-197-123.ngrok-free.app",
        "http://localhost:5173",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API роуты (должны быть ДО статики!)
from routers import all_routers
for router in all_routers:
    app.include_router(router)

# Раздача изображений
app.mount("/data/img", StaticFiles(directory="data/img"), name="data_img")

# Раздача статики фронтенда (в конце!)
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

# SPA роутинг - все неизвестные пути отдают index.html
@app.get("/{catchall:path}")
async def serve_spa(catchall: str):
    # Игнорируем API пути
    if catchall.startswith("api/") or catchall.startswith("data/") or catchall.startswith("docs"):
        raise HTTPException(status_code=404)
    return FileResponse(os.path.join(static_path, "index.html"))