@echo off
echo Finding process using port 8000...
echo.

FOR /F "tokens=5" %%P IN ('netstat -aon ^| findstr :8000') DO (
    echo Found process ID: %%P
    echo Killing process...
    taskkill /PID %%P /F
)

echo.
echo Done! Port 8000 should now be free.
echo You can now run: python run_with_ngrok.py
pause
