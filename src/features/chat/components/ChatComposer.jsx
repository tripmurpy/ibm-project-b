import { useEffect, useRef, useState } from 'react'

function SendIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M3.4 20.4 21 12 3.4 3.6l-.2 6.5L15.8 12 3.2 13.9l.2 6.5Z" />
    </svg>
  )
}

export default function ChatComposer({ onSend, disabled = false, replyTo = null, onCancelReply }) {
  const [draft, setDraft] = useState('')
  const inputRef = useRef(null)

  useEffect(() => {
    if (!disabled) inputRef.current?.focus()
  }, [disabled])

  function submit(event) {
    event.preventDefault()
    if (!draft.trim() || disabled) return

    onSend(draft)
    setDraft('')
    requestAnimationFrame(() => inputRef.current?.focus())
  }

  return (
    <form className="composer" onSubmit={submit}>
      {replyTo && (
        <div className="reply-preview">
          <span>{replyTo.text}</span>
          <button type="button" onClick={onCancelReply} aria-label="Batalkan balasan">×</button>
        </div>
      )}
      <label className="sr-only" htmlFor="message">Tulis pesan</label>
      <textarea
        ref={inputRef}
        id="message"
        rows="1"
        value={draft}
        onChange={(event) => setDraft(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault()
            event.currentTarget.form.requestSubmit()
          }
        }}
        placeholder="Tulis pertanyaan..."
        autoFocus
      />
      <button type="submit" aria-label="Kirim pesan" disabled={disabled || !draft.trim()}>
        <SendIcon />
      </button>
    </form>
  )
}
