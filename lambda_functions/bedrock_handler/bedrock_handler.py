import json
import boto3
import os
from botocore.exceptions import ClientError
import re
import requests
import time

bedrock_runtime = boto3.client('bedrock-runtime')
bedrock_agent = boto3.client('bedrock-agent-runtime')
polly_client = boto3.client('polly')
s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')

BUCKET_NAME = os.environ['STORAGE_BUCKET']
KNOWLEDGE_BASE_ID = "HU9V8VBZBI"
# Auto-detect action executor function name or use direct API calls
API_BASE_URL = "https://439qy87kqq.ap-southeast-1.awsapprunner.com"

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        session_id = body['session_id']
        
        # Get transcript and image analysis (if they exist)
        transcript_data = {'text': 'No audio provided'}
        analysis_data = {'labels': [], 'extracted_text': [], 'custom_labels': []}
        
        try:
            transcript_obj = s3_client.get_object(
                Bucket=BUCKET_NAME,
                Key=f"sessions/{session_id}/transcript.json"
            )
            transcript_data = json.loads(transcript_obj['Body'].read())
        except ClientError as e:
            if e.response['Error']['Code'] != 'NoSuchKey':
                raise
            print(f"No transcript found for session {session_id}")
        
        try:
            analysis_obj = s3_client.get_object(
                Bucket=BUCKET_NAME,
                Key=f"sessions/{session_id}/image_analysis.json"
            )
            analysis_data = json.loads(analysis_obj['Body'].read())
        except ClientError as e:
            if e.response['Error']['Code'] != 'NoSuchKey':
                raise
            print(f"No image analysis found for session {session_id}")
        
        # Analyze query and get knowledge base context
        query_complexity = analyze_query_complexity(transcript_data['text'])
        kb_context = get_knowledge_base_context(transcript_data['text'], analysis_data)
        
        # Determine if tools are needed and which ones
        required_tools = determine_required_tools(transcript_data['text'], analysis_data, kb_context)
        
        # Execute tools if needed
        tool_results = {}
        if required_tools:
            print(f"Executing tools for session {session_id}: {required_tools}")
            tool_results = execute_tools(session_id, required_tools, transcript_data['text'])
        
        # Call Bedrock with adaptive prompt (enhanced with tool results)
        try:
            # Use enhanced prompt if we have tool results, otherwise use adaptive prompt
            if tool_results:
                prompt = build_enhanced_prompt(
                    transcript_data['text'], 
                    analysis_data, 
                    query_complexity, 
                    kb_context,
                    tool_results
                )
            else:
                prompt = build_adaptive_prompt(transcript_data['text'], analysis_data, query_complexity, kb_context)

            max_tokens = 512 if query_complexity == 'simple' else 1024
            native_request = {
                "messages": [
                    {"role": "system", "content": "You are a helpful Unifi TV customer service agent. Provide conversational, friendly responses based on the information available."},
                    {"role": "user", "content": prompt}
                ],
                "max_completion_tokens": max_tokens,
                "temperature": 0.2,
            }

            request = json.dumps(native_request)

            try:
                model_id = "openai.gpt-oss-120b-1:0"
                response = bedrock_runtime.invoke_model(modelId=model_id, body=request)
            except Exception as e:
                print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
                exit(1)

            model_response = json.loads(response["body"].read())

            # ✅ Extract only the model-generated text
            agent_response = model_response["choices"][0]["message"]["content"]
            agent_response = re.sub(r"<reasoning>.*?</reasoning>", "", agent_response, flags=re.DOTALL).strip()

            
        except Exception as e:
            print(f"Bedrock Llama call failed: {e}")
            # Use enhanced fallback if we have tool results, otherwise use basic fallback
            if tool_results:
                agent_response = generate_enhanced_fallback_response(
                    transcript_data['text'], 
                    analysis_data, 
                    tool_results
                )
            else:
                agent_response = generate_fallback_response(transcript_data['text'], analysis_data)
        
        # Generate TTS audio
        try:
            tts_response = polly_client.synthesize_speech(
                Text=agent_response,
                OutputFormat='mp3',
                VoiceId='Joanna'
            )
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == 'TextLengthExceededException':
                truncated_text = agent_response[:2500]
                print(f"WARNING: Text length exceeded, retrying with truncated text ({len(truncated_text)} chars)")
                tts_response = polly_client.synthesize_speech(
                    Text=truncated_text,
                    OutputFormat='mp3',
                    VoiceId='Joanna'
                )
            else:
                raise
        
        # Format response for better readability
        formatted_response = format_markdown_response(agent_response)
        
        # Store audio response with proper headers
        audio_key = f"sessions/{session_id}/response.mp3"
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=audio_key,
            Body=tts_response['AudioStream'].read(),
            ContentType='audio/mpeg',
            CacheControl='max-age=3600',
            Metadata={
                'Content-Type': 'audio/mpeg'
            }
        )
        
        # Use environment variable for API URL (will be set after deployment)
        api_base_url = os.environ.get('API_BASE_URL')
        if api_base_url:
            audio_url = f"{api_base_url}/audio/{session_id}"
        else:
            # Fallback to presigned URL if API URL not available
            audio_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': BUCKET_NAME, 'Key': audio_key},
                ExpiresIn=3600
            )
        
        # Store troubleshooting response
        troubleshooting_data = {
            'response_text': formatted_response,
            'audio_key': audio_key,
            'recommended_actions': extract_actions(agent_response),
            'tools_executed': list(tool_results.keys()) if tool_results else [],
            'tool_results_summary': summarize_tool_results(tool_results) if tool_results else "No tools executed"
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
                'response': formatted_response,
                'audio_url': audio_url,
                'actions': troubleshooting_data['recommended_actions'],
                'tools_executed': troubleshooting_data.get('tools_executed', []),
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

def analyze_query_complexity(query_text):
    """Analyze query complexity to determine response type"""
    complexity_indicators = {
        'simple': ['restart', 'reboot', 'turn on', 'turn off', 'no signal', 'black screen'],
        'complex': ['intermittent', 'sometimes', 'multiple', 'various', 'different channels', 'specific times']
    }
    
    query_lower = query_text.lower()
    word_count = len(query_text.split())
    
    if word_count > 20 or any(indicator in query_lower for indicator in complexity_indicators['complex']):
        return 'complex'
    return 'simple'

def get_knowledge_base_context(query, analysis_data):
    """Retrieve relevant context using Bedrock Knowledge Base semantic search"""
    try:
        final_query = query + " " + " ".join([l['Name'] for l in analysis_data.get('labels', [])])
        response = bedrock_agent.retrieve(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            retrievalQuery={'text': query},
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 3
                }
            }
        )
        
        context = ""
        for result in response['retrievalResults']:
            context += result['content']['text'] + "\n"
        
        return context.strip()
    except Exception as e:
        print(f"KB retrieval failed: {e}")
        return ""

