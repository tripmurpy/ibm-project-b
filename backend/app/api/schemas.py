from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.domain.models import AgentResponse, ChatResult, Citation, SafetyLevel


class ChatRequest(BaseModel):
    request_id: UUID = Field(default_factory=uuid4)
    question: str = Field(min_length=1, max_length=2_000)
    thread_id: UUID | None = None
    reply_to: str | None = Field(default=None, max_length=2_000)


class CitationResponse(BaseModel):
    chunk_id: str
    source_title: str
    page_start: int | None
    page_end: int | None

    @classmethod
    def from_domain(cls, citation: Citation) -> "CitationResponse":
        return cls(
            chunk_id=citation.chunk_id,
            source_title=citation.source_title,
            page_start=citation.page_start,
            page_end=citation.page_end,
        )


class AgentSectionResponse(BaseModel):
    agent: str
    answer: str
    citations: list[CitationResponse]
    needs_clarification: bool
    offers_handoff: bool

    @classmethod
    def from_domain(cls, response: AgentResponse) -> "AgentSectionResponse":
        return cls(
            agent=response.agent,
            answer=response.answer,
            citations=[CitationResponse.from_domain(citation) for citation in response.citations],
            needs_clarification=response.needs_clarification,
            offers_handoff=response.offers_handoff,
        )


class ChatResponse(BaseModel):
    request_id: UUID
    thread_id: UUID
    message_id: UUID
    answer: str
    route: str
    intent: str
    sections: list[AgentSectionResponse]
    citations: list[CitationResponse]
    safety_level: str
    needs_clarification: bool
    escalation_message: str | None
    cache_hit: bool

    @classmethod
    def from_domain(cls, result: ChatResult) -> "ChatResponse":
        responses = result.responses
        citations = {
            citation.chunk_id: citation
            for response in responses
            for citation in response.citations
        }
        severity = {SafetyLevel.GENERAL: 0, SafetyLevel.CAUTION: 1, SafetyLevel.ESCALATE: 2}
        safety_level = max(responses, key=lambda response: severity[response.safety_level]).safety_level
        answer = "\n\n".join(response.answer for response in responses)
        return cls(
            request_id=UUID(result.request_id),
            thread_id=UUID(result.thread_id),
            message_id=UUID(result.message_id),
            answer=answer,
            route=result.route,
            intent=result.route,
            sections=[AgentSectionResponse.from_domain(response) for response in responses],
            citations=[CitationResponse.from_domain(citation) for citation in citations.values()],
            safety_level=safety_level,
            needs_clarification=any(response.needs_clarification for response in responses),
            escalation_message=next(
                (response.escalation_message for response in responses if response.escalation_message), None
            ),
            cache_hit=result.cache_hit,
        )
