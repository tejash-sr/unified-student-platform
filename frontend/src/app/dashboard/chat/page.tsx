'use client'

import React from 'react'
import { Send, MessageCircle } from 'lucide-react'

export default function ChatPage() {
  const [messages, setMessages] = React.useState<Array<{ id: string; type: 'user' | 'bot'; text: string }>>([
    {
      id: '1',
      type: 'bot',
      text: 'Hi! 👋 I\'m your AI study guide. I can help you find courses, understand loan options, calculate ROI, and answer questions about international education. What can I help with today?',
    },
  ])
  const [input, setInput] = React.useState('')
  const [loading, setLoading] = React.useState(false)
  const messagesEndRef = React.useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  React.useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim()) return

    // Add user message
    const userMessage = {
      id: Date.now().toString(),
      type: 'user' as const,
      text: input,
    }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)

    // Simulate bot response (in production, this would call Flowise API)
    setTimeout(() => {
      const botMessage = {
        id: (Date.now() + 1).toString(),
        type: 'bot' as const,
        text: generateBotResponse(input),
      }
      setMessages((prev) => [...prev, botMessage])
      setLoading(false)
    }, 1000)
  }

  const generateBotResponse = (query: string): string => {
    const lowerQuery = query.toLowerCase()
    
    if (lowerQuery.includes('course') || lowerQuery.includes('program')) {
      return 'I can help you find the perfect course! What are your interests? For example:\n- Computer Science?\n- Business?\n- Data Science?\n\nAlso, which countries are you interested in? (USA, UK, Canada, etc.)'
    } else if (lowerQuery.includes('loan') || lowerQuery.includes('financing')) {
      return 'Great question! Based on your profile, you might be eligible for loans up to ₹50 lakhs. Key factors include:\n- Your annual income\n- Academic performance\n- Work experience\n\nWould you like me to calculate your potential EMI?'
    } else if (lowerQuery.includes('roi') || lowerQuery.includes('return')) {
      return 'ROI calculation depends on:\n- Course cost\n- Expected salary after graduation\n- Loan amount & interest rate\n\nTypically, students see positive ROI within 3-5 years. Would you like to calculate yours?'
    } else {
      return 'That\'s a great question! I can help with course recommendations, loan eligibility, ROI calculations, and more. Could you be more specific about what you\'d like to know?'
    }
  }

  return (
    <div className="md:ml-64 p-6 max-w-4xl h-screen flex flex-col">
      <h1 className="text-3xl font-bold text-neutral-900 mb-6 flex items-center gap-2">
        <MessageCircle size={32} className="text-primary-600" />
        AI Study Guide
      </h1>

      {/* Chat Container */}
      <div className="flex-1 bg-white rounded-lg border border-neutral-200 p-6 overflow-y-auto mb-6">
        <div className="space-y-4 max-w-2xl">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`px-4 py-3 rounded-lg max-w-xs lg:max-w-md ${
                  message.type === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-neutral-100 text-neutral-900 border border-neutral-200'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{message.text}</p>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="px-4 py-3 bg-neutral-100 text-neutral-900 rounded-lg border border-neutral-200">
                <div className="flex gap-2">
                  <div className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="flex gap-2">
        <input
          type="text"
          placeholder="Ask about courses, loans, ROI, or anything else..."
          className="flex-1 px-4 py-3 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition font-medium disabled:opacity-50 flex items-center gap-2"
        >
          <Send size={20} />
        </button>
      </div>

      {/* Quick Actions */}
      <div className="mt-4 flex flex-wrap gap-2">
        <button
          onClick={() => setInput('Show me Computer Science courses in USA')}
          className="text-xs px-3 py-2 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 rounded-full transition"
        >
          💻 CS Courses
        </button>
        <button
          onClick={() => setInput('Check my loan eligibility')}
          className="text-xs px-3 py-2 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 rounded-full transition"
        >
          💰 Check Loan
        </button>
        <button
          onClick={() => setInput('Calculate ROI for a course')}
          className="text-xs px-3 py-2 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 rounded-full transition"
        >
          📈 ROI Calc
        </button>
      </div>
    </div>
  )
}
