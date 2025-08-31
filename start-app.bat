@echo off
echo Starting AI-Powered Journal App...
echo.

REM Start Backend Server
echo Starting Flask backend server...
cd /d "%~dp0backend"
call venv\Scripts\activate.bat
start /B python app.py

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start Frontend Server
echo Starting React frontend server...
cd /d "%~dp0frontend"
start /B npm run dev

echo.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Press any key to stop servers...
pause >nul

REM Kill the background processes (basic cleanup)
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
echo Servers stopped.
