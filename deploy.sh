#!/bin/bash

# Customer Service Agent Deployment Script
set -e

echo "🚀 Customer Service Agent Deployment"
echo "===================================="

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Get AWS account and region
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region)
echo "📍 Deploying to Account: $AWS_ACCOUNT, Region: $AWS_REGION"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Setting up virtual environment..."
    python3 setup.py
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install CDK if not present
if ! command -v cdk &> /dev/null; then
    echo "📦 Installing AWS CDK..."
    npm install -g aws-cdk
fi

# Bootstrap CDK if needed
echo "🔧 Bootstrapping CDK..."
cdk bootstrap

# Build web client
echo "🌐 Building web client..."
cd web_client
if [ ! -d "node_modules" ]; then
    npm install
fi
npm run build
cd ..

# Synthesize CDK app
echo "🔨 Synthesizing CDK app..."
cdk synth

# Deploy stacks
if [ "$YES_DEPLOY" = "true" ]; then
    echo "🚀 Deploying all stacks..."
    
    echo "📦 Deploying Core Stack..."
    cdk deploy CustomerServiceCore --require-approval never
    
    echo "🤖 Deploying ML Stack..."
    cdk deploy CustomerServiceML --require-approval never
    
    echo "⚡ Deploying API Stack..."
    cdk deploy CustomerServiceApi --require-approval never
    
    echo "🌐 Deploying Web Stack..."
    cdk deploy CustomerServiceWeb --require-approval never
    
    echo "✅ Deployment completed!"
    
    # Get API URL
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name CustomerServiceApi \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
        --output text)
    
    echo ""
    echo "🎉 Deployment Summary"
    echo "===================="
    echo "API URL: $API_URL"
    echo ""
    echo "📋 Example curl command:"
    echo "curl -X POST $API_URL/upload \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"image\":\"base64_image_data\",\"audio\":\"base64_audio_data\"}'"
    echo ""
    
    # Run smoke test
    echo "🧪 Running smoke test..."
    python scripts/smoke_test.py "$API_URL"
    
else
    echo ""
    echo "⚠️  Dry run completed. To deploy, run:"
    echo "YES_DEPLOY=true ./deploy.sh"
    echo ""
    echo "Or deploy individual stacks:"
    echo "cdk deploy CustomerServiceCore"
    echo "cdk deploy CustomerServiceML"
    echo "cdk deploy CustomerServiceApi"
    echo "cdk deploy CustomerServiceWeb"
fi

echo ""
echo "📚 Next Steps:"
echo "1. Configure Rekognition Custom Labels with router images"
echo "2. Set up Bedrock Agent with troubleshooting knowledge"
echo "3. Configure internal API endpoints in action_executor"
echo "4. Test with real router images and audio"