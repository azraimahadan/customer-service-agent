@echo off
echo Committing frontend fixes...

cd web_client

echo Adding all frontend files...
git add .
git add src/lib/api.ts
git add scripts/ensure-api.js
git add .env.local
git add .eslintrc.json

cd ..

echo Adding deployment files...
git add .github/workflows/deploy.yml
git add stacks/web_stack.py
git add *.bat
git add FRONTEND_DEPLOYMENT.md

echo Committing changes...
git commit -m "Fix frontend integration and deployment configuration

- Add missing API client (src/lib/api.ts)
- Add prebuild script to ensure API file exists
- Update GitHub Actions workflow for proper deployment
- Fix CloudFront configuration for SPA routing
- Add comprehensive deployment scripts and documentation"

echo.
echo Frontend fixes committed! Push to trigger deployment:
echo git push origin main
pause