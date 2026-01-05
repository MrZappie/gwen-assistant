
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import threading, time, os, signal

from backend.routes import file

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
#this must be after including routers
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


@app.post("/shutdown")
def shutdown():
    os.kill(os.getpid(), signal.SIGTERM)
