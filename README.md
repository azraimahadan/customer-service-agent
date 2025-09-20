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
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
npm install -g aws-cdk

# Deploy
cdk bootstrap
./deploy.sh
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
- `bedrock_agent_handler`: AI troubleshooting orchestration
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
# Run unit tests
pytest tests/

# Run smoke test
python scripts/smoke_test.py
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