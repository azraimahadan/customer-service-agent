import json
import boto3
import os

rekognition_client = boto3.client('rekognition')
s3_client = boto3.client('s3')
BUCKET_NAME = os.environ['STORAGE_BUCKET']
REKOGNITION_PROJECT_ARN = os.environ.get('REKOGNITION_PROJECT_ARN')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        session_id = body['session_id']
        image_key = f"sessions/{session_id}/image.jpg"
        
        analysis_results = {}
        
        # Try custom labels first (if project is trained)
        try:
            if REKOGNITION_PROJECT_ARN and REKOGNITION_PROJECT_ARN != "PLACEHOLDER_PROJECT_ARN":
                custom_response = rekognition_client.detect_custom_labels(
                    ProjectVersionArn=REKOGNITION_PROJECT_ARN,
                    Image={
                        'S3Object': {
                            'Bucket': BUCKET_NAME,
                            'Name': image_key
                        }
                    },
                    MinConfidence=70
                )
                analysis_results['custom_labels'] = custom_response.get('CustomLabels', [])
        except Exception as e:
            print(f"Custom labels detection failed: {e}")
            analysis_results['custom_labels'] = []
        
        # Fallback to standard label detection
        labels_response = rekognition_client.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': BUCKET_NAME,
                    'Name': image_key
                }
            },
            MaxLabels=20,
            MinConfidence=70
        )
        analysis_results['labels'] = labels_response.get('Labels', [])
        
        # Text detection for error messages
        text_response = rekognition_client.detect_text(
            Image={
                'S3Object': {
                    'Bucket': BUCKET_NAME,
                    'Name': image_key
                }
            }
        )
        analysis_results['text_detections'] = text_response.get('TextDetections', [])
        
        # Extract meaningful text
        detected_text = []
        for text_detection in analysis_results['text_detections']:
            if text_detection['Type'] == 'LINE' and text_detection['Confidence'] > 80:
                detected_text.append(text_detection['DetectedText'])
        
        analysis_results['extracted_text'] = detected_text
        
        # Store analysis results
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=f"sessions/{session_id}/image_analysis.json",
            Body=json.dumps(analysis_results),
            ContentType='application/json'
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'analysis': analysis_results,
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