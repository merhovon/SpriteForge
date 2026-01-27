@echo off
REM Windows batch script to run SpriteForge
REM Usage: run.bat [optional_image_path]

echo Starting SpriteForge...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from python.org
    pause
    exit /b 1
)

REM Check if spriteforge is installed
python -c "import spriteforge" >nul 2>&1
if errorlevel 1 (
    echo SpriteForge not installed. Installing...
    pip install -e .
    if errorlevel 1 (
        echo Error: Failed to install SpriteForge
        echo Try running: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

REM Run spriteforge
if "%1"=="" (
    python -m spriteforge.app
) else (
    python -m spriteforge.app %1
)

if errorlevel 1 (
    echo.
    echo Error occurred while running SpriteForge
    pause
)
