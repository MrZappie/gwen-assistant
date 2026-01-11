
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import os, signal

from backend.routes import file
from backend.services.project_directory import get_project_status, reset_project
from config.preferences import preference_init

# -------------------------------
env_path = Path(".env")
required_keys = ["GROQ_API_KEY"]

if not env_path.exists():
    # Create .env with placeholders
    with env_path.open("w") as f:
        f.write("GROQ_API_KEY='default'\n")
    print(
        "Created .env file with placeholders.\n"
        "Please fill in GROQ_API_KEY if you want to use ONLINE mode.\n"
        "Run the script again after filling the .env file."
    )
    exit(0) 

preference_init()

# -------------------------------    

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("-------[SERVER STARTING]---------")
    load_dotenv()
    print("Environment loaded")

    yield
    
    print("-------[SERVER SHUTTING DOWN]---------")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict to specific frontend port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(file.router)

@app.post("/shutdown")
def shutdown():
    os.kill(os.getpid(), signal.SIGTERM)

@app.get("/api/close-project")
def close_project():
    reset_project()
    return {
        "error": False
    }

@app.get("/api/project-status")
def get_status():
    return {
        "project_directory": get_project_status()
    }


#this must be after including routers and any paths that contain /api/..
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
