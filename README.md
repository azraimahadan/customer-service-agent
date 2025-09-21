# SUARA - AI-Powered Customer Service Agent

**Team Codezilla's Great AI Hackathon Submission**

SUARA is an intelligent customer service agent that provides multimodal troubleshooting for Unifi TV issues. It accepts text, voice, and image inputs to deliver personalized solutions using advanced AWS AI services.

## 🏗️ Architecture

- **Frontend**: Next.js 14 React web application with TypeScript
- **Backend**: 6 AWS Lambda functions orchestrated via API Gateway
- **AI Services**: Amazon Bedrock (GPT), Transcribe, Rekognition, Polly
- **Storage**: S3 for session data, audio responses, and audit trails
- **Infrastructure**: AWS CDK (Python) for Infrastructure as Code
- **Deployment**: CloudFront + S3 for global CDN distribution

## 🚀 Quick Start

### Prerequisites
- AWS CLI configured with appropriate permissions
- Node.js 18+ and npm installed
- Python 3.11+ and pip installed
- AWS CDK CLI: `npm install -g aws-cdk`

### One-Command Deployment
```bash
# Windows
deploy-full.bat

# Linux/macOS
./deploy.sh
```

### Manual Setup
```bash
# 1. Setup Python environment
python setup.py
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# 2. Install dependencies
pip install -r requirements.txt
cd web_client && npm install && cd ..

# 3. Deploy infrastructure
cdk bootstrap
cdk deploy --all --require-approval never
```

## 📁 Project Structure

```
customer-service-agent/
├── 🔧 lambda_functions/          # 6 AWS Lambda functions
│   ├── upload_handler/           # File upload & session management
│   ├── transcribe_handler/       # Audio → text conversion
│   ├── image_analysis_handler/   # Image analysis via Rekognition
│   ├── bedrock_handler/          # AI troubleshooting with GPT
│   ├── action_executor/          # Execute customer actions
│   └── audio_proxy/              # TTS audio streaming
├── 🏗️ stacks/                    # CDK Infrastructure as Code
│   ├── core_stack.py            # S3, IAM, base resources
│   ├── ml_stack.py              # Rekognition, Bedrock setup
│   ├── api_stack.py             # API Gateway + Lambda integration
│   ├── web_stack.py             # CloudFront + S3 hosting
│   └── cicd_stack.py            # CI/CD pipeline (optional)
├── 🌐 web_client/               # Next.js 14 Frontend
│   ├── src/app/                 # App Router pages
│   ├── src/components/          # React components
│   ├── src/lib/                 # API client & utilities
│   └── src/types/               # TypeScript definitions
├── 📊 knowledge-base-example/    # Sample troubleshooting data
├── 🧪 tests/                    # Unit & integration tests
├── 📜 scripts/                  # Deployment & utility scripts
├── 🎯 sample_data/              # Test images & audio files
├── ⚙️ .github/workflows/        # GitHub Actions CI/CD
└── 📋 Documentation files
```

## 🧩 System Components

### 🏗️ CDK Infrastructure Stacks
- **CoreStack**: S3 storage, IAM roles, security policies
- **MLStack**: Rekognition custom labels, Bedrock knowledge base
- **ApiStack**: API Gateway, 6 Lambda functions, CORS configuration
- **WebStack**: CloudFront distribution, S3 static hosting
- **CICDStack**: CodePipeline for automated deployments (optional)

### ⚡ Lambda Functions (Python 3.11)
- **upload_handler**: Multipart file upload, session management
- **transcribe_handler**: Amazon Transcribe integration
- **image_analysis_handler**: Rekognition labels + custom detection
- **bedrock_handler**: GPT-powered troubleshooting with knowledge base
- **action_executor**: Execute customer service actions (restart, provision)
- **audio_proxy**: Stream Polly TTS responses

### 🌐 Frontend (Next.js 14 + TypeScript)
- **Responsive UI**: Mobile-first design with Tailwind CSS
- **Multimodal Input**: Text, voice recording, image capture
- **Real-time Processing**: Step-by-step progress indicators
- **Action Buttons**: Execute suggested troubleshooting actions
- **Audio Playback**: TTS responses with streaming support

