@echo off
echo Cleaning up old Docker and ngrok files...

if exist Dockerfile (
    del Dockerfile
    echo Deleted Dockerfile
)

if exist docker-compose.yml (
    del docker-compose.yml
    echo Deleted docker-compose.yml
)

if exist .dockerignore (
    del .dockerignore
    echo Deleted .dockerignore
)

if exist run_with_ngrok.py (
    del run_with_ngrok.py
    echo Deleted run_with_ngrok.py
)

if exist NGROK_DEPLOYMENT.md (
    del NGROK_DEPLOYMENT.md
    echo Deleted NGROK_DEPLOYMENT.md
)

if exist kill_port_8000.bat (
    del kill_port_8000.bat
    echo Deleted kill_port_8000.bat
)

if exist START_HERE.txt (
    del START_HERE.txt
    echo Deleted START_HERE.txt
)

echo.
echo ✅ Cleanup complete!
pause
