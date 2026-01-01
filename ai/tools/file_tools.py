import os
from config.settings import PROJECT_DIR
from langchain_core.tools import tool

def safe_path(user_path: str) -> str:
    joined_path = os.path.join(PROJECT_DIR, user_path)
    resolved_path = os.path.realpath(joined_path)

    if not resolved_path.startswith(PROJECT_DIR):
        raise ValueError("Access denied: path outside project directory")

    return resolved_path


@tool
def read_file(path: str) -> str:
    """Read the full contents of a text file inside the project directory."""
    try:
        safe = safe_path(path)
        with open(safe, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.strip():
            return "[EMPTY FILE]"

        return content
    except Exception as e:
        return f"[ERROR] {str(e)}"


@tool
def find_file(filename: str) -> str:
    """Search for a file by name anywhere inside the project directory."""
    import difflib

    matches = []
    all_files = []

    for root, _, files in os.walk(PROJECT_DIR):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, PROJECT_DIR).replace("\\", "/")
            all_files.append((f, rel))
            if f == filename:
                matches.append(rel)

    if matches:
        return "Exact matches:\n" + "\n".join(matches)

    suggestions = difflib.get_close_matches(
        filename, [f for f, _ in all_files], n=5, cutoff=0.6
    )

    if suggestions:
        return (
            "No exact match found.\nSimilar files with paths:\n"
            + "\n".join(rel for f, rel in all_files if f in suggestions)
        )

    return "No matching or similar files found."


@tool
def list_dir(path: str) -> str:
    """List files and folders directly inside a given directory (non-recursive) (also PROJECT_DIR is the path by default)."""
    try:
        safe = safe_path(path)
        if not os.path.isdir(safe):
            return f"Not a directory: {path}"

        entries = []
        for name in os.listdir(safe):
            full = os.path.join(safe, name)
            rel = os.path.relpath(full, PROJECT_DIR).replace("\\", "/")
            entries.append(
                f"[DIR] {rel}" if os.path.isdir(full) else f"[FILE] {rel}"
            )

        return "\n".join(sorted(entries))
    except Exception as e:
        return str(e)


@tool
def write_tool(text: str, file_path: str):
    """ Write text content to a file inside the project directory."""
    try:
        safe = safe_path(file_path)
        os.makedirs(os.path.dirname(safe), exist_ok=True)
        with open(safe, "w", encoding="utf-8") as f:
            f.write(text)
        return "File Written Successful"
    except Exception as e:
        return str(e)

@tool
def find_dir(dirname: str) -> str:
    """
    Search for a directory or module by name anywhere inside the project directory.

    """
    matches = []

    for root, dirs, _ in os.walk(PROJECT_DIR):
        for d in dirs:
            if d == dirname:
                full_path = os.path.join(root, d)
                rel_path = os.path.relpath(full_path, PROJECT_DIR).replace("\\", "/")
                matches.append(rel_path)

    if matches:
        return "Exact matches:\n" + "\n".join(matches)

    return "No matching directories found."

TOOLS = [write_tool, list_dir, read_file, find_file,find_dir]
