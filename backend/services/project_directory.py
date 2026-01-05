from dotenv import set_key
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
            print(f".env updated: PROJECT_DIR='{path}'")

            return path
        except AttributeError:
            return None
    finally:
        pythoncom.CoUninitialize()
