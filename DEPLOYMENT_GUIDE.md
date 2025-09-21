# 🚀 SUARA Deployment Guide

Complete deployment guide for Team Codezilla's AI-powered customer service agent.

## 📋 Prerequisites

### Required Software
1. **AWS CLI** configured with appropriate permissions
2. **Node.js** (v18+) and **npm** installed
3. **Python** (3.11+) and **pip** installed
4. **AWS CDK** installed globally: `npm install -g aws-cdk`

### AWS Permissions Required
Your AWS credentials need access to:
- **CloudFormation** (full access)
- **S3** (full access)
- **Lambda** (full access)
- **API Gateway** (full access)
- **IAM** (full access)
- **Rekognition** (full access)
- **Bedrock** (full access)
- **Polly** (full access)
- **Transcribe** (full access)
- **CloudFront** (full access)

## 🎯 Quick Deployment Options

### Option 1: One-Command Deployment (Recommended)
```bash
# Windows
deploy-full.bat

# Linux/macOS
chmod +x deploy.sh
./deploy.sh
```

This automated script will:
1. Setup Python virtual environment
2. Install all dependencies (Python + Node.js)
3. Build the Next.js frontend
4. Deploy all 4 CDK stacks in correct order
5. Output the final application URL

### Option 2: GitHub Actions CI/CD
```bash
# 1. Push code to GitHub repository
git add .
git commit -m "Initial deployment"
git push origin main

# 2. Configure GitHub Secrets (in repository settings):
# - AWS_ACCESS_KEY_ID: Your AWS access key
# - AWS_SECRET_ACCESS_KEY: Your AWS secret key
# - AWS_REGION: us-east-1 (or your preferred region)

# 3. GitHub Actions will automatically deploy on push to main
```

### Option 3: Manual Step-by-Step
```bash
# 1. Setup environment
python setup.py
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# 2. Install dependencies
pip install -r requirements.txt
cd web_client
npm install
cd ..

# 3. Bootstrap CDK (first time only)
cdk bootstrap

# 4. Build frontend
cd web_client
npm run build
cd ..

# 5. Deploy stacks in order
cdk deploy CustomerServiceCore --require-approval never
cdk deploy CustomerServiceML --require-approval never
cdk deploy CustomerServiceApi --require-approval never
cdk deploy CustomerServiceWeb --require-approval never
```

## 🏗️ Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CoreStack     │    │    MLStack      │    │   ApiStack      │
│                 │    │                 │    │                 │
│ • S3 Buckets    │───▶│ • Rekognition   │───▶│ • API Gateway   │
│ • IAM Roles     │    │ • Bedrock KB    │    │ • 6 Lambda Fns  │
│ • Security      │    │ • Custom Labels │    │ • CORS Config   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   WebStack      │
                                               │                 │
                                               │ • CloudFront    │
                                               │ • S3 Hosting    │
                                               │ • Next.js App   │
                                               └─────────────────┘
```

## ⚙️ Post-Deployment Configuration

### 1. 🔍 Rekognition Custom Labels (Optional Enhancement)

The system works without custom labels, but you can enhance image recognition:

```bash
# 1. Prepare training data
mkdir training_data
# Add 50+ router images in folders:
# - training_data/router_normal/
# - training_data/router_no_service/
# - training_data/router_cable_issue/

# 2. Upload to S3
aws s3 sync training_data/ s3://your-storage-bucket/rekognition-training/

# 3. Create custom labels project via AWS Console
# - Go to Amazon Rekognition → Custom Labels
# - Create project: "unifi-router-detection"
# - Create dataset with uploaded images
# - Start training (cost: $1-10, duration: 1-24 hours)

# 4. Update Lambda environment variable
aws lambda update-function-configuration \
  --function-name CustomerServiceApi-ImageAnalysisHandler \
  --environment Variables='{
    "STORAGE_BUCKET":"your-bucket-name",
    "REKOGNITION_PROJECT_ARN":"arn:aws:rekognition:region:account:project/unifi-router-detection/version/1"
  }'
```

### 2. 🧠 Bedrock Knowledge Base Setup

```bash
# 1. Create Bedrock Knowledge Base (via AWS Console)
# - Go to Amazon Bedrock → Knowledge bases
# - Create knowledge base: "unifi-troubleshooting"
# - Use OpenSearch Serverless as vector store
# - Upload documents from knowledge-base-example/

# 2. Update Knowledge Base ID in code
# Edit lambda_functions/bedrock_handler/bedrock_handler.py
# Change KNOWLEDGE_BASE_ID = "HU9V8VBZBI" to your KB ID

# 3. Redeploy API stack
cdk deploy CustomerServiceApi
```

### 3. 🔧 Action Executor Integration

Replace mock functions with real API integrations:

```python
# Edit lambda_functions/action_executor/action_executor.py

def restart_stb(customer_id, device_id):
    # Replace with actual STB restart API call
    response = requests.post(
        "https://your-provisioning-api.com/restart",
        headers={"Authorization": "Bearer YOUR_TOKEN"},
        json={"customer_id": customer_id, "device_id": device_id}
    )
    return response.json()

def reprovision_service(customer_id):
    # Replace with actual provisioning API call
    response = requests.post(
        "https://your-provisioning-api.com/reprovision",
        headers={"Authorization": "Bearer YOUR_TOKEN"},
        json={"customer_id": customer_id}
    )
    return response.json()
```

## 🧪 Testing Your Deployment

### 1. Automated Smoke Test
```bash
# Get API URL from CloudFormation
API_URL=$(aws cloudformation describe-stacks \
  --stack-name CustomerServiceApi \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)

