@echo off
echo ========================================
echo   Deployment Readiness Check
echo ========================================

echo.
echo Checking Node.js...
node --version
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)

echo.
echo Checking npm...
npm --version
if %errorlevel% neq 0 (
    echo ERROR: npm not found
    pause
    exit /b 1
)

echo.
echo Checking AWS CLI...
aws --version
if %errorlevel% neq 0 (
    echo ERROR: AWS CLI not found. Please install and configure AWS CLI
    pause
    exit /b 1
)

echo.
echo Checking CDK...
cdk --version
if %errorlevel% neq 0 (
    echo ERROR: CDK not found. Please install: npm install -g aws-cdk
    pause
    exit /b 1
)

echo.
echo Checking Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo.
echo Checking if frontend builds successfully...
cd web_client
npm run build > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Frontend build failed
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo ========================================
echo   All checks passed! Ready to deploy.
echo ========================================
echo.
echo Run: deploy-full.bat
echo.
pause