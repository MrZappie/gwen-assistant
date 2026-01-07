from concurrent.futures import ThreadPoolExecutor
import asyncio
import os
from fastapi import APIRouter

from backend.services.file_services import get_file_content
from backend.services.project_directory import pick_folder_thread

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


@router.post("/api/get_file_content/{path: path}")
def get_file(path : str):
    path_list = path.split("/") # splits the relative path to directories and files 
    
    return {
        "name": path_list[-1],
        "type": "file",
        "content": get_file_content(path)
    }

@router.post("/api/open_folder/{path: path}")
def open_folder(path: str):
    if not os.path.isdir(path):
        return {"error": True, "message": "Not a directory"}

    items = []
    for entry in os.scandir(path):
        items.append({
            "name": entry.name,
            "type": "folder" if entry.is_dir() else "file",
            "path": entry.path.replace("\\", "/")
        })

    return {
        "error": False,
        "path": path,
        "children": items
    }