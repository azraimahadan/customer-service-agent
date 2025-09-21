'use client'

import { useState, useRef, useEffect } from 'react'
import { Message } from '@/types'
import { ApiClient } from '@/lib/api'
import ChatMessage from './ChatMessage'
import ChatInput from './ChatInput'
import { Loader2, Tv } from 'lucide-react'

export default function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Hello! I\'m SUARA, your customer service assistant brought to you by Team Codezilla. How can I assist you today?',
      sender: 'bot',
      timestamp: new Date(),
      type: 'text'
    }
  ])
  const [isLoading, setIsLoading] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const processWithBackend = async (sessionId: string, hasImage: boolean, hasAudio: boolean) => {
    try {
      // Step 1: Transcribe audio if present
      if (hasAudio) {
        await ApiClient.transcribeAudio(sessionId)
      }

      // Step 2: Analyze image if present
      if (hasImage) {
        await ApiClient.analyzeImage(sessionId)
      }

      // Step 3: Get troubleshooting response
      const troubleshootResult = await ApiClient.troubleshoot(sessionId)
      
      if (troubleshootResult.error) {
        throw new Error(troubleshootResult.error)
      }

      const response = troubleshootResult.data!
      
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        sender: 'bot',
        timestamp: new Date(),
        type: 'text',
        audioResponse: response.audio_url,
        sessionId: response.session_id,
        actions: response.actions
      }

      setMessages(prev => [...prev, botResponse])
      
    } catch (error) {
      console.error('Backend processing error:', error)
      
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: 'I\'m having trouble processing your request right now. Please try again or contact support if the issue persists.',
        sender: 'bot',
        timestamp: new Date(),
        type: 'text'
      }
      
      setMessages(prev => [...prev, errorResponse])
    }
  }

  const handleSendMessage = async (content: string, type: 'text' | 'image' | 'audio', file?: File) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      sender: 'user',
      timestamp: new Date(),
      type,
      imageUrl: file && type === 'image' ? URL.createObjectURL(file) : undefined,
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      if (type === 'text' && !file) {
        // Simple text message - provide immediate response
        const botResponse: Message = {
          id: (Date.now() + 1).toString(),
          content: 'I understand you have a question about your Unifi TV service. For the most accurate troubleshooting, please share a photo of any error messages on your screen or record an audio description of the issue you\'re experiencing.',
          sender: 'bot',
          timestamp: new Date(),
          type: 'text'
        }
        setMessages(prev => [...prev, botResponse])
      } else {
        // Upload files and process with backend
        const uploadResult = await ApiClient.uploadFiles(
          type === 'image' ? file : undefined,
          type === 'audio' ? file as Blob : undefined
        )
        
        if (uploadResult.error) {
          throw new Error(uploadResult.error)
        }

        const sessionId = uploadResult.data!.session_id
        setCurrentSessionId(sessionId)
        
        // Process with backend pipeline
        await processWithBackend(sessionId, type === 'image', type === 'audio')
      }
    } catch (error) {
      console.error('Error sending message:', error)
      
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
        type: 'text'
      }
      
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data)
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        const audioUrl = URL.createObjectURL(audioBlob)
        
        const audioMessage: Message = {
          id: Date.now().toString(),
          content: 'Audio message describing the issue',
          sender: 'user',
          timestamp: new Date(),
          type: 'audio',
          audioUrl
        }

        setMessages(prev => [...prev, audioMessage])
        handleSendMessage('Audio message describing the issue', 'audio', audioBlob as File)
        
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch (error) {
      console.error('Error starting recording:', error)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-surface shadow-ios-xl rounded-ios-lg overflow-hidden">
      {/* Header */}
      <div className="header-gradient text-white p-6">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center shadow-ios backdrop-blur-ios">
            <Tv size={24} />
          </div>
          <div>
            <h1 className="text-xl font-semibold tracking-tight">SUARA</h1>
            <p className="text-sm opacity-90 font-medium">AI-Powered Customer Service</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 bg-background custom-scrollbar">
        <div className="space-y-4">
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          
          {isLoading && (
            <div className="flex gap-3 mb-6 message-enter message-enter-active">
              <div className="avatar-bot">
                <Loader2 size={16} className="animate-spin text-primary-600" />
              </div>
              <div className="chat-bubble chat-bubble-bot">
                <div className="flex items-center gap-3">
                  <div className="typing-indicator">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                  <span className="text-sm text-text-secondary font-medium">Analyzing your issue...</span>
                </div>
              </div>
            </div>
          )}
        </div>
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-surface-200 bg-surface/50 backdrop-blur-ios">
        <ChatInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          isRecording={isRecording}
          onStartRecording={startRecording}
          onStopRecording={stopRecording}
        />
      </div>
    </div>
  )
}