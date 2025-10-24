
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routes import auth, audios
from .routes import audios, users, roles, areas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Audio Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(audios.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(areas.router)

@app.get("/")
def root():
    return {"status": "ok", "app": "audio-service", "version": "1.0.0"}
