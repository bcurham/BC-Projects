@echo off
REM Quick Start Script for Automated Test Script Generator (Windows)
REM This script helps you set up and run the application quickly

echo ==========================================
echo Automated Test Script Generator
echo Quick Start Setup (Windows)
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python 3 is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
echo [OK] Dependencies installed
echo.

REM Check if .env file exists
if not exist ".env" (
    echo Setting up environment variables...
    copy .env.example .env
    echo.
    echo WARNING: You need to configure your .env file!
    echo.
    echo Please edit .env and add your Anthropic API key:
    echo   ANTHROPIC_API_KEY=sk-ant-api03-...
    echo.
    pause
    echo.
)

REM Create sample files
if not exist "sample_test_script_template.docx" (
    echo Creating sample files for testing...
    python create_sample_files.py
    echo.
)

echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Starting the application...
echo.
echo Once started, open your browser and go to:
echo   http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
echo ==========================================
echo.

REM Start the Flask application
python app.py
