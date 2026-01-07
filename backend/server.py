
from contextlib import asynccontextmanager
from dotenv import load_dotenv 
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import threading, time, os, signal

from backend.routes import file
from backend.services.project_directory import get_project_status
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

@app.get("/api/project-status")
def get_status():
    return {
        "has_project_directory": get_project_status()
    }


#this must be after including routers and any paths that contain /api/..
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
