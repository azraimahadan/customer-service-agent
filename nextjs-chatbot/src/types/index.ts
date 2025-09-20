export interface Message {
  id: string
  content: string
  sender: 'user' | 'bot'
  timestamp: Date
  type: 'text' | 'image' | 'audio'
  imageUrl?: string
  audioUrl?: string
  audioResponse?: string
  sessionId?: string
  actions?: string[]
}

export interface ChatState {
  messages: Message[]
  isLoading: boolean
  isRecording: boolean
  currentSessionId?: string
}