# Run comprehensive smoke test
python scripts/smoke_test.py $API_URL
```

### 2. Manual Testing Scenarios

#### Test 1: Text-Only Query
```bash
curl -X POST $API_URL/upload \
  -H "Content-Type: application/json" \
  -d '{"text": "My Unifi TV shows no service error"}'
```

#### Test 2: Image Upload
```bash
# Convert image to base64
base64 -i sample_data/router_image.jpg > image_b64.txt

# Upload image
curl -X POST $API_URL/upload \
  -H "Content-Type: application/json" \
  -d "{\"image\": \"$(cat image_b64.txt)\"}"
```

#### Test 3: Frontend Application
1. Get CloudFront URL from WebStack outputs
2. Open in browser
3. Test all input methods: text, voice, image
4. Verify TTS audio playback
5. Test action button execution

### 3. Performance Benchmarks
```bash
# Load test with Apache Bench
ab -n 100 -c 10 -H "Content-Type: application/json" \
  -p test_payload.json $API_URL/troubleshoot

# Expected performance:
# - API Response: < 2 seconds
# - Bedrock Processing: < 5 seconds
# - TTS Generation: < 3 seconds
# - Total End-to-End: < 10 seconds
```

## 🔧 Troubleshooting Deployment Issues

### Common Deployment Failures

#### 1. CDK Bootstrap Issues
```bash
# Error: "Need to perform AWS CDK bootstrap"
cdk bootstrap aws://ACCOUNT-ID/REGION

# Error: "Bootstrap version mismatch"
cdk bootstrap --force

# Verify bootstrap
aws cloudformation describe-stacks --stack-name CDKToolkit
```

#### 2. Permission Errors
```bash
# Check current AWS identity
aws sts get-caller-identity

# Test required permissions
aws s3 ls  # S3 access
aws lambda list-functions  # Lambda access
aws apigateway get-rest-apis  # API Gateway access

# Common fix: Attach AdministratorAccess policy (for development)
```

#### 3. Node.js/Python Version Issues
```bash
# Check versions
node --version  # Should be 18+
python --version  # Should be 3.11+

# Update Node.js (Windows)
# Download from nodejs.org

# Update Python (Windows)
# Download from python.org

# Linux/macOS
nvm install 18
pyenv install 3.11
```

#### 4. Frontend Build Failures
```bash
# Clear cache and rebuild
cd web_client
rm -rf node_modules .next package-lock.json
npm install
npm run build

# Check for missing API file
ls src/lib/api.ts  # Should exist

# Verify environment variables
cat .env.local
```

#### 5. Lambda Deployment Size Issues
```bash
# Error: "Unzipped size must be smaller than 262144000 bytes"
# Solution: Use Lambda layers for large dependencies

# Check current package size
cd lambda_functions/bedrock_handler
du -sh .

# Optimize by removing unnecessary files
rm -rf __pycache__ *.pyc tests/
```

### Monitoring Deployment Health

#### CloudWatch Dashboards
```bash
# Create monitoring dashboard
aws cloudwatch put-dashboard \
  --dashboard-name "SUARA-Monitoring" \
  --dashboard-body file://monitoring-dashboard.json
```

#### Key Metrics to Monitor
- **Lambda Duration**: < 30 seconds average
- **API Gateway Latency**: < 2 seconds
- **Error Rate**: < 1%
- **Bedrock Throttling**: Should be 0
- **S3 Request Rate**: Monitor for spikes

#### Set Up Alarms
```bash
# High error rate alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "SUARA-High-Error-Rate" \
  --alarm-description "Alert when error rate > 5%" \
  --metric-name "4XXError" \
  --namespace "AWS/ApiGateway" \
  --statistic "Sum" \
  --period 300 \
  --threshold 5 \
  --comparison-operator "GreaterThanThreshold"
```

## 🌍 Production Deployment Considerations

### Security Enhancements
```bash
# 1. Enable WAF on API Gateway
aws wafv2 create-web-acl \
  --name "SUARA-WAF" \
  --scope "REGIONAL"

# 2. Use VPC endpoints for AWS services
# 3. Implement API key authentication
# 4. Enable CloudTrail logging
# 5. Set up AWS Config for compliance
```

### Performance Optimizations
```bash
# 1. Enable Lambda provisioned concurrency
aws lambda put-provisioned-concurrency-config \
  --function-name CustomerServiceApi-BedrockHandler \
  --provisioned-concurrency-config ProvisionedConcurrencyConfig=10

# 2. Enable API Gateway caching
# 3. Use CloudFront for global distribution
# 4. Implement database caching for knowledge base
```

### Cost Management
```bash
# 1. Set up billing alerts
aws budgets create-budget \
  --account-id ACCOUNT-ID \
  --budget file://budget-config.json

# 2. Enable S3 Intelligent Tiering
# 3. Use Spot instances for batch processing
# 4. Implement lifecycle policies
```

## 🗑️ Cleanup

### Remove All Resources
```bash
# Destroy all stacks (in reverse order)
cdk destroy CustomerServiceWeb --force
cdk destroy CustomerServiceApi --force
cdk destroy CustomerServiceML --force
cdk destroy CustomerServiceCore --force

# Clean up CDK bootstrap (optional)
aws cloudformation delete-stack --stack-name CDKToolkit
```

### Partial Cleanup (Keep Infrastructure)
```bash
# Only remove web stack for frontend updates
cdk destroy CustomerServiceWeb

# Redeploy with updates
cdk deploy CustomerServiceWeb
```

---

## 📞 Support

For deployment issues:
1. Check CloudWatch logs for detailed error messages
2. Review this troubleshooting guide
3. Verify all prerequisites are met
4. Test with minimal configuration first

**🎉 Successful deployment? Your SUARA AI agent is ready to revolutionize customer service!**