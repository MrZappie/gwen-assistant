# AI Chat Mini Project

**Authors:** Sourav & Abhinav

## Overview
This is a small college‑level project that demonstrates a **full‑stack AI chat application** built with:
- **FastAPI** backend exposing REST endpoints for chat sessions and file handling.
- **LangChain / LangGraph** agents that decide whether a request needs code analysis or normal conversation and interact with the filesystem using controlled tool calls.
- A lightweight **static frontend** (HTML, CSS, JavaScript) that communicates with the backend via the provided API.
- Simple configuration handling via a `.env` file and a `data.json` preferences store.

The system can:
1. Maintain multiple chat sessions, persisting both normal and debug logs.
2. Stream AI responses to the client in real‑time.
3. Reset or close a project directory through dedicated API calls.
4. Run in **LOCAL** mode (default) or **ONLINE** mode when a `GROQ_API_KEY` is supplied.

## Project Structure
```
.
├─ ai/                     # Core AI utilities, agents, models
│   ├─ agent/              # LangGraph graph definition
│   ├─ models/             # Pydantic request models
│   └─ utils/              # Storage, streaming helpers
├─ backend/                # FastAPI server
│   ├─ routes/             # chat and file endpoints
│   └─ services/           # Helper services (project status, file ops)
├─ config/                 # Preference handling (data.json)
├─ frontend/               # Static HTML/CSS/JS UI
├─ .env                    # Environment variables (GROQ_API_KEY placeholder)
├─ data.json               # Stores PROJECT_DIR and MODE
├─ requirements.txt        # Python dependencies
└─ ai_test.py              # Simple CLI test script
```

## Setup & Installation
1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd <repo-directory>
   ```
2. **Create a virtual environment & install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # on Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configure environment variables**
   - The first run will generate a `.env` file with a placeholder `GROQ_API_KEY`.  
   - If you want to use the online mode, replace the placeholder with a valid key.
4. **Run the server**
   ```bash
   uvicorn backend.server:app --reload
   ```
   The server will serve the frontend at `http://localhost:8000/` and expose the API under `/api`.
5. **Optional: Test via CLI**
   ```bash
   python ai_test.py
   ```
   Type messages, press `Enter`, and type `q` to quit.

## Usage
- Open `http://localhost:8000/` in a browser. The UI lets you start a new chat session, view past sessions, and delete them.
- API endpoints (see `backend/routes/`):
  - `GET /api/project-status` – returns current project directory status.
  - `GET /api/close-project` – resets the project directory.
  - `POST /api/chat/{session_id}` – streams AI responses for a given session.
  - `GET /chat/{session_id}` – fetches the clean chat log.
  - `DELETE /chat/{session_id}` – removes a session.
  - `GET /sessions` – lists all stored sessions.

## Design Highlights
- **Planner node** (`plan_mode_ai`) decides if a request requires *analysis* (code/module inspection) or simple *conversation*.
- **Tool node** uses a registry (`ai.tools.tool_registry`) to safely interact with the filesystem – the agent never accesses files directly.
- **Controlled execution**: the agent follows strict invariants (no invented paths, only tool output is trusted) to ensure reproducibility and safety.
- **Debug vs. normal logs**: each chat message is stored twice – a clean log for UI consumption and a detailed debug log for developers.

## Contributing
Feel free to fork the repo and submit pull requests. When adding new features, keep the following in mind:
- Respect the tool‑call invariants defined in `ai/agent/graph_builder.py`.
- Update the README to reflect any new endpoints or configuration options.
- Add unit tests where appropriate.

## License
This project is licensed under the MIT License – see the `LICENSE` file for details.
