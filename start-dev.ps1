# start-dev.ps1
# This script starts the FastAPI backend and Vue 3 frontend development servers in new windows.

# 1. Start the Backend
Write-Host "Starting FastAPI Backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; uv run uvicorn main:app --reload" -WindowStyle Normal

# 2. Start the Frontend
Write-Host "Starting Vue Frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -WindowStyle Normal

Write-Host "`nDevelopment servers are starting in new windows." -ForegroundColor Yellow
Write-Host "Backend: http://127.0.0.1:8000/docs"
Write-Host "Frontend: http://localhost:5173"
