@echo off
echo ========================================
echo   Update API URL and Redeploy Frontend
echo ========================================

if "%1"=="" (
    echo Usage: update-api-url.bat [API_GATEWAY_URL]
    echo Example: update-api-url.bat https://abc123.execute-api.us-east-1.amazonaws.com/prod
    pause
    exit /b 1
)

set API_URL=%1

echo.
echo Updating API URL to: %API_URL%

echo # API Configuration > web_client\.env.local
echo NEXT_PUBLIC_API_URL=%API_URL% >> web_client\.env.local
echo. >> web_client\.env.local
echo # Development mode (set to 'true' for local development) >> web_client\.env.local
echo NEXT_PUBLIC_DEV_MODE=false >> web_client\.env.local

echo.
echo Building frontend with new API URL...
cd web_client
npm run build

echo.
echo Redeploying web stack...
cd ..
cdk deploy CustomerServiceWeb --require-approval never

echo.
echo ========================================
echo   Frontend Update Complete!
echo ========================================
pause