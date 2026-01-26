import os
from config.preferences import get_value
from langchain_core.tools import tool


def safe_path(user_path: str) -> str:
    
    PROJECT_DIR = get_value("PROJECT_DIR")
    joined_path = os.path.join(PROJECT_DIR, user_path)
    resolved_path = os.path.realpath(joined_path)

    if not resolved_path.startswith(PROJECT_DIR):
        raise ValueError("Access denied: path outside project directory")

    return resolved_path

@tool
def list_dir_recursive(
    path: str = "",
    max_depth: int = 3,
    max_entries: int = 50
) -> str:
    """
    Recursively list files and folders starting at path,
    with depth and entry limits. Use this when you want to list the entire folder structure starting from the given directory.
    Much more efficient when trying to search for multiple directories
    """

    PROJECT_DIR = get_value("PROJECT_DIR")
    start = safe_path(path)
    results = []
    count = 0

    for root, dirs, files in os.walk(start):
        depth = os.path.relpath(root, start).count(os.sep)
        if depth > max_depth:
            dirs[:] = []
            continue

        for d in dirs:
            full = os.path.join(root, d)
            rel = os.path.relpath(full, PROJECT_DIR).replace("\\", "/")
            results.append(f"[DIR]  {rel}")
            count += 1
            if count >= max_entries:
                return "\n".join(results) + "\n[TRUNCATED]"

        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, PROJECT_DIR).replace("\\", "/")
            results.append(f"[FILE] {rel}")
            count += 1
            if count >= max_entries:
                return "\n".join(results) + "\n[TRUNCATED]"

    return "\n".join(results)

@tool
def list_files_recursive(
    path: str = "",
    max_depth: int = 5,
    max_files: int = 300
) -> str:
    """
    Recursively list only files under a directory and its sub-directory.
    Use this when you want to list the many file under a  folder structure starting from the given directory.
    """

    PROJECT_DIR = get_value("PROJECT_DIR")
    start = safe_path(path)
    files_out = []
    count = 0

    for root, _, files in os.walk(start):
        depth = os.path.relpath(root, start).count(os.sep)
        if depth > max_depth:
            continue

        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, PROJECT_DIR).replace("\\", "/")
            files_out.append(rel)
            count += 1
            if count >= max_files:
                return "\n".join(files_out) + "\n[TRUNCATED]"

    return "\n".join(files_out)


@tool
def file_metadata(path: str) -> str:
    """
    Return metadata about a file.
    """

    import time

    safe = safe_path(path)
    if not os.path.exists(safe):
        return "File does not exist."

    stat = os.stat(safe)

    return (
        f"Path: {path}\n"
        f"Size: {stat.st_size} bytes\n"
        f"Modified: {time.ctime(stat.st_mtime)}\n"
        f"Is file: {os.path.isfile(safe)}\n"
        f"Is directory: {os.path.isdir(safe)}"
    )

@tool
def read_multiple_files(
    paths: list[str],
    max_total_chars: int = 8000
) -> str:
    """
    Read multiple files and return their contents in a clearly separated format.
    Use this when you want to analyse multiple file contents together.
    """

    PROJECT_DIR = get_value("PROJECT_DIR")
    output = []
    total_chars = 0

    for path in paths:
        try:
            safe = safe_path(path)
            with open(safe, "r", encoding="utf-8") as f:
                content = f.read()

            if not content.strip():
                content = "[EMPTY FILE]"

        except Exception as e:
            content = f"[ERROR] {e}"

        block = (
            f"\n===== FILE: {path} =====\n"
            f"{content}\n"
            f"===== END FILE =====\n"
        )

        total_chars += len(block)
        if total_chars > max_total_chars:
            output.append("[TRUNCATED: size limit reached]")
            break

        output.append(block)

    return "".join(output)

