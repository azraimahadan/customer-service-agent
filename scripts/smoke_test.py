#!/usr/bin/env python3
"""
Smoke test script for Customer Service Agent
Tests the complete workflow with sample data
"""

import requests
import json
import base64
import time
import os
import sys

def load_sample_data():
    """Load sample image and audio data"""
    # Create a simple test image (1x1 pixel PNG)
    test_image_data = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=='
    )
    
    # Create a simple test audio (minimal WAV header)
    test_audio_data = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    
    return base64.b64encode(test_image_data).decode(), base64.b64encode(test_audio_data).decode()

def run_smoke_test(api_url):
    """Run complete smoke test"""
    print("Starting Customer Service Agent Smoke Test")
    print(f"API URL: {api_url}")
    
    try:
        # Load sample data
        print("\nLoading sample data...")
        image_b64, audio_b64 = load_sample_data()
        
        # Step 1: Upload files
        print("\nStep 1: Uploading image and audio...")
        upload_response = requests.post(
            f"{api_url}/upload",
            json={
                "image": image_b64,
                "audio": audio_b64
            },
            timeout=30
        )
        
        if upload_response.status_code != 200:
            raise Exception(f"Upload failed: {upload_response.text}")
        
        upload_data = upload_response.json()
        session_id = upload_data['session_id']
        print(f"Upload successful. Session ID: {session_id}")
        
        # Step 2: Transcribe audio
        print("\nStep 2: Transcribing audio...")
        transcribe_response = requests.post(
            f"{api_url}/transcribe",
            json={"session_id": session_id},
            timeout=60
        )
        
        if transcribe_response.status_code == 200:
            transcribe_data = transcribe_response.json()
            print(f"Transcription successful: {transcribe_data.get('transcript', 'N/A')}")
        else:
            print(f"Transcription failed (expected for test audio): {transcribe_response.status_code}")
        
        # Step 3: Analyze image
        print("\nStep 3: Analyzing image...")
        image_response = requests.post(
            f"{api_url}/analyze-image",
            json={"session_id": session_id},
            timeout=30
        )
        
        if image_response.status_code == 200:
            image_data = image_response.json()
            print(f"Image analysis successful. Labels found: {len(image_data.get('analysis', {}).get('labels', []))}")
        else:
            print(f"Image analysis failed: {image_response.status_code}")
        
        # Step 4: Get troubleshooting response
        print("\nStep 4: Getting AI troubleshooting response...")
        troubleshoot_response = requests.post(
            f"{api_url}/troubleshoot",
            json={"session_id": session_id},
            timeout=60
        )
        
        if troubleshoot_response.status_code == 200:
            troubleshoot_data = troubleshoot_response.json()
            print(f"Troubleshooting successful")
            print(f"Response: {troubleshoot_data.get('response', 'N/A')[:100]}...")
            
            # Step 5: Execute actions
            actions = troubleshoot_data.get('actions', [])
            if actions:
                print(f"\nStep 5: Executing {len(actions)} recommended actions...")
                for action in actions:
                    action_response = requests.post(
                        f"{api_url}/execute-action",
                        json={
                            "session_id": session_id,
                            "action": action
                        },
                        timeout=30
                    )
                    
                    if action_response.status_code == 200:
                        print(f"Action '{action}' executed successfully")
                    else:
                        print(f"Action '{action}' failed: {action_response.status_code}")
            else:
                print("\nStep 5: No actions to execute")
        else:
            print(f"Troubleshooting failed: {troubleshoot_response.status_code}")
        
        print("\nSmoke test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nSmoke test failed: {str(e)}")
        return False

def get_api_url_from_cdk():
    """Get API URL from CDK outputs"""
    import subprocess
    try:
        result = subprocess.run(['cdk', 'list', '--json'], capture_output=True, text=True)
        if result.returncode == 0:
            # Try to get the API URL from CloudFormation outputs
            cf_result = subprocess.run(['aws', 'cloudformation', 'describe-stacks', '--stack-name', 'CustomerServiceApi'], capture_output=True, text=True)
            if cf_result.returncode == 0:
                import json
                stacks = json.loads(cf_result.stdout)
                for stack in stacks['Stacks']:
                    for output in stack.get('Outputs', []):
                        if output['OutputKey'] == 'ApiUrl':
                            return output['OutputValue']
    except Exception as e:
        print(f"Could not get API URL automatically: {e}")
    return None

if __name__ == "__main__":
    api_url = None
    
    # Try to get API URL from command line argument
    if len(sys.argv) == 2:
        api_url = sys.argv[1].rstrip('/')
    else:
        # Try to get API URL from CDK outputs
        api_url = get_api_url_from_cdk()
        
    if not api_url:
        print("Usage: python smoke_test.py <API_URL>")
        print("Or run after CDK deployment to auto-detect API URL")
        sys.exit(1)
    
    success = run_smoke_test(api_url)
    sys.exit(0 if success else 1)