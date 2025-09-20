import json
import boto3
import os

bedrock_runtime = boto3.client('bedrock-runtime')
polly_client = boto3.client('polly')
s3_client = boto3.client('s3')
BUCKET_NAME = os.environ['STORAGE_BUCKET']
BEDROCK_AGENT_ID = os.environ.get('BEDROCK_AGENT_ID', 'PLACEHOLDER_AGENT_ID')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        session_id = body['session_id']
        
        # Get transcript and image analysis
        transcript_obj = s3_client.get_object(
            Bucket=BUCKET_NAME,
            Key=f"sessions/{session_id}/transcript.json"
        )
        transcript_data = json.loads(transcript_obj['Body'].read())
        
        analysis_obj = s3_client.get_object(
            Bucket=BUCKET_NAME,
            Key=f"sessions/{session_id}/image_analysis.json"
        )
        analysis_data = json.loads(analysis_obj['Body'].read())
        
        # Prepare input for Bedrock agent
        user_input = f"""
        Customer Issue: {transcript_data['text']}
        
        Image Analysis:
        - Detected Labels: {[label['Name'] for label in analysis_data.get('labels', [])]}
        - Detected Text: {analysis_data.get('extracted_text', [])}
        - Custom Labels: {[label['Name'] for label in analysis_data.get('custom_labels', [])]}
        
        Please analyze this Unifi TV issue and provide troubleshooting steps.
        """
        
        # Call Bedrock with Llama model directly
        try:
            bedrock_runtime = boto3.client('bedrock-runtime')
            
            # Use Llama 3.3 70B Instruct model
            model_id = "meta.llama3-3-70b-instruct-v1:0"
            
            prompt = f"""You are a Unifi TV customer service agent. Analyze this customer issue and provide troubleshooting steps.

Customer Issue: {transcript_data['text']}

Image Analysis Results:
- Detected Labels: {[label['Name'] for label in analysis_data.get('labels', [])]}
- Detected Text: {analysis_data.get('extracted_text', [])}
- Custom Labels: {[label['Name'] for label in analysis_data.get('custom_labels', [])]}

Provide a helpful response with specific troubleshooting steps. If you see "No Service" error or similar issues, suggest checking cables, restarting the set-top box, and re-provisioning the service.

Response:"""

            response = bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps({
                    "messages": [
                        {"role": "user", "content": "your prompt here"}
                    ],
                    "max_tokens": 512,
                    "temperature": 0.7,
                    "top_p": 0.9
                })
            )
            
            response_body = json.loads(response['body'].read())
            agent_response = response_body.get('generation', '')
            
        except Exception as e:
            print(f"Bedrock Llama call failed: {e}")
            agent_response = generate_fallback_response(transcript_data['text'], analysis_data)
        
        # Generate TTS audio
        tts_response = polly_client.synthesize_speech(
            Text=agent_response,
            OutputFormat='mp3',
            VoiceId='Joanna'
        )
        
        # Store audio response
        audio_key = f"sessions/{session_id}/response.mp3"
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=audio_key,
            Body=tts_response['AudioStream'].read(),
            ContentType='audio/mpeg'
        )
        
        # Store troubleshooting response
        troubleshooting_data = {
            'response_text': agent_response,
            'audio_key': audio_key,
            'recommended_actions': extract_actions(agent_response)
        }
        
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=f"sessions/{session_id}/troubleshooting.json",
            Body=json.dumps(troubleshooting_data),
            ContentType='application/json'
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'response': agent_response,
                'audio_url': f"https://{BUCKET_NAME}.s3.amazonaws.com/{audio_key}",
                'actions': troubleshooting_data['recommended_actions'],
                'session_id': session_id
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }

def generate_fallback_response(transcript, analysis):
    """Generate a basic troubleshooting response when Bedrock agent is not available"""
    detected_text = analysis.get('extracted_text', [])
    labels = [label['Name'] for label in analysis.get('labels', [])]
    
    response = "I understand you're having issues with your Unifi TV service. "
    
    if 'no service' in transcript.lower() or any('no service' in text.lower() for text in detected_text):
        response += "I can see there's a 'No Service' error. Let me help you with these steps: "
        response += "1. Check if all cables are properly connected. "
        response += "2. Restart your set-top box by unplugging it for 30 seconds. "
        response += "3. I'll also check your subscription status and re-provision your service if needed."
    elif 'hdmi' in transcript.lower():
        response += "I notice you mentioned HDMI. Please ensure the HDMI cable is securely connected to both your set-top box and TV."
    else:
        response += "Let me run some diagnostics and provide you with the appropriate troubleshooting steps."
    
    return response

def extract_actions(response_text):
    """Extract actionable items from the response"""
    actions = []
    if 'restart' in response_text.lower():
        actions.append('restart_stb')
    if 'provision' in response_text.lower():
        actions.append('reprovision_service')
    if 'subscription' in response_text.lower():
        actions.append('check_subscription')
    return actions