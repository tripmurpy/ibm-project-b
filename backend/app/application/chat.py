from uuid import uuid4

from app.application.agent import SpecialistAgent
from app.application.ports import ChatCache
from app.application.router import IntentRouter
from app.application.safety import SafetyPolicy
from app.domain.models import AgentName, AgentRequest, AgentResponse, ChatResult, Intent, SafetyLevel


class ChatService:
    """Deterministic coordinator for safety, routing, and agent-scoped context."""

    def __init__(
        self,
        safety_policy: SafetyPolicy,
        router: IntentRouter,
        agents: dict[AgentName, SpecialistAgent],
        cache: ChatCache,
    ) -> None:
        self._safety_policy = safety_policy
        self._router = router
        self._agents = agents
        self._cache = cache

    async def handle(self, *, request_id: str, thread_id: str | None, question: str, reply_to: str | None = None) -> ChatResult:
        cached = await self._cache.get_response(request_id)
        if cached:
            return cached

        thread_id = thread_id or str(uuid4())
        request = AgentRequest(question=question.strip(), thread_id=thread_id, request_id=request_id)
        safety = self._safety_policy.assess(request)
        if safety.intent:
            responses = (self._platform_response(safety.message, safety.intent, safety.safety_level),)
            route = safety.intent
        else:
            active_agent = await self._cache.get_active_agent(thread_id)
            route = self._router.route(request, fallback=self._intent_for(active_agent) if active_agent else None)

            agent_names = self._agent_names(route)
            if not agent_names:
                responses = (self._platform_response("Apa keluhan utama si kecil, Bu?", Intent.CLARIFY),)
                route = Intent.CLARIFY
            else:
                responses = tuple(
                    [
                        await self._agents[agent].answer(
                            AgentRequest(
                                question=request.question,
                                thread_id=thread_id,
                                history=await self._cache.get_history(thread_id, agent)
                                + ((f"reply_to: {reply_to}",) if reply_to else ()),
                                request_id=request_id,
                            )
                        )
                        for agent in agent_names
                    ]
                )

        result = ChatResult(request_id, thread_id, str(uuid4()), route, responses)
        await self._cache.record(result, request.question)
        return result

    @staticmethod
    def _intent_for(agent: AgentName) -> Intent:
        return Intent.KNOWLEDGE if agent is AgentName.MOM else Intent.RECIPE

    @staticmethod
    def _agent_names(intent: Intent) -> tuple[AgentName, ...]:
        return {
            Intent.KNOWLEDGE: (AgentName.MOM,),
            Intent.RECIPE: (AgentName.KOKI_BEN,),
            Intent.MIXED: (AgentName.MOM, AgentName.KOKI_BEN),
        }.get(intent, ())

    @staticmethod
    def _platform_response(
        message: str | None,
        intent: Intent,
        safety_level: SafetyLevel = SafetyLevel.GENERAL,
    ) -> AgentResponse:
        answer = message or "Maaf, Bu. Saya hanya bisa membantu topik kesehatan ringan dan resep anak."
        return AgentResponse(
            agent=AgentName.MOM,
            answer=answer,
            safety_level=safety_level,
            intent=intent,
            needs_clarification=intent is Intent.CLARIFY,
            escalation_message=answer if intent is Intent.ESCALATE else None,
        )
