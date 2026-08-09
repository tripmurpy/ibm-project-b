const messageTime = (date = new Date()) => date.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })

export default class ChatMessage {
  constructor({ id = crypto.randomUUID(), from, text, time = messageTime(), status = 'completed', citations = [], agent = null, replyTo = null }) {
    const normalizedText = text.trim()

    if (!['assistant', 'user'].includes(from)) {
      throw new TypeError(`Unknown message sender: ${from}`)
    }

    if (!normalizedText) {
      throw new TypeError('Message text cannot be empty')
    }

    this.id = id
    this.from = from
    this.text = normalizedText
    this.time = time
    this.status = status
    this.citations = citations.filter((citation, index, all) => (
      all.findIndex((candidate) => (
        candidate.source_title === citation.source_title
        && candidate.page_start === citation.page_start
        && candidate.page_end === citation.page_end
      )) === index
    ))
    this.agent = agent
    this.replyTo = replyTo
  }

  static fromUser(text, replyTo = null) {
    return new ChatMessage({ from: 'user', text, replyTo })
  }

  static pending(id) {
    return new ChatMessage({ id, from: 'assistant', text: 'Sedang mencari sumber yang relevan…', status: 'processing' })
  }

  static welcome() {
    return new ChatMessage({
      id: 'welcome',
      from: 'assistant',
      text: 'Hai, Bu. Ceritakan saja yang sedang Ibu pikirkan tentang si kecil. Saya bisa membantu mencari informasi kesehatan ringan atau menu dari buku yang tersedia.',
    })
  }

  static fromAssistant({ id, answer, citations = [], status = 'completed', agent = null, replyTo = null }) {
    return new ChatMessage({ id, from: 'assistant', text: answer, citations, status, agent, replyTo })
  }
}
