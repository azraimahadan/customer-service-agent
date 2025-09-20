# Customer Service Agent - Unifi TV Troubleshooting

A deployable prototype that accepts voice and image inputs to troubleshoot Unifi TV issues using AWS AI services.

## Architecture

- **Frontend**: React web client for image/audio capture
- **Backend**: AWS Lambda functions orchestrated via API Gateway
- **AI Services**: Transcribe, Rekognition, Bedrock Agent, Polly
- **Storage**: S3 for persistence and audit trails
- **Infrastructure**: AWS CDK (Python) for IaC

## Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd customer-service-agent

# Setup virtual environment and dependencies
python setup.py

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Unix/Linux/macOS:
source venv/bin/activate

# Deploy to AWS
./deploy.sh        # Unix/Linux/macOS
# or
deploy.bat         # Windows
```

## Project Structure

```
customer-service-agent/
├── lambda_functions/          # AWS Lambda function code
│   ├── upload_handler/        # Receives image/audio uploads
│   ├── transcribe_handler/    # Speech-to-text conversion
│   ├── image_analysis_handler/# Rekognition analysis
│   ├── bedrock_handler/       # AI troubleshooting
│   └── action_executor/       # Execute remediation actions
├── stacks/                    # CDK infrastructure code
│   ├── core_stack.py         # S3 buckets, IAM roles
│   ├── ml_stack.py           # Rekognition, Bedrock
│   ├── api_stack.py          # API Gateway, Lambda
│   └── web_stack.py          # Static web hosting
├── web_client/               # React frontend
│   ├── src/                  # React components
│   └── public/               # Static assets
├── tests/                    # Unit tests
├── scripts/                  # Utility scripts
├── sample_data/              # Test data
├── app.py                    # CDK app entry point
├── requirements.txt          # Python dependencies
└── setup.py                  # Environment setup script
```

## Components

### CDK Stacks
- **CoreStack**: S3 buckets, IAM roles
- **MLStack**: Rekognition project, Bedrock agent
- **ApiStack**: API Gateway, Lambda functions
- **WebStack**: Static web hosting

### Lambda Functions
- `upload_handler`: Receives image/audio uploads
- `transcribe_handler`: Speech-to-text conversion
- `image_analysis_handler`: Rekognition analysis
- `bedrock_handler`: AI troubleshooting orchestration
- `action_executor`: Execute remediation actions

### Web Client
- React app for capturing image/audio
- Sends to API Gateway
- Plays returned TTS audio

## Manual Steps Required

1. **Rekognition Custom Labels**: Train model with labeled router images
2. **Bedrock Agent**: Configure agent with troubleshooting knowledge base
3. **API Integrations**: Configure internal provisioning API endpoints

## Testing

```bash
# Activate virtual environment first
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run unit tests
pytest tests/

# Run smoke test (after deployment)
python scripts/smoke_test.py <API_URL>
```

## Development

```bash
# Setup development environment
python setup.py

# Activate virtual environment
source venv/bin/activate  # Unix/Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install additional dev dependencies
pip install pytest black flake8

# Run linting
flake8 lambda_functions/ stacks/
black lambda_functions/ stacks/

# Deploy individual stacks for testing
cdk deploy CustomerServiceCore
cdk deploy CustomerServiceML
cdk deploy CustomerServiceApi
cdk deploy CustomerServiceWeb
```

## Security

- Least-privilege IAM policies
- PII redaction in logs
- Rate limiting on API Gateway
- Input validation and sanitization

## Cost Optimization

- S3 lifecycle policies for dev
- Small Bedrock model (Claude Haiku)
- CloudWatch log retention limits

## Troubleshooting

### Common Issues

1. **Virtual Environment Issues**
   ```bash
   # Remove and recreate
   rm -rf venv
   python setup.py
   ```

2. **CDK Bootstrap Issues**
   ```bash
   cdk bootstrap --force
   ```

3. **Permission Issues**
   - Ensure AWS CLI is configured with appropriate permissions
   - Check IAM roles have required policies

4. **Node.js Dependencies**
   ```bash
   cd web_client
   rm -rf node_modules package-lock.json
   npm install
   ```