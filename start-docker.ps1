# PowerShell script to start Unraid Scripts Docker Application

Write-Host "Starting Unraid Scripts Docker Application..." -ForegroundColor Green
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker status..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "Docker is running." -ForegroundColor Green
} catch {
    Write-Host "Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    Write-Host "Then run this script again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Docker is running. Building and starting the application..." -ForegroundColor Green
Write-Host ""

# Build Docker image
Write-Host "Building Docker image..." -ForegroundColor Yellow
docker build -t my-unraid-scripts .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to build Docker image." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Starting application with docker-compose..." -ForegroundColor Yellow
docker-compose up --build

Write-Host ""
Write-Host "Application stopped. Press Enter to exit." -ForegroundColor Green
Read-Host
