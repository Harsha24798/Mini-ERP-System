@echo off
REM Activation script for Windows Command Prompt
echo Activating virtual environment...
cd backend
call venv\Scripts\activate.bat
echo.
echo Virtual environment activated!
echo.
echo Available commands:
echo   flask run              - Run development server
echo   flask db upgrade       - Apply database migrations
echo   pytest                 - Run tests
echo   python app.py          - Run app directly
echo.
