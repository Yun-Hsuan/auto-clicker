@echo off
REM ============================================
REM Orange Clicker - Run as Administrator
REM ============================================
REM This script ensures the application runs with administrator privileges
REM which may be required for certain game windows that use Raw Input/DirectInput

setlocal EnableDelayedExpansion

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] Running with administrator privileges
) else (
    echo [INFO] Requesting administrator privileges...
    REM Re-run this script with administrator privileges
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

REM Navigate to script directory
cd /d "%~dp0"
if %errorLevel% neq 0 (
    echo [ERROR] Failed to change to script directory
    pause
    exit /b 1
)

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call ".venv\Scripts\activate.bat"
    if %errorLevel% neq 0 (
        echo [WARNING] Failed to activate virtual environment, continuing anyway...
    )
) else (
    echo [INFO] No virtual environment found, using system Python
)

REM Check if Python is available
where py >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python is not found in PATH. Please ensure Python is installed.
    pause
    exit /b 1
)

REM Check if main.py exists
if not exist "main.py" (
    echo [ERROR] main.py not found in current directory
    echo [INFO] Current directory: %CD%
    pause
    exit /b 1
)

REM Run the application
echo [INFO] Starting Orange Clicker...
echo.
py main.py

REM Capture exit code
set EXIT_CODE=%errorLevel%

REM Pause to view output if there was an error
if %EXIT_CODE% neq 0 (
    echo.
    echo [ERROR] Application exited with code %EXIT_CODE%
    pause
)

endlocal
exit /b %EXIT_CODE%

