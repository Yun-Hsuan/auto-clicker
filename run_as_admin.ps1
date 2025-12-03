# ============================================
# Orange Clicker - Run as Administrator
# ============================================
# This script ensures the application runs with administrator privileges
# which may be required for certain game windows that use Raw Input/DirectInput

#Requires -Version 5.1

# Check for administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[INFO] Requesting administrator privileges..." -ForegroundColor Yellow
    # Re-run this script with administrator privileges
    try {
        Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
        exit 0
    } catch {
        Write-Host "[ERROR] Failed to elevate privileges: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host "[INFO] Running with administrator privileges" -ForegroundColor Green

# Navigate to script directory
try {
    Set-Location -Path $PSScriptRoot -ErrorAction Stop
} catch {
    Write-Host "[ERROR] Failed to change to script directory: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment if it exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Cyan
    try {
        & ".venv\Scripts\Activate.ps1"
    } catch {
        Write-Host "[WARNING] Failed to activate virtual environment: $_" -ForegroundColor Yellow
        Write-Host "[INFO] Continuing with system Python..." -ForegroundColor Yellow
    }
} else {
    Write-Host "[INFO] No virtual environment found, using system Python" -ForegroundColor Cyan
}

# Check if Python is available
$pythonCmd = Get-Command py -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[ERROR] Python is not found in PATH. Please ensure Python is installed." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if main.py exists
if (-not (Test-Path "main.py")) {
    Write-Host "[ERROR] main.py not found in current directory" -ForegroundColor Red
    Write-Host "[INFO] Current directory: $PWD" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Run the application
Write-Host "[INFO] Starting Orange Clicker..." -ForegroundColor Cyan
Write-Host ""

try {
    py main.py
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -ne 0) {
        Write-Host ""
        Write-Host "[ERROR] Application exited with code $exitCode" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Press any key to exit..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
    exit $exitCode
} catch {
    Write-Host "[ERROR] Failed to start application: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

