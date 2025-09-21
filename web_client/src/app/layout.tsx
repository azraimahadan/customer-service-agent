import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'SUARA',
  description: 'AI-powered customer service chatbot for TM customers. Brought to you by Codezilla.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-background min-h-screen font-sf">{children}</body>
    </html>
  )
}