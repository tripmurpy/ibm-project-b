from typing import Protocol

from app.domain.models import AgentName, AgentRequest, ChatResult, Citation, Intent, KnowledgeChunk, SafetyLevel


class RetrievalUnavailableError(RuntimeError):
    pass


class GenerationUnavailableError(RuntimeError):
    pass


class KnowledgeRetriever(Protocol):
    async def search(
        self, query: str, *, intent: Intent, top_k: int, target_condition: str | None = None
    ) -> list[KnowledgeChunk]: ...


class AnswerGenerator(Protocol):
    async def generate(
        self,
        request: AgentRequest,
        context: list[KnowledgeChunk],
        *,
        agent: AgentName,
        safety_level: SafetyLevel,
    ) -> str: ...


class ConversationWriter(Protocol):
    async def save(self, request: AgentRequest, response: str, citations: tuple[Citation, ...]) -> None: ...


class ChatCache(Protocol):
    async def get_history(self, thread_id: str, agent: AgentName) -> tuple[str, ...]: ...

    async def get_active_agent(self, thread_id: str) -> AgentName | None: ...

    async def get_response(self, request_id: str) -> ChatResult | None: ...

    async def record(self, result: ChatResult, question: str) -> None: ...
