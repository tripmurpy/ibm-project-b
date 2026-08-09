from app.domain.models import AgentRequest, Intent


class IntentRouter:
    """Small deterministic router; replace only after evaluation proves a model router is needed."""

    _recipe_terms = ("resep", "masak", "menu", "makanan", "makan apa")
    _care_terms = ("cara merawat", "cara menangani", "atasi", "perawatan", "harus bagaimana")
    _health_terms = ("demam", "panas", "batuk", "pilek", "muntah", "diare", "mencret", "ruam", "flu")
    def route(self, request: AgentRequest, *, fallback: Intent | None = None) -> Intent:
        question = request.question.casefold().strip()
        wants_recipe = any(term in question for term in self._recipe_terms)
        wants_care = any(term in question for term in self._care_terms)
        mentions_health = any(term in question for term in self._health_terms)
        if wants_recipe and wants_care:
            return Intent.MIXED
        if wants_recipe:
            return Intent.RECIPE
        if wants_care or mentions_health:
            return Intent.KNOWLEDGE
        if fallback:
            return fallback
        if len(question) < 8:
            return Intent.CLARIFY
        return Intent.KNOWLEDGE
