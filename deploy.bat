@echo off
REM Customer Service Agent Deployment Script for Windows
setlocal enabledelayedexpansion

echo 🚀 Customer Service Agent Deployment
echo ====================================

REM Check if AWS CLI is configured
aws sts get-caller-identity >nul 2>&1
if errorlevel 1 (
    echo ❌ AWS CLI not configured. Please run 'aws configure' first.
    exit /b 1
)

REM Get AWS account and region
for /f "tokens=*" %%i in ('aws sts get-caller-identity --query Account --output text') do set AWS_ACCOUNT=%%i
for /f "tokens=*" %%i in ('aws configure get region') do set AWS_REGION=%%i
echo 📍 Deploying to Account: %AWS_ACCOUNT%, Region: %AWS_REGION%

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo 📦 Setting up virtual environment...
    python setup.py
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install CDK if not present
where cdk >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing AWS CDK...
    npm install -g aws-cdk
)

REM Bootstrap CDK if needed
echo 🔧 Bootstrapping CDK...
cdk bootstrap

REM Build web client
echo 🌐 Building web client...
cd web_client
if not exist "node_modules" (
    npm install
)
npm run build
cd ..

REM Synthesize CDK app
echo 🔨 Synthesizing CDK app...
cdk synth

REM Deploy stacks
if "%YES_DEPLOY%"=="true" (
    echo 🚀 Deploying all stacks...
    
    echo 📦 Deploying Core Stack...
    cdk deploy CustomerServiceCore --require-approval never
    
    echo 🤖 Deploying ML Stack...
    cdk deploy CustomerServiceML --require-approval never
    
    echo ⚡ Deploying API Stack...
    cdk deploy CustomerServiceApi --require-approval never
    
    echo 🌐 Deploying Web Stack...
    cdk deploy CustomerServiceWeb --require-approval never
    
    echo ✅ Deployment completed!
    
    REM Get API URL
    for /f "tokens=*" %%i in ('aws cloudformation describe-stacks --stack-name CustomerServiceApi --query "Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue" --output text') do set API_URL=%%i
    
    echo.
    echo 🎉 Deployment Summary
    echo ====================
    echo API URL: !API_URL!
    echo.
    echo 📋 Example curl command:
    echo curl -X POST !API_URL!/upload ^
    echo   -H "Content-Type: application/json" ^
    echo   -d "{\"image\":\"base64_image_data\",\"audio\":\"base64_audio_data\"}"
    echo.
    
    REM Run smoke test
    echo 🧪 Running smoke test...
    python scripts/smoke_test.py "!API_URL!"
    
) else (
    echo.
    echo ⚠️  Dry run completed. To deploy, run:
    echo set YES_DEPLOY=true ^&^& deploy.bat
    echo.
    echo Or deploy individual stacks:
    echo cdk deploy CustomerServiceCore
    echo cdk deploy CustomerServiceML
    echo cdk deploy CustomerServiceApi
    echo cdk deploy CustomerServiceWeb
)

echo.
echo 📚 Next Steps:
echo 1. Configure Rekognition Custom Labels with router images
echo 2. Set up Bedrock Agent with troubleshooting knowledge
echo 3. Configure internal API endpoints in action_executor
echo 4. Test with real router images and audio