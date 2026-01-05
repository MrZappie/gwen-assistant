from concurrent.futures import ThreadPoolExecutor
import asyncio
from fastapi import APIRouter

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
