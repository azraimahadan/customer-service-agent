# Frontend Deployment Guide

## Quick Start

### 1. Full Deployment (First Time)
```bash
# Run the complete deployment script
deploy-full.bat
```

This will:
- Install Python dependencies
- Install Node.js dependencies  
- Build the Next.js frontend
- Deploy all CDK stacks (Core, ML, API, Web)

### 2. Update API URL (After Backend Deployment)
```bash
# Update frontend with actual API Gateway URL
update-api-url.bat https://your-api-gateway-url.amazonaws.com/prod
```

### 3. Local Development
```bash
# Start development server
cd web_client
dev.bat
```

## Manual Steps

### Prerequisites
- Node.js 18+ installed
- AWS CLI configured
- CDK CLI installed (`npm install -g aws-cdk`)

### Build Frontend Only
```bash
cd web_client
npm install
npm run build
```

### Deploy Web Stack Only
```bash
cdk deploy CustomerServiceWeb
```

## Configuration

### Environment Variables
Edit `web_client/.env.local`:
```
NEXT_PUBLIC_API_URL=https://your-api-gateway-url.amazonaws.com/prod
NEXT_PUBLIC_DEV_MODE=false
```

### API Endpoints
The frontend expects these API endpoints:
- `POST /upload` - Upload files
- `POST /transcribe` - Transcribe audio
- `POST /analyze-image` - Analyze images
- `POST /troubleshoot` - Get troubleshooting response
- `POST /execute-action` - Execute actions

## Troubleshooting

### Build Errors
1. **Module not found '@/lib/api'** - Fixed by creating the API client
2. **ESLint errors** - Fixed by updating ESLint config
3. **Missing dependencies** - Run `npm install`

### Deployment Issues
1. **CDK errors** - Ensure AWS credentials are configured
2. **S3 bucket conflicts** - Bucket names must be globally unique
3. **API URL not working** - Update the environment variable and rebuild

### Development Issues
1. **CORS errors** - API Gateway needs proper CORS configuration
2. **404 errors** - Check API Gateway deployment stage
3. **Authentication errors** - Verify AWS permissions

## Architecture

```
Frontend (Next.js) → API Gateway → Lambda Functions → AWS Services
     ↓
   S3 + CloudFront
```

The frontend is deployed as a static site to S3 with CloudFront distribution for global CDN.

## Files Created/Fixed

1. `src/lib/api.ts` - API client for backend communication
2. `.env.local` - Environment configuration
3. `.eslintrc.json` - ESLint configuration
4. `build.bat` - Build script
5. `dev.bat` - Development server script
6. `deploy-full.bat` - Complete deployment script
7. `update-api-url.bat` - API URL update script

## Next Steps

1. Deploy the backend infrastructure first
2. Get the API Gateway URL from CDK outputs
3. Update the frontend configuration
4. Test the complete application
5. Monitor CloudWatch logs for any issues