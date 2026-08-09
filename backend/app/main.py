from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.application.agent import SpecialistAgent, SpecialistPolicy
from app.application.chat import ChatService
from app.application.router import IntentRouter
from app.application.safety import SafetyPolicy
from app.core.config import Settings
from app.infrastructure.cache import InMemoryChatCache
from app.infrastructure.providers import OpenAICompatibleGenerator, SupabaseKnowledgeRetriever
from app.infrastructure.unconfigured import GroundedGenerator, UnconfiguredRetriever

settings = Settings.from_environment()
retrieval_configured = bool(settings.supabase_url and settings.supabase_service_role_key)
llm_configured = bool(settings.llm_api_key)
retriever = (
    SupabaseKnowledgeRetriever(
        settings.supabase_url,
        settings.supabase_service_role_key,
        embedding_model=settings.embedding_model,
        timeout_seconds=settings.provider_timeout_seconds,
    )
    if retrieval_configured
    else UnconfiguredRetriever()
)
generator = (
    OpenAICompatibleGenerator(
        settings.llm_base_url,
        settings.llm_api_key,
        settings.llm_model,
        timeout_seconds=settings.provider_timeout_seconds,
    )
    if llm_configured
    else GroundedGenerator()
)
agents = {
    policy.agent: SpecialistAgent(
        policy,
        retriever,
        generator,
        max_question_length=settings.max_question_length,
        retrieval_top_k=settings.retrieval_top_k,
    )
    for policy in (SpecialistPolicy.mom(), SpecialistPolicy.koki_ben())
}
cache = InMemoryChatCache(
    ttl_seconds=settings.chat_cache_ttl_seconds,
    max_threads=settings.chat_cache_max_threads,
    history_messages=settings.chat_history_max_messages,
)
chat_service = ChatService(SafetyPolicy(), IntentRouter(), agents, cache)

app = FastAPI(title=settings.app_name)
app.add_middleware(CORSMiddleware, allow_origins=[origin.strip() for origin in settings.cors_origin.split(",") if origin.strip()], allow_credentials=True, allow_methods=["POST"], allow_headers=["*"])
app.include_router(router)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "retrieval": "configured" if retrieval_configured else "unconfigured",
        "llm": "configured" if llm_configured else "unconfigured",
        "cache": "memory-ttl",
    }
