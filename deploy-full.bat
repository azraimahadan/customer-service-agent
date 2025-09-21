@echo off
echo ========================================
echo   Customer Service Agent Deployment
echo ========================================

echo.
echo Step 1: Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Step 2: Installing Node.js dependencies...
cd web_client
npm install

echo.
echo Step 3: Building Next.js application...
npm run build

echo.
echo Step 4: Going back to root directory...
cd ..

echo.
echo Step 5: Deploying CDK stacks...
echo Deploying Core Stack...
cdk deploy CustomerServiceCore --require-approval never

echo.
echo Deploying ML Stack...
cdk deploy CustomerServiceML --require-approval never

echo.
echo Deploying API Stack...
cdk deploy CustomerServiceApi --require-approval never

echo.
echo Deploying Web Stack...
cdk deploy CustomerServiceWeb --require-approval never

echo.
echo ========================================
echo   Deployment Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Update the API URL in web_client/.env.local
echo 2. Rebuild and redeploy the web client if needed
echo.
pause