from dataclasses import dataclass
import json
import re
from re import Pattern

from app.application.ports import (
    AnswerGenerator,
    ConversationWriter,
    GenerationUnavailableError,
    KnowledgeRetriever,
    RetrievalUnavailableError,
)
from app.domain.models import AgentName, AgentRequest, AgentResponse, Intent, KnowledgeChunk, SafetyLevel


NUMBER_PATTERN = r"(?:\d{1,2}|satu|dua|tiga|empat|lima|enam|tujuh|delapan|sembilan|sepuluh|sebelas|dua\s+belas)"
NUMBER_VALUES = {
    word: value
    for value, word in enumerate(
        ("nol", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh", "delapan", "sembilan", "sepuluh", "sebelas", "dua belas")
    )
}
SHORT_NUMBER_PATTERN = re.compile(rf"^{NUMBER_PATTERN}$", re.I)
AGE_PATTERN = re.compile(rf"\b{NUMBER_PATTERN}\s*(?:bulan|bln|tahun|thn)\b", re.I)
DURATION_PATTERN = re.compile(
    rf"\b(?:sejak|tadi|kemarin|baru|{NUMBER_PATTERN}\s*(?:jam|hari|minggu))\b", re.I
)
COMPLAINT_PATTERN = re.compile(
    r"\b(?:demam|panas|batuk|pilek|muntah|diare|mencret|sakit\s+(?:perut|kepala|tenggorokan)|"
    r"ruam|flu|sembelit|lemas|rewel|gatal|dehidrasi|anemia|tidak\s+mau\s+makan|susah\s+tidur)\b",
    re.I,
)
RECURRENCE_PATTERN = re.compile(r"\b(?:sering|berulang|kambuh|bolak-balik)\b|\b([a-z]+)\s+\1\b", re.I)
ALLERGY_STATUS_PATTERN = re.compile(
    r"\b(?:(?:tidak|nggak|gak)\s+(?:ada|punya)\s+alergi|alergi\s+(?!belum\b|makanan\b|tidak\s+tahu\b)[a-z])",
    re.I,
)
SYMPTOM_SCREEN_MARKERS = ("apakah si kecil juga mengalami", "selain itu, apakah ada")
FREQUENCY_MARKER = "berapa kali si kecil mengalami"
BEVERAGE_PATTERN = re.compile(r"\b(?:smoothie|jus|minuman|milkshake|teh|es\s+mentimun)\b", re.I)


def normalize_user_text(text: str) -> str:
    return re.sub(r"\b([a-z]+)2\b", r"\1 \1", text, flags=re.I)


@dataclass(frozen=True)
class RequiredFact:
    pattern: Pattern[str]
    question: str


@dataclass(frozen=True)
class SpecialistPolicy:
    """Agent-owned rules consumed by one shared, traceable workflow."""

    agent: AgentName
    intent: Intent
    allowed_content_types: frozenset[str]
    required_facts: tuple[RequiredFact, ...]
    unsafe_output_terms: tuple[str, ...]

    @classmethod
    def mom(cls) -> "SpecialistPolicy":
        return cls(
            AgentName.MOM,
            Intent.KNOWLEDGE,
            frozenset({"health", "tip", "nutrition"}),
            (
                RequiredFact(COMPLAINT_PATTERN, "Apa keluhan utama si kecil, Bu?"),
                RequiredFact(AGE_PATTERN, "Usia si kecil berapa, Bu?"),
                RequiredFact(DURATION_PATTERN, "Keluhannya sudah berapa lama, Bu?"),
            ),
            ("diagnosisnya", "dosisnya"),
        )

    @classmethod
    def koki_ben(cls) -> "SpecialistPolicy":
        return cls(
            AgentName.KOKI_BEN,
            Intent.RECIPE,
            frozenset({"recipe"}),
            (
                RequiredFact(AGE_PATTERN, "Usia si kecil berapa, Bu?"),
                RequiredFact(ALLERGY_STATUS_PATTERN, "Si kecil punya alergi makanan, Bu?"),
            ),
            ("menyembuhkan", "mengobati", "meredakan", "menenangkan tenggorokan", "membantu pemulihan"),
        )

    def next_question(self, request: AgentRequest) -> str | None:
        user_context = self._user_context(request)
        if self.agent is AgentName.MOM:
            return self._mom_question(request, user_context)
        return self._koki_question(request, user_context)

    def _koki_question(self, request: AgentRequest, user_context: str) -> str | None:
        if not AGE_PATTERN.search(user_context):
            if self._answers_last_question(request, "usia") and SHORT_NUMBER_PATTERN.fullmatch(request.question.strip()):
                return f"Maksud Ibu {request.question.strip()} tahun atau bulan?"
            return f"Baik, Bu. Saya bantu carikan {self._recipe_request_summary(request)}. Boleh tahu usia si kecil berapa, Bu?"
        if ALLERGY_STATUS_PATTERN.search(user_context) or self._negative_allergy_reply(request):
            return None
        if self._answers_last_question(request, "alergi") and re.fullmatch(r"(?:ada|punya)(?:\s+(?:dok|bu))?", request.question.strip(), re.I):
            return "Alergi terhadap bahan apa, Bu?"
        summary = self._recipe_request_summary(request)
        return f"Baik, Bu. Saya paham Ibu mencari {summary}. Sebelum saya pilihkan, si kecil punya alergi makanan, Bu?"

    def _mom_question(self, request: AgentRequest, user_context: str) -> str | None:
        complaint = COMPLAINT_PATTERN.search(user_context)
        if not complaint:
            return "Saya dengarkan, Bu. Apa yang paling mengganggu si kecil sekarang?"

        complaint_text = complaint.group(0).casefold()
        age = AGE_PATTERN.search(user_context)
        if not age:
            if self._answers_last_question(request, "usia") and SHORT_NUMBER_PATTERN.fullmatch(request.question.strip()):
                return f"Maksud Ibu {request.question.strip()} tahun atau bulan?"
            return (
                f"{complaint_text.capitalize()} pada si kecil pasti Ibu jadi kepikiran, ya. "
                "Agar informasinya sesuai, boleh tahu usia si kecil berapa, Bu?"
            )

        duration = DURATION_PATTERN.search(user_context)
        if not duration:
            if self._answers_last_question(request, "sejak kapan") and SHORT_NUMBER_PATTERN.fullmatch(request.question.strip()):
                return f"Maksud Ibu sudah {request.question.strip()} hari, jam, atau minggu?"
            return f"Baik, si kecil berusia {age.group(0).casefold()}. {complaint_text.capitalize()}nya mulai sejak kapan, Bu?"

        assistant_context = " ".join(
            line.removeprefix("assistant: ").casefold()
            for line in request.history
            if line.startswith("assistant: ")
        )
        if not any(marker in assistant_context for marker in SYMPTOM_SCREEN_MARKERS):
            return (
                f"Baik, {complaint_text}nya sudah sekitar {duration.group(0).casefold()}. Selain itu, apakah ada demam, "
                "batuk, sakit tenggorokan, sulit bernapas, sulit minum, atau si kecil terlihat jauh lebih lemas, Bu?"
            )

        if RECURRENCE_PATTERN.search(user_context) and FREQUENCY_MARKER not in assistant_context:
            return f"Karena Ibu bilang ini sering terjadi, dalam beberapa minggu atau bulan terakhir kira-kira sudah berapa kali si kecil mengalami {complaint_text}, Bu?"
        return None

    def safe_context(self, request: AgentRequest, context: list[KnowledgeChunk]) -> list[KnowledgeChunk]:
        accepted = [chunk for chunk in context if chunk.content_type in self.allowed_content_types]
        if self.agent is AgentName.KOKI_BEN and self._age_months(request) < 12:
            return []
        if self.agent is AgentName.KOKI_BEN:
            target_condition = self.target_condition(request)
            if target_condition:
                accepted = [
                    chunk for chunk in accepted
                    if not chunk.entity_payload.get("target_condition")
                    or chunk.entity_payload.get("target_condition") == target_condition
                ]
            if self._wants_solid_food(request):
                accepted = [
                    chunk for chunk in accepted
                    if not BEVERAGE_PATTERN.search(str(chunk.entity_payload.get("title") or chunk.content))
                ]
        allergens = self._allergens(request) if self.agent is AgentName.KOKI_BEN else ()
        if not allergens:
            return accepted[:1] if self.agent is AgentName.KOKI_BEN else accepted
        return [
            chunk
            for chunk in accepted
            if isinstance(chunk.entity_payload.get("ingredients"), list)
            and chunk.entity_payload["ingredients"]
            and not any(
                allergen in f"{chunk.content} {json.dumps(chunk.entity_payload, ensure_ascii=False)}".casefold()
                for allergen in allergens
            )
        ][:1]

    def output_is_safe(self, answer: str) -> bool:
        normalized = answer.casefold()
        clinical_certainty = re.search(
            r"\b(?:pasti|tampaknya|kemungkinan besar)\s+(?:masih\s+)?(?:flu|pilek|demam|infeksi|alergi|sembuh|aman|normal|wajar|ringan)\b|"
            r"\b(?:kondisi(?:nya| ini)?|si kecil)\s+(?:terdengar|terlihat|tampak)\s+(?:stabil|aman|normal|wajar|ringan)\b|"
            r"\bkondisi ini\s+(?:biasanya|umumnya)(?:\s+\w+){0,5}\s+(?:ringan|aman|membaik)\b|"
            r"\b(?:senang|lega)\s+mendengar\b|"
            r"\b(?:batuk|pilek|demam|diare)\b[^.!?]{0,80}\b(?:memang|sering|umumnya)\s+(?:sering\s+)?terjadi\b|"
            r"\bkarena tidak ada\b[^.!?]{0,120}\b(?:langkah|disarankan|perawatan|cukup minum)\b|"
            r"\b(?:dalam batas wajar|kabar baik|tidak ada gejala berat|umumnya (?:tidak serius|bisa membaik)|"
            r"membantu pemulihan|bisa terus memantau|senang mendengar|tidak ada tanda-tanda bahaya|"
            r"kondisinya stabil|perjalanan penyakit yang umum|membantu tubuh melawan virus)\b",
            normalized,
        )
        return not clinical_certainty and not any(term in normalized for term in self.unsafe_output_terms)

    def remove_unsafe_sentences(self, answer: str) -> str:
        return " ".join(
            sentence for sentence in re.split(r"(?<=[.!?])\s+", answer) if self.output_is_safe(sentence)
        ).strip()

    @staticmethod
    def clean_output(answer: str) -> str:
        answer = re.sub(r"[\U0001F300-\U0001FAFF\u2700-\u27BF]", "", answer)
        answer = re.sub(r"(?m)^\s*#{1,6}\s*|^\s*-{3,}\s*$", "", answer)
        return answer.replace("**", "").strip()

    @staticmethod
    def format_health(chunk: KnowledgeChunk) -> str:
        lines = chunk.content.strip().splitlines()
        if lines and lines[0].startswith("# "):
            lines = lines[1:]
        return "Berikut informasi umum dari buku yang tersedia:\n\n" + "\n".join(lines).strip()

    @staticmethod
    def _user_context(request: AgentRequest) -> str:
        return normalize_user_text(" ".join(
            [line.removeprefix("user: ") for line in request.history if line.startswith("user: ")]
            + [request.question]
        ))

    @staticmethod
    def _answers_last_question(request: AgentRequest, marker: str) -> bool:
        return bool(request.history and request.history[-1].startswith("assistant: ") and marker in request.history[-1].casefold())

    def _negative_allergy_reply(self, request: AgentRequest) -> bool:
        return self._answers_last_question(request, "alergi") and bool(re.fullmatch(
            r"(?:tidak|nggak|gak)(?:\s+(?:ada|punya))?(?:\s+(?:dok|bu))?",
            request.question.strip(),
            re.I,
        ))

    def _allergens(self, request: AgentRequest) -> tuple[str, ...]:
        user_context = self._user_context(request).casefold()
        if re.search(r"\b(?:tidak|nggak|gak)\s+(?:ada|punya)\s+alergi\b", user_context):
            return ()
        clauses = re.findall(r"\balergi(?:\s+(?:terhadap|pada))?\s+([^.,;]+)", user_context)
        allergens = []
        for clause in clauses:
            clause = re.split(
                rf"\b(?:untuk|sejak|karena|anak|mau|resep|menu|usia)\b|{AGE_PATTERN.pattern}",
                clause,
                maxsplit=1,
            )[0]
            allergens.extend(item.strip() for item in re.split(r"\s+(?:dan|atau)\s+|/", clause) if item.strip())
        return tuple(dict.fromkeys(allergens))

    @staticmethod
    def target_condition(request: AgentRequest) -> str | None:
        context = SpecialistPolicy._user_context(request).casefold()
        if re.search(r"\b(?:batuk|pilek)\b", context):
            return "batuk pilek"
        if re.search(r"\b(?:flu|influenza)\b", context):
            return "influenza"
        if "tifus" in context:
            return "tifus"
        return None

    def _recipe_request_summary(self, request: AgentRequest) -> str:
        form = "makanan" if self._wants_solid_food(request) else "menu"
        condition = self.target_condition(request)
        return f"{form} untuk kondisi {condition}" if condition else form

    @staticmethod
    def _wants_solid_food(request: AgentRequest) -> bool:
        context = SpecialistPolicy._user_context(request).casefold()
        return "makanan" in context and not BEVERAGE_PATTERN.search(context)

    @staticmethod
    def format_recipe(chunk: KnowledgeChunk) -> str | None:
        payload = chunk.entity_payload
        title = payload.get("title")
        ingredients = payload.get("ingredients")
        instructions = payload.get("instructions")
        notes = payload.get("notes") or []
        if not isinstance(title, str) or not title.strip():
            return None
        if not isinstance(ingredients, list) or not ingredients or not all(isinstance(item, str) and item.strip() for item in ingredients):
            return None
        if not isinstance(instructions, list) or not instructions or not all(isinstance(item, str) and item.strip() for item in instructions):
            return None
        if not isinstance(notes, list) or not all(isinstance(item, str) and item.strip() for item in notes):
            return None
        steps = [step if re.match(r"^\d+[.)]\s", step) else f"{index}. {step}" for index, step in enumerate(instructions, 1)]
        sections = [
            f"Judul: {title.strip()}",
            "Bahan:\n" + "\n".join(f"- {item.strip()}" for item in ingredients),
            "Cara membuat:\n" + "\n".join(steps),
        ]
        if notes:
            sections.append("Catatan:\n" + "\n".join(f"- {item.strip()}" for item in notes))
        return "\n\n".join(sections)

    def _age_months(self, request: AgentRequest) -> int:
        match = AGE_PATTERN.search(self._user_context(request))
        if not match:
            return 0
        amount_text = re.match(NUMBER_PATTERN, match.group(0), re.I).group(0).casefold()
        amount = int(amount_text) if amount_text.isdigit() else NUMBER_VALUES[amount_text]
        return amount if re.search(r"\b(?:bulan|bln)\b", match.group(0), re.I) else amount * 12


class SpecialistAgent:
    """One workflow, two policies; common logic is never copied between agents."""

    def __init__(
        self,
        policy: SpecialistPolicy,
        retriever: KnowledgeRetriever,
        generator: AnswerGenerator,
        conversation_writer: ConversationWriter | None = None,
        *,
        max_question_length: int = 2_000,
        retrieval_top_k: int = 5,
    ) -> None:
        self._policy = policy
        self._retriever = retriever
        self._generator = generator
        self._conversation_writer = conversation_writer
        self._max_question_length = max_question_length
        self._retrieval_top_k = retrieval_top_k

    async def answer(self, request: AgentRequest) -> AgentResponse:
        question = request.question.strip()
        if not question or len(question) > self._max_question_length:
            return self._response("Boleh tulis pertanyaannya lebih singkat, Bu?", Intent.CLARIFY, needs_clarification=True)

        request = AgentRequest(question, request.thread_id, request.user_id, request.history, request.request_id)
        if follow_up := self._policy.next_question(request):
            return self._response(follow_up, Intent.CLARIFY, needs_clarification=True)

        try:
            context = await self._retriever.search(
                self._retrieval_query(request),
                intent=self._policy.intent,
                top_k=self._retrieval_top_k,
                target_condition=self._policy.target_condition(request) if self._policy.intent is Intent.RECIPE else None,
            )
        except RetrievalUnavailableError:
            return self._response("Sumber sedang sulit dibuka, Bu. Coba lagi sebentar, ya.", self._policy.intent, SafetyLevel.CAUTION)
        context = self._policy.safe_context(request, context)
        if not context:
            if self._policy.agent is AgentName.KOKI_BEN and self._policy._age_months(request) < 12:
                return self._response(
                    "Maaf, Bu. Untuk si kecil di bawah 1 tahun, saya belum bisa menyarankan resep dari buku ini "
                    "dengan aman karena setiap bayi membutuhkan penyesuaian tekstur dan tahap makan.",
                    self._policy.intent,
                    SafetyLevel.CAUTION,
                )
            return self._response(
                "Terima kasih sudah menjelaskan kondisinya, Bu. Maaf, saya belum menemukan informasi yang cukup "
                "dari buku yang tersedia untuk menjawab dengan aman.",
                self._policy.intent,
                SafetyLevel.CAUTION,
            )

        if self._policy.agent is AgentName.MOM:
            answer = self._policy.format_health(context[0])
            citations = (context[0].citation,)
            if self._conversation_writer:
                await self._conversation_writer.save(request, answer, citations)
            return self._response(answer, self._policy.intent, citations=citations)

        if self._policy.agent is AgentName.KOKI_BEN:
            answer = self._policy.format_recipe(context[0])
            if not answer:
                return self._response(
                    "Saya menemukan resep yang berkaitan, Bu, tetapi data bahan atau langkahnya belum lengkap. "
                    "Saya tidak akan menebak bagian yang hilang.",
                    self._policy.intent,
                    SafetyLevel.CAUTION,
                )
        else:
            try:
                answer = await self._generator.generate(
                    request, context, agent=self._policy.agent, safety_level=SafetyLevel.GENERAL
                )
            except GenerationUnavailableError:
                return self._response("Layanan sedang sibuk, Bu. Coba kirim lagi sebentar, ya.", self._policy.intent, SafetyLevel.CAUTION)
        answer = self._policy.clean_output(answer)
        if not self._policy.output_is_safe(answer):
            answer = self._policy.remove_unsafe_sentences(answer)
        if not answer and self._policy.agent is AgentName.MOM:
            try:
                answer = await self._generator.generate(
                    AgentRequest(
                        question=(
                            f"{request.question}\n\nTulis ulang jawaban hanya dari EVIDENCE. Jangan menyimpulkan "
                            "penyebab, keamanan, prognosis, atau rencana pemantauan untuk kondisi anak ini. Jangan "
                            "menggunakan kalimat seperti 'kabar baik', 'akan membaik', atau 'karena kondisi anak'."
                        ),
                        thread_id=request.thread_id,
                        user_id=request.user_id,
                        history=request.history,
                        request_id=request.request_id,
                    ),
                    context,
                    agent=self._policy.agent,
                    safety_level=SafetyLevel.GENERAL,
                )
                answer = self._policy.clean_output(answer)
                if not self._policy.output_is_safe(answer):
                    answer = self._policy.remove_unsafe_sentences(answer)
            except GenerationUnavailableError:
                answer = ""
        if not answer or not self._policy.output_is_safe(answer):
            return self._response(
                "Saya menemukan sumber yang berkaitan, Bu, tetapi susunan jawaban tadi memuat kesimpulan yang tidak "
                "didukung sumber. Saya tidak akan meneruskan bagian itu. Boleh coba tanyakan dengan kalimat yang lebih spesifik?",
                self._policy.intent,
                SafetyLevel.CAUTION,
            )
        citations = tuple(chunk.citation for chunk in context)
        if self._conversation_writer:
            await self._conversation_writer.save(request, answer, citations)
        return self._response(answer, self._policy.intent, citations=citations)

    @staticmethod
    def _retrieval_query(request: AgentRequest) -> str:
        previous_questions = [line.removeprefix("user: ") for line in request.history if line.startswith("user: ")]
        return normalize_user_text(" ".join(previous_questions + [request.question]))

    def _response(
        self,
        answer: str,
        intent: Intent,
        safety_level: SafetyLevel = SafetyLevel.GENERAL,
        *,
        citations=(),
        needs_clarification: bool = False,
        offers_handoff: bool = False,
    ) -> AgentResponse:
        return AgentResponse(
            agent=self._policy.agent,
            answer=answer,
            safety_level=safety_level,
            intent=intent,
            citations=tuple(citations),
            needs_clarification=needs_clarification,
            offers_handoff=offers_handoff,
        )
