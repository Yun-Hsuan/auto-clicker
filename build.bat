@echo off
REM ============================================
REM Auto-Clicker - Build Script
REM ============================================
REM This script builds the Auto-Clicker executable using PyInstaller.
REM The resulting executable will request administrator privileges automatically
REM via PyInstaller's --uac-admin option.

setlocal EnableDelayedExpansion

echo ============================================
echo Auto-Clicker - Build Script
echo ============================================
echo.

REM Check if PyInstaller is installed
where pyinstaller >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] PyInstaller is not installed.
    echo [INFO] Please install it with: pip install pyinstaller
    pause
    exit /b 1
)

REM Clean previous builds
echo [INFO] Cleaning previous builds...
if exist "build" (
    rmdir /s /q "build"
    echo [INFO] Removed 'build' directory
)
if exist "dist" (
    rmdir /s /q "dist"
    echo [INFO] Removed 'dist' directory
)
if exist "AutoClicker.spec" (
    del "AutoClicker.spec"
    echo [INFO] Removed old spec file
)
echo.

REM Icon handling (optional)
REM Currently we build without an explicit .ico to avoid Windows batch parsing issues.
REM If you want a custom icon later, add: --icon "path\to\icon.ico" to the pyinstaller command.

REM Build with PyInstaller
echo [INFO] Building executable with PyInstaller...
echo.

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "AutoClicker" ^
    --uac-admin ^
    --icon "frontend\public\assets\icons\orange_clicker_icon_256x256.ico" ^
    --add-data "frontend\public\assets;frontend\public\assets" ^
    --add-data "frontend\i18n;frontend\i18n" ^
    --hidden-import "PySide6.QtCore" ^
    --hidden-import "PySide6.QtGui" ^
    --hidden-import "PySide6.QtWidgets" ^
    --clean ^
    main.py

if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Build failed! Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ============================================
echo Build successful!
echo ============================================
echo.
echo [INFO] Executable location: dist\AutoClicker.exe
echo.
echo [NOTE] The executable will request administrator privileges when launched (--uac-admin).
echo [NOTE] This is required for clicking in game windows that use Raw Input/DirectInput.
echo.
echo [INFO] To test the executable, run: dist\AutoClicker.exe
echo.

pause
endlocal

