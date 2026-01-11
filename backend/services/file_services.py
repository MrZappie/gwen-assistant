
import os
from dotenv import get_key

MAX_CHARS = 25000

def get_file_content(file_path):
    
    PROJECT_DIR = get_key(".env","PROJECT_DIR")
    abs_file_path = os.path.join(PROJECT_DIR,file_path)
    if not abs_file_path.startswith(PROJECT_DIR):
        return f'Error: {file_path} is not a valid directory (it is outside project directory)'
    
    if not os.path.isfile(abs_file_path):
        return f'Error: {file_path} is not a file'
    
    content = ""
    try:
        with open(abs_file_path,"r") as f:
            content = f.read(MAX_CHARS)
    except:
        return f"Error in loading {file_path} file"

    return content

