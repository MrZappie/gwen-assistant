from concurrent.futures import ThreadPoolExecutor
import asyncio
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException

from backend.services.file_services import get_file_content
from backend.services.project_directory import pick_folder_thread
from config.preferences import get_value

executor = ThreadPoolExecutor(max_workers=1)


router = APIRouter()

@router.get("/api/selectdir")
async def select_directory():
    loop = asyncio.get_running_loop()
    path = await loop.run_in_executor(executor, pick_folder_thread)
    print("[LOG] SelectDir: ", path)
    if not path:
        return {"message": "No directory selected", "error": True}
    
    return {"message": "Directory Changed", "error": False, "directory": path}


@router.get("/api/get_file_content")
def get_file(path: str):
    PROJECT_DIR = get_value("PROJECT_DIR")
    ROOT_DIR = Path(PROJECT_DIR).resolve()
    full_path = Path(path).resolve()  # accept absolute paths

    if ROOT_DIR not in full_path.parents and full_path != ROOT_DIR:
        raise HTTPException(status_code=403, detail="Invalid path")

    if not full_path.is_file():
        raise HTTPException(status_code=400, detail="Not a file")

    return {
        "name": full_path.name,
        "type": "file",
        "content": get_file_content(str(full_path))
    }


@router.get("/api/open_folder")
def open_folder(path: str):
    PROJECT_DIR = get_value("PROJECT_DIR")
    ROOT_DIR = Path(PROJECT_DIR).resolve()
    full_path = (ROOT_DIR / path).resolve()

    if not str(full_path).startswith(str(ROOT_DIR)):
        raise HTTPException(status_code=403, detail="Invalid path")

    if not full_path.is_dir():
        raise HTTPException(status_code=400, detail="Not a directory")

    children = []
    for entry in full_path.iterdir():
        children.append({
            "name": entry.name,
            "type": "folder" if entry.is_dir() else "file",
            "path": str((Path(path) / entry.name).as_posix())
        })

    return {"children": children}