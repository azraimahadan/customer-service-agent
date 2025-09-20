'use client'

import { useState, useRef } from 'react'
import { Send, Mic, MicOff, Image, X, Camera } from 'lucide-react'

interface ChatInputProps {
  onSendMessage: (content: string, type: 'text' | 'image' | 'audio', file?: File) => void
  isLoading: boolean
  isRecording: boolean
  onStartRecording: () => void
  onStopRecording: () => void
}

export default function ChatInput({ 
  onSendMessage, 
  isLoading, 
  isRecording, 
  onStartRecording, 
  onStopRecording 
}: ChatInputProps) {
  const [message, setMessage] = useState('')
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!message.trim() && !selectedImage) return

    if (selectedImage) {
      onSendMessage(message, 'image', selectedImage)
      setSelectedImage(null)
      setImagePreview(null)
    } else {
      onSendMessage(message, 'text')
    }
    setMessage('')
  }

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedImage(file)
      const reader = new FileReader()
      reader.onload = (e) => setImagePreview(e.target?.result as string)
      reader.readAsDataURL(file)
    }
  }

  const removeImage = () => {
    setSelectedImage(null)
    setImagePreview(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  return (
    <div className="glass-effect border-t border-gray-200/50 p-4">
      {imagePreview && (
        <div className="mb-4 relative inline-block">
          <img src={imagePreview} alt="Preview" className="max-w-24 max-h-24 rounded-ios shadow-ios" />
          <button
            onClick={removeImage}
            className="absolute -top-2 -right-2 bg-danger text-white rounded-full p-1 hover:bg-red-600 shadow-ios active:scale-95 transition-all"
          >
            <X size={12} />
          </button>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="flex gap-3 items-end">
        <div className="flex-1">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask about your issue..."
            className="input-field resize-none min-h-[44px] max-h-32"
            rows={1}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSubmit(e)
              }
            }}
          />
        </div>
        
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleImageSelect}
          className="hidden"
        />
        
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          className="btn-secondary p-3"
          disabled={isLoading}
        >
          <Camera size={20} />
        </button>
        
        <button
          type="button"
          onClick={isRecording ? onStopRecording : onStartRecording}
          className={`btn-secondary p-3 ${
            isRecording 
              ? 'bg-danger/10 text-danger border-danger/20 animate-pulse' 
              : ''
          }`}
          disabled={isLoading}
        >
          {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
        </button>
        
        <button
          type="submit"
          disabled={isLoading || (!message.trim() && !selectedImage)}
          className="btn-primary p-3"
        >
          <Send size={20} />
        </button>
      </form>
    </div>
  )
}