@echo off
echo ========================================
echo Finance Tracker - Full Stack with FastAPI
echo ========================================
echo.

REM Get the directory where this batch file is located
set "PROJECT_DIR=%~dp0"

echo [1/4] Starting FastAPI ML Service...
start "ML Service" cmd /k "cd /d "%PROJECT_DIR%ml-service" && python main.py"
timeout /t 5 /nobreak > nul

echo [2/4] Starting Backend API Gateway...
start "Backend" cmd /k "cd /d "%PROJECT_DIR%backend" && npm start"
timeout /t 5 /nobreak > nul

echo [3/4] Starting Frontend React App...
start "Frontend" cmd /k "cd /d "%PROJECT_DIR%frontend" && npm start"

echo.
echo ========================================
echo Application Starting!
echo ========================================
echo.
echo ML Service: http://localhost:8000
echo Backend:    http://localhost:5000
echo Frontend:   http://localhost:3000
echo.
echo ML Docs:    http://localhost:8000/docs
echo.
echo All services are starting in separate windows.
echo Wait 10-15 seconds for all services to be ready.
echo.
echo Press any key to exit this window...
pause > nul
