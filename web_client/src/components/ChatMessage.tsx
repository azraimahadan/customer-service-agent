'use client'

import { Message } from '@/types'
import { User, Bot, Volume2 } from 'lucide-react'
import Image from 'next/image'

interface ChatMessageProps {
  message: Message
  onActionClick?: (action: string) => void
}

export default function ChatMessage({ message, onActionClick }: ChatMessageProps) {
  const isUser = message.sender === 'user'

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'} mb-6 message-enter message-enter-active`}>
      <div className={isUser ? 'avatar' : 'avatar-bot'}>
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>
      
      <div className={`chat-bubble ${isUser ? 'chat-bubble-user' : 'chat-bubble-bot'}`}>
        {message.type === 'text' && (
          <p className="text-base leading-relaxed font-medium">{message.content}</p>
        )}
        
        {message.type === 'image' && message.imageUrl && (
          <div>
            <Image 
              src={message.imageUrl} 
              alt="Uploaded image" 
              width={240} 
              height={240}
              className="rounded-ios mb-3 shadow-ios-md border border-surface-200"
            />
            {message.content && <p className="text-base leading-relaxed font-medium">{message.content}</p>}
          </div>
        )}
        
        {message.type === 'audio' && message.audioUrl && (
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 bg-primary-50 rounded-full">
              <Volume2 size={16} className="text-primary-600" />
            </div>
            <audio controls className="flex-1 h-8">
              <source src={message.audioUrl} type="audio/wav" />
            </audio>
          </div>
        )}
        
        {message.audioResponse && (
          <div className="mt-3 pt-3 border-t border-surface-200">
            <div className="flex items-center gap-2 mb-2">
              <Volume2 size={14} className="text-secondary-500" />
              <span className="text-sm font-medium text-text-secondary">Audio Response</span>
            </div>
            <audio controls className="w-full h-8">
              <source src={message.audioResponse} type="audio/mpeg" />
            </audio>
          </div>
        )}
        
        {message.actions && message.actions.length > 0 && (
          <div className="mt-4 pt-3 border-t border-surface-200">
            <p className="text-sm font-medium text-text-secondary mb-2">Suggested Actions:</p>
            <div className="flex flex-wrap gap-2">
              {message.actions.map((action, index) => (
                <button
                  key={index}
                  onClick={() => onActionClick?.(action)}
                  className="btn-secondary text-xs px-3 py-1.5 hover:bg-primary-50 hover:text-primary-700 transition-colors"
                >
                  {action}
                </button>
              ))}
            </div>
          </div>
        )}
        
        <div className={`text-xs mt-2 font-medium ${isUser ? "text-white/80" : "text-text-muted" }`}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  )
}