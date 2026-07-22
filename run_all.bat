@echo off
echo ====================================================
echo STARTING DECISION INTELLIGENCE ENGINE (FRONTEND + BACKEND)
echo ====================================================

:: Start backend in a new window
echo Starting FastAPI Backend on port 8000...
start cmd /k "cd backend && python -m uvicorn app.main:app --reload --port 8000"

:: Start frontend in a new window
echo Starting Vite Frontend on port 5173...
start cmd /k "cd aethel-dashboard && npm run dev"

:: Wait a brief second and open browser
timeout /t 3 /nobreak >nul
echo Opening dashboard in browser...
start http://localhost:5173

echo Both servers are launching in background windows. 
echo Press any key to close this launcher.
pause
