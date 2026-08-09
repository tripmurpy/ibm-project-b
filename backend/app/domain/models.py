from dataclasses import dataclass, field
from enum import StrEnum


class SafetyLevel(StrEnum):
    GENERAL = "general"
    CAUTION = "caution"
    ESCALATE = "escalate"


class AgentName(StrEnum):
    MOM = "mom"
    KOKI_BEN = "koki_ben"


class Intent(StrEnum):
    KNOWLEDGE = "knowledge"
    RECIPE = "recipe"
    MIXED = "mixed"
    CLARIFY = "clarify"
    ESCALATE = "escalate"
    OUT_OF_SCOPE = "out_of_scope"


@dataclass(frozen=True)
class Citation:
    chunk_id: str
    source_title: str
    page_start: int | None = None
    page_end: int | None = None


@dataclass(frozen=True)
class KnowledgeChunk:
    id: str
    content: str
    citation: Citation
    content_type: str
    similarity: float
    entity_payload: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentRequest:
    question: str
    thread_id: str | None = None
    user_id: str | None = None
    history: tuple[str, ...] = ()
    request_id: str | None = None


@dataclass(frozen=True)
class AgentResponse:
    agent: AgentName
    answer: str
    safety_level: SafetyLevel
    intent: Intent
    citations: tuple[Citation, ...] = field(default_factory=tuple)
    needs_clarification: bool = False
    escalation_message: str | None = None
    offers_handoff: bool = False


@dataclass(frozen=True)
class ChatResult:
    request_id: str
    thread_id: str
    message_id: str
    route: Intent
    responses: tuple[AgentResponse, ...]
    cache_hit: bool = False
