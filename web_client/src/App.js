import React, { useState, useRef } from 'react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://4c1w5gc7e8.execute-api.us-east-1.amazonaws.com/prod';

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [image, setImage] = useState(null);
  const [audioBlob, setAudioBlob] = useState(null);
  const [, setSessionId] = useState(null);
  const [response, setResponse] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const fileInputRef = useRef(null);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => setImage(e.target.result);
      reader.readAsDataURL(file);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setAudioBlob(audioBlob);
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const convertToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result.split(',')[1]);
      reader.onerror = error => reject(error);
    });
  };

  const submitIssue = async () => {
    if (!image || !audioBlob) {
      alert('Please provide both an image and audio recording');
      return;
    }

    setIsProcessing(true);
    setResponse('Processing your request...');

    try {
      // Convert files to base64
      const imageBase64 = image.split(',')[1];
      const audioBase64 = await convertToBase64(audioBlob);

      console.log('Uploading to:', `${API_BASE_URL}/upload`);
      
      // Upload files
      const uploadResponse = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          image: imageBase64,
          audio: audioBase64
        })
      });

      console.log('Upload response status:', uploadResponse.status);
      
      if (!uploadResponse.ok) {
        const errorText = await uploadResponse.text();
        console.error('Upload failed:', errorText);
        throw new Error(`Upload failed: ${uploadResponse.status} - ${errorText}`);
      }

      const uploadData = await uploadResponse.json();
      console.log('Upload successful:', uploadData);
      const currentSessionId = uploadData.session_id;
      setSessionId(currentSessionId);

      // Transcribe audio
      setResponse('Converting speech to text...');
      await fetch(`${API_BASE_URL}/transcribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: currentSessionId })
      });

      // Analyze image
      setResponse('Analyzing image...');
      await fetch(`${API_BASE_URL}/analyze-image`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: currentSessionId })
      });

      // Get troubleshooting response
      setResponse('Generating troubleshooting response...');
      const troubleshootResponse = await fetch(`${API_BASE_URL}/troubleshoot`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: currentSessionId })
      });

      const troubleshootData = await troubleshootResponse.json();
      setResponse(troubleshootData.response);

      // Play audio response
      if (troubleshootData.audio_url) {
        const audio = new Audio(troubleshootData.audio_url);
        audio.play();
      }

      // Execute recommended actions
      if (troubleshootData.actions && troubleshootData.actions.length > 0) {
        for (const action of troubleshootData.actions) {
          await fetch(`${API_BASE_URL}/execute-action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              session_id: currentSessionId,
              action: action
            })
          });
        }
      }

    } catch (error) {
      console.error('Error processing request:', error);
      setResponse(`Error: ${error.message}. Please check the console for details.`);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Unifi TV Customer Service</h1>
        <p>Upload an image of your issue and describe the problem</p>
      </header>

      <main className="App-main">
        <div className="upload-section">
          <div className="image-upload">
            <h3>Upload Image</h3>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              ref={fileInputRef}
            />
            {image && (
              <div className="image-preview">
                <img src={image} alt="Uploaded" style={{ maxWidth: '300px', maxHeight: '200px' }} />
              </div>
            )}
          </div>

          <div className="audio-recording">
            <h3>Record Your Issue</h3>
            <button
              onClick={isRecording ? stopRecording : startRecording}
              className={isRecording ? 'recording' : ''}
            >
              {isRecording ? 'Stop Recording' : 'Start Recording'}
            </button>
            {audioBlob && <p>Audio recorded successfully!</p>}
          </div>

          <button
            onClick={submitIssue}
            className={`submit-button ${(!image || !audioBlob || isProcessing) ? 'disabled' : ''}`}
          >
            {isProcessing ? 'Processing...' : 'Submit Issue'}
          </button>
        </div>

        {response && (
          <div className="response-section">
            <h3>Response</h3>
            <div className="response-text">
              {response}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