def determine_required_tools(query_text, analysis_data, kb_context):
    """Determine which tools are needed based on query and context"""
    tools_needed = []
    query_lower = query_text.lower()
    
    # Analyze the text from image for error indicators
    detected_texts = [text.lower() for text in analysis_data.get('extracted_text', [])]
    all_text = f"{query_lower} {' '.join(detected_texts)}"
    
    # Enhanced tool determination logic for common issues
    
    # 1. Outstanding balance / Payment issues
    balance_indicators = ['outstanding', 'balance', 'payment', 'bill', 'billing', 'overdue', 'suspended', 'expired', 'subscription']
    if any(indicator in all_text for indicator in balance_indicators):
        tools_needed.extend(['check_account', 'refresh_account'])
        print(f"Detected billing/account issue: {[i for i in balance_indicators if i in all_text]}")
    
    # 2. Loading/Performance issues  
    loading_indicators = ['loading', 'slow', 'buffering', 'stuck', 'frozen', 'spinning', 'waiting']
    if any(indicator in all_text for indicator in loading_indicators):
        tools_needed.extend(['quick_tv_check', 'restart_stb'])
        print(f"Detected loading/performance issue: {[i for i in loading_indicators if i in all_text]}")
    
    # 3. General technical issues
    technical_indicators = ['not working', 'broken', 'error', 'problem', 'issue', 'black screen', 'no signal', 'no service']
    if any(indicator in all_text for indicator in technical_indicators):
        tools_needed.extend(['detect_tv_errors', 'quick_tv_check'])
        print(f"Detected technical issue: {[i for i in technical_indicators if i in all_text]}")
    
    # 4. Service restoration needs
    service_indicators = ['restart', 'reboot', 'reset', 'fix', 'restore']
    if any(indicator in all_text for indicator in service_indicators):
        tools_needed.append('restart_stb')
        print(f"Detected service restoration need: {[i for i in service_indicators if i in all_text]}")
    
    # 5. Always analyze image if we have visual data (important for error screens)
    if analysis_data.get('labels') or analysis_data.get('extracted_text'):
        tools_needed.append('analyze_image')
    
    # 6. Default diagnostic if no specific indicators found but customer has an issue
    if not tools_needed and any(word in all_text for word in ['help', 'issue', 'problem', 'not', 'cant', "can't"]):
        tools_needed.extend(['quick_tv_check', 'check_account'])
        print("No specific indicators found, running default diagnostics")
    
    # Remove duplicates while preserving order
    return list(dict.fromkeys(tools_needed))

