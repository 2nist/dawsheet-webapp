from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DAWSheet API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "DAWSheet API", "version": "1.0.0"}

@app.get("/songs")
async def get_songs():
    return [{"id": 1, "title": "Test Song", "artist": "Test Artist"}]

@app.get("/api/health")
def health():
    return {"status": "healthy"}

print("Server created successfully")