## ⚠️ Post-Deployment Configuration

### 1. 🔍 Rekognition Custom Labels (Optional)
```bash
# Upload training images to S3
aws s3 cp sample_data/router_image.jpg s3://your-bucket/training/

# Train custom model via AWS Console
# - Create dataset with router images
# - Label: router_normal, router_no_service, router_cable_issue
# - Training cost: ~$1-10, takes 1-24 hours
```

### 2. 🧠 Bedrock Knowledge Base
```bash
# Knowledge base ID is hardcoded: HU9V8VBZBI
# Update in bedrock_handler.py if using different KB
# Upload knowledge-base-example/*.json to your KB
```

### 3. 🔧 Action Executor Integration
```python
# Update lambda_functions/action_executor/action_executor.py
# Replace mock functions with real API calls:
# - restart_stb() → actual STB restart API
# - reprovision_service() → provisioning system API
# - check_subscription() → billing system API
```

## 🧪 Testing

### Unit Tests
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# Run Python tests
pytest tests/ -v

# Run frontend tests
cd web_client
npm test
```

### Integration Testing
```bash
# Get API URL from deployment
API_URL=$(aws cloudformation describe-stacks \
  --stack-name CustomerServiceApi \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)

# Run smoke test
python scripts/smoke_test.py $API_URL

# Test with sample data
curl -X POST $API_URL/upload \
  -H "Content-Type: application/json" \
  -d '{"text": "My TV shows no service error"}'
```

### Manual Testing Scenarios
1. **Text Input**: "My Unifi TV is not working"
2. **Image Upload**: Upload router image from sample_data/
3. **Voice Input**: Record audio describing the issue
4. **Action Execution**: Click suggested action buttons

## 👨💻 Development

### Local Development Setup
```bash
# Backend development
python setup.py
venv\Scripts\activate
pip install pytest black flake8 mypy

# Frontend development
cd web_client
npm install
npm run dev  # Starts on http://localhost:3000
```

### Code Quality
```bash
# Python linting & formatting
flake8 lambda_functions/ stacks/
black lambda_functions/ stacks/
mypy lambda_functions/

# TypeScript checking
cd web_client
npm run lint
npm run type-check
```

### Incremental Deployment
```bash
# Deploy specific stacks
cdk deploy CustomerServiceCore    # Base infrastructure
cdk deploy CustomerServiceML      # AI services
cdk deploy CustomerServiceApi     # Backend APIs
cdk deploy CustomerServiceWeb     # Frontend

# Deploy with hotswap for faster Lambda updates
cdk deploy CustomerServiceApi --hotswap
```

### Environment Variables
```bash
# Backend (set in CDK stacks)
STORAGE_BUCKET=customer-service-storage-*
REKOGNITION_PROJECT_ARN=arn:aws:rekognition:*
BEDROCK_AGENT_ID=*
KNOWLEDGE_BASE_ID=HU9V8VBZBI

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://your-api.amazonaws.com/prod
NEXT_PUBLIC_DEV_MODE=true
```

## 🔒 Security Features

- **IAM Least Privilege**: Function-specific permissions only
- **Input Validation**: Request validators on all API endpoints
- **CORS Configuration**: Controlled cross-origin access
- **PII Protection**: Automatic redaction in CloudWatch logs
- **Rate Limiting**: API Gateway throttling (1000 req/sec)
- **Encryption**: S3 server-side encryption, HTTPS everywhere
- **Session Isolation**: UUID-based session management

## 💰 Cost Optimization

### Development Environment
- **S3 Lifecycle**: 30-day object expiration
- **Bedrock Model**: GPT-OSS-120B (cost-effective)
- **Lambda**: On-demand pricing, 30-60s timeouts
- **CloudWatch**: 7-day log retention
- **API Gateway**: Pay-per-request model

### Production Recommendations
- **Reserved Capacity**: For consistent workloads
- **CloudFront**: Global edge caching
- **S3 Intelligent Tiering**: Automatic cost optimization
- **Lambda Provisioned Concurrency**: For low latency
- **Extended Retention**: 90+ days for audit compliance

## 🔧 Troubleshooting

### Common Issues & Solutions

#### 1. **Deployment Failures**
```bash
# CDK bootstrap issues
cdk bootstrap --force
aws sts get-caller-identity  # Verify credentials

