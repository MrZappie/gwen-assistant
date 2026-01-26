import os
from config.preferences import set_value , get_value
import pythoncom
import win32com.client
import win32gui

def pick_folder_thread():
    pythoncom.CoInitialize()
    try:
        shell = win32com.client.Dispatch("Shell.Application")

        hwnd = win32gui.GetForegroundWindow()

        folder = shell.BrowseForFolder(
            hwnd,
            "Select Project Directory",
            0,
            None
        )

        if folder is None:
            return None

        path = folder.Self.Path
        set_value("PROJECT_DIR", path)
        return path

    finally:
        pythoncom.CoUninitialize()


def get_project_status():
    PROJECT_DIR = get_value("PROJECT_DIR")
    if not PROJECT_DIR or PROJECT_DIR == '':
        print("[LOG]: PROJECT_DIR IS NOT PRESENT")
        return None
    else:
        print("[LOG]: PROJECT_DIR IS PRESENT")
        return PROJECT_DIR
    
def reset_project():
    set_value("PROJECT_DIR", '')