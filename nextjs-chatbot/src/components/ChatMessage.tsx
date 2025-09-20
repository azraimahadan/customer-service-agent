'use client'

import { Message } from '@/types'
import { User, Bot, Volume2 } from 'lucide-react'
import Image from 'next/image'

interface ChatMessageProps {
  message: Message
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.sender === 'user'

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'} mb-6`}>
      <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center shadow-ios ${
        isUser ? 'bg-primary text-white' : 'bg-surface text-primary border border-gray-200'
      }`}>
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>
      
      <div className={`chat-bubble ${isUser ? 'chat-bubble-user' : 'chat-bubble-bot'}`}>
        {message.type === 'text' && (
          <p className="text-base leading-relaxed">{message.content}</p>
        )}
        
        {message.type === 'image' && message.imageUrl && (
          <div>
            <Image 
              src={message.imageUrl} 
              alt="Uploaded image" 
              width={240} 
              height={240}
              className="rounded-ios mb-3 shadow-ios"
            />
            {message.content && <p className="text-base leading-relaxed">{message.content}</p>}
          </div>
        )}
        
        {message.type === 'audio' && message.audioUrl && (
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 bg-primary/10 rounded-full">
              <Volume2 size={16} className="text-primary" />
            </div>
            <audio controls className="flex-1 h-8">
              <source src={message.audioUrl} type="audio/wav" />
            </audio>
          </div>
        )}
        
        {message.audioResponse && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            <div className="flex items-center gap-2 mb-2">
              <Volume2 size={14} className="text-accent" />
              <span className="text-sm font-medium text-text-secondary">Audio Response</span>
            </div>
            <audio controls className="w-full h-8">
              <source src={message.audioResponse} type="audio/mpeg" />
            </audio>
          </div>
        )}
        
        <div className={`text-xs mt-2 opacity-100 ${isUser ? "text-white" : "text-gray-600" }`}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  )
}