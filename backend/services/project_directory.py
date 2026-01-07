from dotenv import set_key ,get_key
import pythoncom
import win32com.client


def pick_folder_thread():
    pythoncom.CoInitialize()
    try:
        shell = win32com.client.Dispatch("Shell.Application")
        folder = shell.BrowseForFolder(0, "Select Project Directory", 0, None)
        if folder is None:
            return None
        folder_item = folder.Self
        try:
            path = folder_item.Path            
            set_key(".env", "PROJECT_DIR", path)
            return path
        except AttributeError:
            return None
    finally:
        pythoncom.CoUninitialize()

def get_project_status():
    PROJECT_DIR = get_key(".env", "PROJECT_DIR")
    if not PROJECT_DIR or PROJECT_DIR == '':
        print("[LOG]: PROJECT_DIR IS NOT PRESENT")
        return None
    else:
        print("[LOG]: PROJECT_DIR IS PRESENT")
        return PROJECT_DIR