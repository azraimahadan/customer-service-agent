@echo off
echo ====================================
echo Building SUARA Customer Service App
echo ====================================

:: Change to web client directory
cd /d "%~dp0web_client"

echo.
echo [1/4] Installing dependencies...
call npm install

echo.
echo [2/4] Building static export...
call npm run build

:: Check if build was successful
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

:: Go back to root directory
cd /d "%~dp0"

echo.
echo [3/4] Cleaning assets folder...
if exist "assets\web\*" (
    rmdir /s /q "assets\web"
    mkdir "assets\web"
) else (
    if not exist "assets" mkdir "assets"
    if not exist "assets\web" mkdir "assets\web"
)

echo.
echo [4/4] Copying build files...
xcopy "web_client\out\*" "assets\web\" /E /I /Y

:: Check if copy was successful
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Failed to copy files!
    pause
    exit /b 1
)

echo.
echo ====================================
echo Build completed successfully!
echo ====================================
echo.
echo Files copied to: assets\web\
echo You can now serve the static files from the assets\web\ directory
echo.

:: List the files that were copied
echo Contents of assets\web\:
dir "assets\web" /b

echo.
pause