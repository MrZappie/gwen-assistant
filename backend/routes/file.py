from concurrent.futures import ThreadPoolExecutor
import asyncio
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException

from ai.models.file_models import SaveFileData
from backend.services.file_services import get_file_content
from backend.services.project_directory import pick_folder_thread
from config.preferences import get_value

executor = ThreadPoolExecutor(max_workers=1)

import os
from fastapi import HTTPException


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
    
    # FIX: Join the path to ROOT_DIR first, then resolve
    full_path = (ROOT_DIR / path).resolve() 

    # Security Check
    if ROOT_DIR not in full_path.parents and full_path != ROOT_DIR:
        raise HTTPException(status_code=403, detail="Access Denied")

    if not full_path.is_file():
        raise HTTPException(status_code=400, detail="Not a file")

    return {
        "name": full_path.name,
        "type": "file",
        "content": get_file_content(str(full_path))
    }

@router.get("/api/open_folder")
def open_folder(path: str = ""):
    PROJECT_DIR = get_value("PROJECT_DIR")
    ROOT_DIR = Path(PROJECT_DIR).resolve()

    # If path is empty, use root
    full_path = (ROOT_DIR / path).resolve()

    if ROOT_DIR not in full_path.parents and full_path != ROOT_DIR:
        raise HTTPException(status_code=403, detail="Invalid path")

    if not full_path.is_dir():
        raise HTTPException(status_code=400, detail="Not a directory")

    children = []
    for entry in full_path.iterdir():
        rel_path = entry.relative_to(ROOT_DIR).as_posix()

        children.append({
            "name": entry.name,
            "type": "folder" if entry.is_dir() else "file",
            "path": rel_path
        })

    return {"children": children}

@router.post("/api/save-file")
async def save_file(data: SaveFileData): # 2. Add the type hint here
    try:
        # 3. Access attributes using dot notation: data.path
        # Use absolute path logic if needed, but ensure it's safe
        PROJECT_DIR =get_value("PROJECT_DIR")
        full_path = os.path.abspath(os.path.join(PROJECT_DIR, data.path))
        
        # Simple security check: Ensure the path is inside the current directory
        if not full_path.startswith(PROJECT_DIR):
            raise HTTPException(status_code=403, detail="Access denied")

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(data.content)
            
        return {"message": "File saved successfully"}
    except Exception as e:
        print(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail=str(e))