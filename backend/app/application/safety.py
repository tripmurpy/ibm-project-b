from dataclasses import dataclass
import re

from app.domain.models import AgentRequest, Intent, SafetyLevel


@dataclass(frozen=True)
class SafetyDecision:
    safety_level: SafetyLevel
    intent: Intent | None = None
    message: str | None = None


class SafetyPolicy:
    """Deterministic first gate; it must run before retrieval or model calls."""

    _urgent_terms = (
        "sulit bernapas", "sesak napas", "tidak bernapas", "tidak bisa bernapas", "tidak dapat bernapas",
        "bibir membiru", "bibir kebiruan", "kejang",
        "pingsan", "tidak sadar", "sulit dibangunkan", "tidak mau minum", "tidak bisa minum", "tidak kencing",
        "sangat lemas", "perdarahan hebat",
    )
    _screen_terms = (
        "demam", "batuk", "sakit tenggorokan", "sulit bernapas", "sesak napas", "sulit minum",
        "tidak mau minum", "tidak bisa minum", "lemas", "sangat lemas", "bibir membiru", "kejang",
    )
    _injection_terms = ("abaikan instruksi", "ignore previous", "system prompt")

    def assess(self, request: AgentRequest) -> SafetyDecision:
        question = request.question.casefold()
        if any(term in question and not self._is_negated_screen_term(question, term) for term in self._urgent_terms):
            return SafetyDecision(
                SafetyLevel.ESCALATE,
                Intent.ESCALATE,
                "Bu, kondisi ini perlu bantuan medis segera. Hubungi layanan darurat setempat atau bawa si kecil ke IGD sekarang.",
            )
        if any(term in question for term in self._injection_terms):
            return SafetyDecision(SafetyLevel.CAUTION, Intent.OUT_OF_SCOPE, "Saya hanya dapat membantu berdasarkan topik dan sumber yang disetujui.")
        return SafetyDecision(SafetyLevel.GENERAL)

    @classmethod
    def _is_negated_screen_term(cls, question: str, term: str) -> bool:
        terms = "|".join(re.escape(item) for item in cls._screen_terms)
        separators = r"\s*(?:,|\bdan\b|\batau\b)\s*"
        return bool(re.search(
            rf"\b(?:tidak|nggak|gak)\s+(?:ada\s+)?(?:(?:{terms}){separators})*{re.escape(term)}\b",
            question,
        ))
