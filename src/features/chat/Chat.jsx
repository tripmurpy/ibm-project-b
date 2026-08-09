import { useEffect, useRef, useState } from 'react'
import ChatComposer from './components/ChatComposer.jsx'
import ChatHeader from './components/ChatHeader.jsx'
import MessageList from './components/MessageList.jsx'
import ChatMessage from './ChatMessage.js'
import { sendChat } from './chatApi.js'

const welcomeMessage = ChatMessage.welcome()

export default function Chat() {
  const [messages, setMessages] = useState([welcomeMessage])
  const [threadId, setThreadId] = useState(null)
  const [isSending, setIsSending] = useState(false)
  const [replyTo, setReplyTo] = useState(null)
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function sendMessage(text) {
    const requestId = crypto.randomUUID()
    const pendingId = `pending-${requestId}`
    setIsSending(true)
    const reply = replyTo && { id: replyTo.id, text: replyTo.text, from: replyTo.from }
    setReplyTo(null)
    setMessages((current) => [...current, ChatMessage.fromUser(text, reply), ChatMessage.pending(pendingId)])

    try {
      const result = await sendChat({ requestId, threadId, question: text, replyTo: reply?.text })
      setThreadId(result.thread_id)
      setMessages((current) => current.flatMap((message) => {
        if (message.id !== pendingId) return [message]
        return (result.sections || [{ answer: result.answer, citations: result.citations }]).map((section, index) => (
          ChatMessage.fromAssistant({
            id: `${result.message_id}-${index}`,
            answer: section.answer,
            citations: section.citations,
            agent: section.agent,
          })
        ))
      }))
    } catch {
      setMessages((current) => current.map((message) => (
        message.id === pendingId
          ? ChatMessage.fromAssistant({
              id: pendingId,
              answer: 'Koneksi ke layanan sedang bermasalah. Coba lagi sebentar, ya.',
              status: 'failed',
            })
          : message
      )))
    } finally {
      setIsSending(false)
    }
  }

  return (
    <section className="chat" aria-label="Percakapan dengan Teman Tumbuh">
      <ChatHeader />

      <div className="notice" role="note">
        Informasi umum, bukan pengganti diagnosis atau pemeriksaan dokter.
      </div>

      <MessageList messages={messages} endRef={endRef} onReply={setReplyTo} />
      <ChatComposer onSend={sendMessage} disabled={isSending} replyTo={replyTo} onCancelReply={() => setReplyTo(null)} />
    </section>
  )
}
