import { useEffect, useState } from 'react'

const agentLabels = { mom: 'Kesehatan anak', koki_ben: 'Menu anak' }

function MessageText({ message }) {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  const [visibleText, setVisibleText] = useState(
    message.status === 'processing' || (message.from === 'assistant' && !reduceMotion) ? '' : message.text,
  )

  useEffect(() => {
    if (message.status === 'processing' || message.from !== 'assistant' || reduceMotion) return
    let index = 0
    const timer = setInterval(() => {
      index = Math.min(index + 3, message.text.length)
      setVisibleText(message.text.slice(0, index))
      if (index === message.text.length) clearInterval(timer)
    }, 18)
    return () => clearInterval(timer)
  }, [message, reduceMotion])

  return message.status === 'processing'
    ? <span className="typing" aria-label="Sedang mengetik"><i /><i /><i /></span>
    : <p>{visibleText}</p>
}

export default function MessageList({ messages, endRef, onReply }) {
  return (
    <div className="messages" aria-live="polite">
      <div className="date-chip">Hari ini</div>
      {messages.map((message) => (
        <article className={`message ${message.from}`} key={message.id} onDoubleClick={() => onReply(message)}>
          {message.agent && <span className="agent-label">{agentLabels[message.agent]}</span>}
          {message.replyTo && <blockquote className="reply-quote">{message.replyTo.text}</blockquote>}
          <MessageText message={message} />
          {message.citations.length > 0 && (
            <div className="sources">
              <span>Sumber</span>
              <ul className="citations" aria-label="Sumber jawaban">
              {message.citations.map((citation, index) => (
                <li key={`${citation.source_title}-${index}`}>
                  {citation.source_title}
                  {citation.page_start ? `, hal. ${citation.page_start}${citation.page_end && citation.page_end !== citation.page_start ? `–${citation.page_end}` : ''}` : ''}
                </li>
              ))}
              </ul>
            </div>
          )}
          <time>{message.time}</time>
          {message.status !== 'processing' && <button className="reply-button" type="button" onClick={() => onReply(message)}>Balas</button>}
        </article>
      ))}
      <div ref={endRef} />
    </div>
  )
}