def execute_tools(session_id, tools, query_context):
    """Execute the required tools and return results"""
    tool_results = {}
    priority = determine_priority(query_context)
    
    for tool in tools:
        try:
            print(f"Executing tool: {tool} for session: {session_id}")
            tool_results[tool] = execute_single_tool(tool, session_id, query_context, priority)
                
        except Exception as e:
            print(f"Error executing tool {tool}: {str(e)}")
            tool_results[tool] = {'success': False, 'message': f'Tool error: {str(e)}'}
    
    return tool_results

def execute_single_tool(tool, session_id, query_context, priority):
    """Execute a single tool using direct API calls"""
    
    # Map tool names to API endpoints
    tool_endpoints = {
        'restart_stb': '/restartBox',
        'refresh_account': '/refreshAccBill',
        'check_account': '/checkAccount',
        'quick_tv_check': '/aws/quick-tv-check',
        'detect_tv_errors': '/aws/detect-tv-errors',
        'analyze_image': '/aws/analyze-image'
    }
    
    endpoint = tool_endpoints.get(tool)
    if not endpoint:
        return {'success': False, 'message': f'Unknown tool: {tool}'}
    
    try:
        api_url = f"{API_BASE_URL}{endpoint}"
        payload = {
            'session_id': session_id,
            'priority': priority,
            'context': query_context[:200] if query_context else ''
        }
        
        # Set timeout based on tool type
        timeout = 60 if tool in ['restart_stb', 'refresh_account'] else 30
        
        response = requests.post(
            api_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'message': f'{tool.replace("_", " ").title()} completed successfully',
                'details': result,
                'tool': tool
            }
        else:
            return {
                'success': False,
                'message': f'{tool.replace("_", " ").title()} failed with status {response.status_code}',
                'details': {'status_code': response.status_code}
            }
            
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'message': f'{tool.replace("_", " ").title()} timed out - operation may still be in progress',
            'timeout': True
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'{tool.replace("_", " ").title()} failed: {str(e)}'
        }

def determine_priority(query_text):
    """Determine priority based on query urgency"""
    urgent_keywords = ['urgent', 'emergency', 'critical', 'immediately', 'asap', 'not working at all']
    query_lower = query_text.lower()
    
    if any(keyword in query_lower for keyword in urgent_keywords):
        return 'high'
    return 'normal'

def build_enhanced_prompt(query, analysis_data, complexity, kb_context, tool_results):
    """Build enhanced prompt with tool results"""
    
    prompt = f"""You are a friendly Unifi TV customer service agent helping a customer.

Customer's Issue: {query}

Image Analysis:
- Detected Labels: {[l['Name'] for l in analysis_data.get('labels', [])]}
- Text from Screen: {analysis_data.get('extracted_text', [])}
- Technical Details: {[l['Name'] for l in analysis_data.get('custom_labels', [])]}"""
    
    if kb_context:
        prompt += f"\n\nKnowledge Base Information:\n{kb_context[:500]}..."
    
    if tool_results:
        prompt += f"\n\nActions Taken:"
        for tool, result in tool_results.items():
            if result.get('success'):
                prompt += f"\n- {tool.replace('_', ' ').title()}: {result.get('message', 'Completed successfully')}"
                if 'health_score' in result:
                    prompt += f" (Health Score: {result['health_score']})"
            else:
                prompt += f"\n- {tool.replace('_', ' ').title()}: {result.get('message', 'Failed to complete')}"
    
    if complexity == 'simple':
        prompt += "\n\nProvide a friendly, conversational response in 2-3 sentences explaining what you've done and any next steps."
    else:
        prompt += "\n\nProvide a comprehensive but conversational explanation of the situation, what actions were taken, and recommended next steps. Keep it friendly and easy to understand."
    
    prompt += "\n\nImportant: Speak as if you've personally performed these actions for the customer. Be conversational and reassuring."
    
    return prompt

