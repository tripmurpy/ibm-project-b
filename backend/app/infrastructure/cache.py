import asyncio
from collections import OrderedDict, deque
from dataclasses import replace
from time import monotonic

from app.domain.models import AgentName, ChatResult


class InMemoryChatCache:
    """TTL cache with one seamless short-term history per chat thread."""

    def __init__(self, *, ttl_seconds: int, max_threads: int, history_messages: int) -> None:
        self._ttl = ttl_seconds
        self._max_threads = max_threads
        self._history_messages = history_messages
        self._histories: OrderedDict[str, tuple[float, deque[str]]] = OrderedDict()
        self._responses: OrderedDict[str, tuple[float, ChatResult]] = OrderedDict()
        self._active_agents: OrderedDict[str, tuple[float, AgentName]] = OrderedDict()
        self._lock = asyncio.Lock()

    async def get_history(self, thread_id: str, agent: AgentName) -> tuple[str, ...]:
        async with self._lock:
            item = self._histories.get(thread_id)
            if not item or item[0] <= monotonic():
                self._histories.pop(thread_id, None)
                return ()
            self._histories.move_to_end(thread_id)
            return tuple(item[1])

    async def get_active_agent(self, thread_id: str) -> AgentName | None:
        async with self._lock:
            item = self._active_agents.get(thread_id)
            if not item or item[0] <= monotonic():
                self._active_agents.pop(thread_id, None)
                return None
            self._active_agents.move_to_end(thread_id)
            return item[1]

    async def get_response(self, request_id: str) -> ChatResult | None:
        async with self._lock:
            item = self._responses.get(request_id)
            if not item or item[0] <= monotonic():
                self._responses.pop(request_id, None)
                return None
            self._responses.move_to_end(request_id)
            return replace(item[1], cache_hit=True)

    async def record(self, result: ChatResult, question: str) -> None:
        async with self._lock:
            expires_at = monotonic() + self._ttl
            item = self._histories.get(result.thread_id)
            history = item[1] if item else deque(maxlen=self._history_messages)
            history.append(f"user: {question}")
            history.extend(f"assistant: {response.answer}" for response in result.responses)
            self._histories[result.thread_id] = (expires_at, history)
            self._histories.move_to_end(result.thread_id)

            clarifying = next((response.agent for response in result.responses if response.needs_clarification), None)
            active = clarifying or (result.responses[0].agent if len(result.responses) == 1 else None)
            if active:
                self._active_agents[result.thread_id] = (expires_at, active)
                self._active_agents.move_to_end(result.thread_id)

            self._responses[result.request_id] = (expires_at, result)
            self._responses.move_to_end(result.request_id)

            # ponytail: process-local LRU remains enough until deployment adds replicas.
            self._trim(self._histories, self._max_threads * 2)
            self._trim(self._active_agents, self._max_threads)
            self._trim(self._responses, self._max_threads * 2)

    @staticmethod
    def _trim(items: OrderedDict, limit: int) -> None:
        while len(items) > limit:
            items.popitem(last=False)
