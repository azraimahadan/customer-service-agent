# Deployment Guide

## Prerequisites

1. **AWS CLI configured** with appropriate permissions
2. **Node.js** (v16+) and **npm** installed
3. **Python** (3.11+) and **pip** installed
4. **AWS CDK** installed globally: `npm install -g aws-cdk`

## Quick Deployment

### Option 1: Automated Deployment
```bash
# Windows
set YES_DEPLOY=true && deploy.bat

# Linux/Mac
YES_DEPLOY=true ./deploy.sh
```

### Option 2: Step-by-Step Deployment
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Bootstrap CDK (first time only)
cdk bootstrap

# 3. Build web client
cd web_client
npm install
npm run build
cd ..

# 4. Deploy stacks
cdk deploy CustomerServiceCore --require-approval never
cdk deploy CustomerServiceML --require-approval never
cdk deploy CustomerServiceApi --require-approval never
cdk deploy CustomerServiceWeb --require-approval never
```

## Manual Configuration Required

### 1. Rekognition Custom Labels

After deployment, you need to train a custom model:

```bash
# Run the setup script for guidance
python scripts/setup_rekognition.py

# Create project (done by CDK)
# Upload training images to S3
# Create manifest files
# Train model via AWS Console or CLI
```

**Training Steps:**
1. Collect 50+ router images showing different states
2. Label images: `router_normal`, `router_no_service`, `router_cable_issue`
3. Upload to S3 with proper folder structure
4. Create training/testing manifest files
5. Start training job (takes 1-24 hours, costs $1-10)

### 2. Bedrock Agent Configuration

1. **Create Bedrock Agent** via AWS Console:
   - Go to Amazon Bedrock → Agents
   - Create new agent with name "unifi-troubleshooting-agent"
   - Configure with Claude model
   - Add knowledge base with troubleshooting procedures

2. **Update Lambda Environment**:
   - Get the Agent ID from console
   - Update `BEDROCK_AGENT_ID` in API stack
   - Redeploy: `cdk deploy CustomerServiceApi`

### 3. Internal API Integration

Update `lambda_functions/action_executor/action_executor.py`:
- Replace mock functions with real API calls
- Add authentication/authorization
- Configure endpoint URLs

## Testing

### Smoke Test
```bash
# Get API URL from CloudFormation outputs
API_URL=$(aws cloudformation describe-stacks \
  --stack-name CustomerServiceApi \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)

# Run smoke test
python scripts/smoke_test.py $API_URL
```

### Unit Tests
```bash
pytest tests/
```

## Production Deployment

For production, consider these additional configurations:

### Security Enhancements
- Enable WAF on API Gateway
- Use VPC endpoints for AWS services
- Implement API key authentication
- Add rate limiting
- Enable CloudTrail logging

### Performance Optimizations
- Use Lambda provisioned concurrency
- Enable API Gateway caching
- Optimize Lambda memory allocation
- Use CloudFront for web client

### Monitoring
- Set up CloudWatch alarms
- Enable X-Ray tracing
- Configure log aggregation
- Set up cost monitoring

## Cost Optimization

### Development Environment
- S3 lifecycle policies (30-day retention)
- Small Bedrock model (Claude Haiku)
- Limited CloudWatch log retention
- No provisioned concurrency

### Production Environment
- Longer S3 retention for audit
- Larger Bedrock model for accuracy
- Extended log retention
- Provisioned concurrency for performance

## Troubleshooting

### Common Issues

1. **CDK Bootstrap Failed**
   ```bash
   # Ensure AWS credentials are configured
   aws sts get-caller-identity
   
   # Bootstrap with explicit region
   cdk bootstrap aws://ACCOUNT/REGION
   ```

2. **Lambda Deployment Failed**
   ```bash
   # Check Lambda function size limits
   # Ensure all dependencies are in layer
   # Verify IAM permissions
   ```

3. **Rekognition Training Failed**
   ```bash
   # Verify image format (JPEG/PNG)
   # Check manifest file format
   # Ensure minimum 10 images per label
   ```

4. **Bedrock Access Denied**
   ```bash
   # Enable Bedrock model access in console
   # Verify IAM permissions
   # Check region availability
   ```

## Cleanup

To remove all resources:
```bash
cdk destroy CustomerServiceWeb
cdk destroy CustomerServiceApi
cdk destroy CustomerServiceML
cdk destroy CustomerServiceCore
```

**Note**: Some resources like S3 buckets with objects may require manual deletion.