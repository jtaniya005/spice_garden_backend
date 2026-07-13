@echo off
echo Starting Spice Garden API...
echo.
echo Make sure Ollama is running: ollama serve
echo.
call .venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