def generate_enhanced_fallback_response(query, analysis_data, tool_results):
    """Enhanced fallback response that incorporates tool results"""
    
    response = "I've been helping you with your Unifi TV service issue. "
    
    # Incorporate tool results into fallback response
    if tool_results:
        successful_tools = [tool for tool, result in tool_results.items() if result.get('success')]
        if successful_tools:
            response += f"I've completed some troubleshooting steps including {', '.join([t.replace('_', ' ') for t in successful_tools])}. "
    
    # Analyze the issue based on available data
    detected_texts = [text.lower() for text in analysis_data.get('extracted_text', [])]
    
    if any('no service' in text for text in detected_texts) or 'no service' in query.lower():
        response += "I can see there's a 'No Service' error on your screen. I've run some diagnostics and restarted your set-top box. "
        response += "Please wait about 2 minutes for the service to fully restore. If the issue persists, I may need to refresh your account subscription."
    
    elif any('error' in text for text in detected_texts):
        response += "I've detected some error messages on your TV screen and have run diagnostics to identify the specific issue. "
        response += "I've also initiated some corrective actions that should help resolve the problem."
    
    else:
        response += "I've run a comprehensive check of your TV service and taken some troubleshooting steps to improve your experience."
    
    response += " Is there anything specific you'd like me to explain about what I've done?"
    
    return response

def summarize_tool_results(tool_results):
    """Create a summary of tool execution results"""
    if not tool_results:
        return "No tools executed"
    
    successful = [tool for tool, result in tool_results.items() if result.get('success')]
    failed = [tool for tool, result in tool_results.items() if not result.get('success')]
    
    summary = f"Executed {len(tool_results)} tools. "
    if successful:
        summary += f"Successful: {', '.join(successful)}. "
    if failed:
        summary += f"Failed: {', '.join(failed)}."
    
    return summary



def build_adaptive_prompt(query, analysis_data, complexity, kb_context):
    """Build prompt based on complexity and available context"""
    base_prompt = f"""You are a Unifi TV customer service agent.

Customer Issue: {query}

Image Analysis:
- Labels: {[l['Name'] for l in analysis_data.get('labels', [])]}
- Text: {analysis_data.get('extracted_text', [])}
- Custom: {[l['Name'] for l in analysis_data.get('custom_labels', [])]}

Instructions: 
If the user's query is ambiguous, prompt user for asking again.
Utilize Knowledge Base context only if user's issue is clear..
"""
    
    if kb_context:
        base_prompt += f"\n\nKnowledge Base Context:\n{kb_context}"
    
    if complexity == 'simple':
        base_prompt += "\n\nProvide a concise, direct solution with 2-3 key steps."
    else:
        base_prompt += "\n\nProvide detailed troubleshooting with explanations, multiple options, and preventive measures."
    
    return base_prompt

def format_markdown_response(text):
    """Format response text for better markdown readability"""
    # Clean up the text
    text = text.strip()
    
    # Add proper spacing around numbered lists
    text = re.sub(r'(\d+\.)\s*', r'\n\1 ', text)
    
    # Add proper spacing around bullet points
    text = re.sub(r'([•-])\s*', r'\n\1 ', text)
    
    # Add spacing around bold text
    text = re.sub(r'\*\*(.*?)\*\*', r'\n**\1**\n', text)
    
    # Clean up multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Ensure proper paragraph spacing
    sentences = text.split('. ')
    formatted_sentences = []
    
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if sentence:
            if i < len(sentences) - 1:
                sentence += '.'
            formatted_sentences.append(sentence)
    
    # Join with proper spacing
    result = ' '.join(formatted_sentences)
    
    # Add line breaks before questions
    result = re.sub(r'(\?\s*)([A-Z])', r'\1\n\n\2', result)
    
    return result.strip()

def extract_actions(response_text):
    """Extract actionable items from the response"""
    actions = []
    response_lower = response_text.lower()
    
    if any(word in response_lower for word in ['restart', 'reboot', 'reset']):
        actions.append('restart_stb')
    if any(word in response_lower for word in ['refresh', 'provision', 'subscription']):
        actions.append('refresh_account')
    if any(word in response_lower for word in ['check', 'verify', 'account']):
        actions.append('check_account')
    if any(word in response_lower for word in ['diagnos', 'health', 'status']):
        actions.append('quick_tv_check')
    
    return actions