# Permission errors
# Ensure your AWS user/role has:
# - CloudFormation full access
# - S3, Lambda, API Gateway, IAM permissions
# - Bedrock, Rekognition, Transcribe, Polly access
```

#### 2. **Frontend Build Issues**
```bash
# Module resolution errors
cd web_client
rm -rf node_modules .next package-lock.json
npm install
npm run build

# API URL not found
# Update .env.local with correct API Gateway URL
echo "NEXT_PUBLIC_API_URL=https://your-api.amazonaws.com/prod" > .env.local
```

#### 3. **Lambda Function Errors**
```bash
# Check CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/CustomerService"

# Common fixes:
# - Increase timeout (currently 30-60s)
# - Check environment variables
# - Verify S3 bucket permissions
# - Ensure Bedrock model access is enabled
```

#### 4. **API Gateway Issues**
```bash
# CORS errors
# Verify CORS is enabled for all methods
# Check preflight OPTIONS requests

# 403/404 errors
# Ensure API is deployed to 'prod' stage
# Check resource paths match frontend calls
```

#### 5. **AI Service Issues**
```bash
# Bedrock access denied
# Enable model access in Bedrock console
# Verify region supports GPT models

# Rekognition custom labels
# Ensure model is trained and running
# Check project ARN in environment variables

# Transcribe failures
# Verify audio format (WAV supported)
# Check file size limits (< 10MB)
```

### Debug Commands
```bash
# Check deployment status
aws cloudformation describe-stacks --stack-name CustomerServiceApi

# Test API endpoints
curl -X POST https://your-api.amazonaws.com/prod/upload \
  -H "Content-Type: application/json" \
  -d '{"text": "test message"}'

# Monitor Lambda logs
aws logs tail /aws/lambda/CustomerServiceApi-BedrockHandler --follow
```

### Performance Monitoring
- **CloudWatch Metrics**: Lambda duration, API Gateway latency
- **X-Ray Tracing**: End-to-end request tracing (enable in production)
- **Cost Explorer**: Monitor AWS service costs
- **CloudWatch Alarms**: Set up alerts for errors/high latency

## 🎯 Key Features

### Multimodal Input Support
- **📝 Text Chat**: Direct text input for quick queries
- **🎤 Voice Recording**: Browser-based audio capture and transcription
- **📸 Image Upload**: Visual troubleshooting with router/device images
- **🔄 Mixed Mode**: Combine text, voice, and images in single session

### AI-Powered Troubleshooting
- **🧠 GPT Integration**: Advanced language understanding via Amazon Bedrock
- **📚 Knowledge Base**: Semantic search through troubleshooting procedures
- **🔍 Image Analysis**: Automatic detection of device states and error messages
- **🎯 Contextual Responses**: Adaptive solutions based on query complexity

### Interactive Experience
- **⚡ Real-time Processing**: Step-by-step progress indicators
- **🔊 Text-to-Speech**: Audio responses via Amazon Polly
- **🎬 Action Buttons**: One-click execution of suggested solutions
- **📱 Responsive Design**: Works on desktop, tablet, and mobile

### Enterprise Ready
- **🔐 Secure**: IAM-based access control, encrypted storage
- **📊 Auditable**: Complete session logging and audit trails
- **⚡ Scalable**: Serverless architecture handles traffic spikes
- **🌍 Global**: CloudFront CDN for worldwide deployment

## 🏆 Team Codezilla

Built for the Great AI Hackathon - showcasing the power of AWS AI services in creating intelligent, multimodal customer service experiences.

### Technology Stack
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: AWS Lambda (Python 3.11), API Gateway
- **AI Services**: Bedrock GPT, Transcribe, Rekognition, Polly
- **Infrastructure**: AWS CDK, CloudFormation
- **Storage**: S3, CloudFront
- **CI/CD**: GitHub Actions, AWS CodePipeline

---

**🚀 Ready to deploy? Run `deploy-full.bat` and experience the future of AI-powered customer service!**