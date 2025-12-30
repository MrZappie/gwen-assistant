from flask import Flask, jsonify
from flask_cors import CORS # Install with: pip install flask-cors

app = Flask(__name__)
CORS(app) # This is required to fix the "Fetch Error"

@app.route('/select-folder')
def select_folder():
    # Your folder selection logic here
    return jsonify({
        "status": "success",
        "folder_name": "Project_Gwen",
        "files": ["main.py", "index.html"]
    })

if __name__ == '__main__':
    app.run(port=5000)