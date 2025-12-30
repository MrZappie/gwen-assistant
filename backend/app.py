from flask import Flask, jsonify, render_template
from flask_cors import CORS
import tkinter as tk
from tkinter import filedialog
import os

app = Flask(__name__)
CORS(app) # Allows the frontend to talk to the backend

@app.route('/select-folder', methods=['GET'])
def select_folder():
    # Initialize tkinter and hide the main window
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True) # Bring the folder picker to front
    
    # Open folder selection dialog
    folder_path = filedialog.askdirectory()
    root.destroy()

    if folder_path:
        # Get list of files in the folder
        try:
            files = os.listdir(folder_path)
            return jsonify({
                "status": "success",
                "folder_name": os.path.basename(folder_path),
                "files": files
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    
    return jsonify({"status": "cancelled"})

if __name__ == '__main__':
    app.run(port=5000, debug=True)