# Qyntara AI - Developer Guide

## Project Overview
Qyntara AI is a Maya plugin for intelligent 3D scene validation.

## Structure
- `ui/`: PySide2/PySide6 widgets using `qt_utils` for compatibility.
- `core/`: Validation logic (geometry, transforms, UVs).
- `server/`: FastAPI server and `mayapy` worker.
- `ai_assist/`: Interfaces for AI models.
- `rules/`: JSON ruleset configuration.

## Setup
1. Install dependencies:
   ```bash
   pip install -r install/requirements.txt
   ```
2. Register Plugin (Maya 2022-2027):
   ```bash
   python install/install_plugin.py
   ```
   This creates a `.mod` file in your Maya modules directory pointing to this repository.

## Running the UI
In Maya Python Script Editor:
```python
import qyntara_ai.ui.main_window as gui
win = gui.show()
```

## Running the Backend
1. Start Redis:
   ```bash
   redis-server
   ```
2. Start API Server:
   ```bash
   uvicorn qyntara_ai.server.api_server:app --reload
   ```
3. Start Worker (must find `mayapy` in your PATH):
   ```bash
   mayapy qyntara_ai/server/worker.py
   ```

## Adding to Maya Shelf
To define a shelf button:
1. Open Script Editor > Python.
2. Run:
   ```python
   import qyntara_ai.install.create_shelf as cs
   cs.create_shelf()
   ```

## Cloud / Docker Deployment
To run the validation server with Redis:
```bash
docker-compose up --build
```
This starts the FastAPI server at `http://localhost:8000`.

## Adding Rules
Edit `qyntara_ai/rules/qyntara_ruleset.json`. define a new rule ID and map it to a function in `core/`.
