from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import library, analyze, import_ as import_router, export_ as export_router, bridge

app = FastAPI(title="DAWSheet Bridge Hub")

# Basic CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(library.router, prefix="/api/library", tags=["library"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["analyze"])
app.include_router(import_router.router, prefix="/api/import", tags=["import"]) 
app.include_router(export_router.router, prefix="/api/export", tags=["export"]) 
app.include_router(bridge.router, prefix="/api/bridge", tags=["bridge"]) 

# Serve frontend static files
app.mount("/", StaticFiles(directory="webapp/frontend", html=True), name="frontend")

@app.get("/api/health")
def health():
    return {"ok": True}
