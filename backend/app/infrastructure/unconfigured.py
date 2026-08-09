from app.domain.models import AgentName, AgentRequest, Intent, KnowledgeChunk, SafetyLevel


class UnconfiguredRetriever:
    """Safe startup adapter until the Supabase hybrid-retrieval adapter is configured."""

    async def search(
        self, query: str, *, intent: Intent, top_k: int, target_condition: str | None = None
    ) -> list[KnowledgeChunk]:
        return []


class GroundedGenerator:
    """Provider seam; a real LLM adapter must only receive retrieved context."""

    async def generate(
        self,
        request: AgentRequest,
        context: list[KnowledgeChunk],
        *,
        agent: AgentName,
        safety_level: SafetyLevel,
    ) -> str:
        return "Saya belum dikonfigurasi untuk menyusun jawaban dari sumber buku."
