from dataclasses import dataclass
import os
from pathlib import Path


def _runtime_environment() -> dict[str, str]:
    values = dict(os.environ)
    env_file = Path(__file__).parents[3] / ".env"
    if env_file.exists():
        for raw_line in env_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values.setdefault(key.strip(), value.strip().strip("\"'"))
    return values


@dataclass(frozen=True)
class Settings:
    """Runtime configuration kept outside application code."""

    app_name: str = "Teman Tumbuh API"
    cors_origin: str = "http://localhost:5173,http://127.0.0.1:5173"
    max_question_length: int = 2_000
    retrieval_top_k: int = 5
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    llm_base_url: str = "https://api.groq.com/openai/v1"
    llm_api_key: str = ""
    llm_model: str = "qwen/qwen3.6-27b"
    embedding_model: str = "BAAI/bge-m3"
    provider_timeout_seconds: float = 45
    chat_cache_ttl_seconds: int = 1_800
    chat_cache_max_threads: int = 1_000
    chat_history_max_messages: int = 20

    @classmethod
    def from_environment(cls) -> "Settings":
        env = _runtime_environment()
        return cls(
            cors_origin=env.get("CORS_ORIGIN", cls.cors_origin),
            max_question_length=int(env.get("MAX_QUESTION_LENGTH", cls.max_question_length)),
            retrieval_top_k=int(env.get("RETRIEVAL_TOP_K", cls.retrieval_top_k)),
            supabase_url=(
                env.get("SUPABASE_PROJECT_URL")
                or env.get("VITE_SUPABASE_URL")
                or env.get("SUPABASE_PROJECT_UR")
                or ""
            ),
            supabase_service_role_key=env.get("SUPABASE_SERVICE_ROLE_KEY", ""),
            llm_base_url=env.get("LLM_BASE_URL", cls.llm_base_url),
            llm_api_key=env.get("LLM_API_KEY") or env.get("OPENAI_API_KEY", ""),
            llm_model=env.get("LLM_MODEL", cls.llm_model),
            embedding_model=env.get("EMBEDDING_MODEL", cls.embedding_model),
            provider_timeout_seconds=float(env.get("PROVIDER_TIMEOUT_SECONDS", cls.provider_timeout_seconds)),
            chat_cache_ttl_seconds=int(env.get("CHAT_CACHE_TTL_SECONDS", cls.chat_cache_ttl_seconds)),
            chat_cache_max_threads=int(env.get("CHAT_CACHE_MAX_THREADS", cls.chat_cache_max_threads)),
            chat_history_max_messages=int(env.get("CHAT_HISTORY_MAX_MESSAGES", cls.chat_history_max_messages)),
        )
