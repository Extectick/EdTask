from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from data.data import ensure_bootstrap_master, init_db
from media import ensure_image_bucket
import os

app = FastAPI()

default_cors_origins = [
    "http://hare.ge",
    "http://www.hare.ge",
    "https://hare.ge",
    "https://www.hare.ge",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
    "http://hare.ge:8001",
    "http://www.hare.ge:8001",
    "https://hare.ge:8001",
    "https://www.hare.ge:8001",
]

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOW_ORIGINS", ",".join(default_cors_origins)).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
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

# Раздача файлов
app.mount("/data/files", StaticFiles(directory="data/files"), name="data_files")

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


@app.on_event("startup")
async def startup():
    init_db()
    ensure_image_bucket()
    ensure_bootstrap_master()
