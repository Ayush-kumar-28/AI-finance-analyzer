# Finance Tracker - PowerShell Startup Script
# Alternative to batch file with better error handling

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Finance Tracker - Full Stack with FastAPI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Function to start service in new window
function Start-Service {
    param(
        [string]$Name,
        [string]$Path,
        [string]$Command
    )
    
    Write-Host "Starting $Name..." -ForegroundColor Yellow
    
    $FullPath = Join-Path $ProjectDir $Path
    
    if (Test-Path $FullPath) {
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$FullPath'; $Command" -WindowStyle Normal
        Write-Host "✓ $Name started" -ForegroundColor Green
    } else {
        Write-Host "✗ Error: Path not found: $FullPath" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Start ML Service
Write-Host "[1/3] " -NoNewline
if (-not (Start-Service "ML Service" "ml-service" "python main.py")) {
    Write-Host "Failed to start ML Service. Check if Python is installed." -ForegroundColor Red
    pause
    exit 1
}
Start-Sleep -Seconds 3

# Start Backend
Write-Host "[2/3] " -NoNewline
if (-not (Start-Service "Backend" "backend" "npm start")) {
    Write-Host "Failed to start Backend. Check if Node.js is installed." -ForegroundColor Red
    pause
    exit 1
}
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "[3/3] " -NoNewline
if (-not (Start-Service "Frontend" "frontend" "npm start")) {
    Write-Host "Failed to start Frontend. Check if Node.js is installed." -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Application Starting!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "ML Service: " -NoNewline
Write-Host "http://localhost:8000" -ForegroundColor Blue
Write-Host "Backend:    " -NoNewline
Write-Host "http://localhost:5000" -ForegroundColor Blue
Write-Host "Frontend:   " -NoNewline
Write-Host "http://localhost:3000" -ForegroundColor Blue
Write-Host ""
Write-Host "ML Docs:    " -NoNewline
Write-Host "http://localhost:8000/docs" -ForegroundColor Blue
Write-Host ""
Write-Host "All services are starting in separate windows." -ForegroundColor Yellow
Write-Host "Wait 10-15 seconds for all services to be ready." -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
