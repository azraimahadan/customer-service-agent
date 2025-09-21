import ChatContainer from '@/components/ChatContainer'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-background via-surface-50 to-primary-50/20 py-6 px-4">
      <div className="absolute inset-0 bg-grid-pattern opacity-5 pointer-events-none"></div>
      <div className="relative z-10">
        <ChatContainer />
      </div>
    </main>
  )
}