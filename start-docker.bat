@echo off
echo Starting Unraid Scripts Docker Application...
echo.

echo Checking Docker status...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not running. Please start Docker Desktop first.
    echo Then run this script again.
    pause
    exit /b 1
)

echo Docker is running. Building and starting the application...
echo.

echo Building Docker image...
docker build -t my-unraid-scripts .

if %errorlevel% neq 0 (
    echo Failed to build Docker image.
    pause
    exit /b 1
)

echo.
echo Starting application with docker-compose...
docker-compose up --build

echo.
echo Application stopped. Press any key to exit.
pause
