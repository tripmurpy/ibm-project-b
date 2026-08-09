import unittest

from app.application.agent import SpecialistAgent, SpecialistPolicy
from app.application.ports import RetrievalUnavailableError
from app.domain.models import AgentName, AgentRequest, Citation, Intent, KnowledgeChunk, SafetyLevel
from app.infrastructure.providers import SYSTEM_PROMPTS


class FakeRetriever:
    def __init__(self) -> None:
        self.calls = []

    async def search(self, query, *, intent, top_k, target_condition=None):
        self.calls.append((query, intent, top_k, target_condition))
        content_type = "recipe" if intent is Intent.RECIPE else "health"
        return [
            KnowledgeChunk(
                id=f"{content_type}-1",
                content="Evidence yang sudah direview.",
                citation=Citation(f"{content_type}-1", "Buku Teman Tumbuh", 10, 10),
                content_type=content_type,
                similarity=0.9,
                entity_payload=(
                    {"title": "Menu Uji", "ingredients": ["nasi"], "instructions": ["Masak sampai matang."], "notes": []}
                    if content_type == "recipe" else {}
                ),
            )
        ]


class AllergyConflictRetriever:
    async def search(self, query, *, intent, top_k, target_condition=None):
        return [
            KnowledgeChunk(
                id="recipe-egg",
                content="Bubur dibuat memakai telur ayam.",
                citation=Citation("recipe-egg", "Buku Resep", 20, 20),
                content_type="recipe",
                similarity=1.0,
                entity_payload={"ingredients": ["1 butir telur"]},
            )
        ]


class TwoRecipeRetriever:
    async def search(self, query, *, intent, top_k, target_condition=None):
        return [
            KnowledgeChunk(
                id=f"recipe-{index}",
                content=f"Resep {index}",
                citation=Citation(f"recipe-{index}", "Buku Resep", index, index),
                content_type="recipe",
                similarity=1 / index,
                entity_payload={
                    "title": f"Resep {index}",
                    "ingredients": ["nasi"],
                    "instructions": ["Masak sampai matang."],
                    "notes": [],
                },
            )
            for index in (1, 2)
        ]


class FormAwareRecipeRetriever:
    def __init__(self) -> None:
        self.target_condition = None

    async def search(self, query, *, intent, top_k, target_condition=None):
        self.target_condition = target_condition
        return [
            KnowledgeChunk(
                id="smoothie",
                content="Smoothie avokad diminum dari gelas.",
                citation=Citation("smoothie", "Buku Resep", 10, 10),
                content_type="recipe",
                similarity=1.0,
                entity_payload={
                    "title": "Smoothie Avokad",
                    "target_condition": "batuk pilek",
                    "ingredients": ["avokad"],
                },
            ),
            KnowledgeChunk(
                id="nagasari",
                content="Nagasari adalah makanan untuk batuk pilek.",
                citation=Citation("nagasari", "Buku Resep", 11, 11),
                content_type="recipe",
                similarity=0.9,
                entity_payload={
                    "title": "Nagasari",
                    "target_condition": "batuk pilek",
                    "ingredients": ["pisang"],
                    "instructions": ["Kukus sampai matang."],
                    "notes": ["Sajikan hangat."],
                },
            ),
        ]


class NeverGenerator:
    async def generate(self, request, context, *, agent, safety_level):
        raise AssertionError("structured recipes must not be rewritten by an LLM")


class UnavailableRetriever:
    async def search(self, query, *, intent, top_k, target_condition=None):
        raise RetrievalUnavailableError("private provider detail")


class FakeGenerator:
    def __init__(self) -> None:
        self.calls = []

    async def generate(self, request, context, *, agent, safety_level):
        self.calls.append((request, context, agent, safety_level))
        return "Tenang ya, Bu. Ini jawaban dari sumber yang tersedia."


class DecorativeGenerator:
    async def generate(self, request, context, *, agent, safety_level):
        return "Tenang, Bu. Si kecil masih dapat dipantau. ✅"


class SpecialistAgentTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.retriever = FakeRetriever()
        self.generator = FakeGenerator()
        self.mom = SpecialistAgent(SpecialistPolicy.mom(), self.retriever, self.generator)
        self.koki = SpecialistAgent(SpecialistPolicy.koki_ben(), self.retriever, self.generator)

    async def test_mom_validates_the_problem_before_asking_age(self) -> None:
        response = await self.mom.answer(AgentRequest("Anak saya demam"))

        self.assertEqual(response.agent, AgentName.MOM)
        self.assertIn("pasti Ibu jadi kepikiran", response.answer)
        self.assertIn("Agar informasinya sesuai", response.answer)
        self.assertTrue(response.answer.endswith("usia si kecil berapa, Bu?"))
        self.assertTrue(response.needs_clarification)
        self.assertEqual(self.retriever.calls, [])

    async def test_mom_asks_one_concise_user_centered_question(self) -> None:
        response = await self.mom.answer(AgentRequest("Anak saya demam"))

        self.assertNotIn("membantu saya", response.answer.casefold())
        self.assertLessEqual(len(response.answer.split()), 30)
        self.assertEqual(response.answer.count("?"), 1)

    async def test_mom_understands_informal_repetition_and_follows_recurrent_flow(self) -> None:
        first = await self.mom.answer(AgentRequest("Anak saya sering pilek2, kenapa ya"))
        self.assertNotIn("keluhan utama", first.answer.casefold())
        self.assertIn("pilek", first.answer.casefold())
        self.assertTrue(first.answer.endswith("usia si kecil berapa, Bu?"))

        age_history = (
            "user: Anak saya sering pilek2, kenapa ya",
            f"assistant: {first.answer}",
        )
        second = await self.mom.answer(AgentRequest("5 tahun", history=age_history))
        self.assertIn("berusia 5 tahun", second.answer)
        self.assertIn("sejak kapan", second.answer)

        duration_history = age_history + ("user: 5 tahun", f"assistant: {second.answer}")
        third = await self.mom.answer(AgentRequest("sudah 2 hari", history=duration_history))
        self.assertIn("sekitar 2 hari", third.answer)
        self.assertIn("sulit bernapas", third.answer)

        symptom_history = duration_history + ("user: sudah 2 hari", f"assistant: {third.answer}")
        fourth = await self.mom.answer(AgentRequest("Tidak ada demam, hanya pilek", history=symptom_history))
        self.assertIn("sering", fourth.answer)
        self.assertIn("berapa kali", fourth.answer)

        frequency_history = symptom_history + (
            "user: Tidak ada demam, hanya pilek",
            f"assistant: {fourth.answer}",
        )
        final = await self.mom.answer(AgentRequest("sekitar 3 kali dalam 2 bulan", history=frequency_history))

        self.assertFalse(final.needs_clarification)
        self.assertEqual(len(self.retriever.calls), 1)

    async def test_mom_checks_associated_symptoms_before_searching_once(self) -> None:
        history = (
            "user: Anak dua tahun demam sejak dua hari",
            "assistant: Selama ini, apakah si kecil juga mengalami gejala lain atau terlihat jauh lebih lemas, Bu?",
        )
        response = await self.mom.answer(AgentRequest("Tidak ada, masih aktif dan mau minum", history=history))

        self.assertFalse(response.needs_clarification)
        self.assertEqual(len(self.retriever.calls), 1)

    async def test_mom_uses_follow_up_context_then_retrieves_once(self) -> None:
        history = (
            "user: Anak saya demam",
            "assistant: Usia membantu saya menyesuaikan informasi. Boleh tahu usia si kecil berapa, Bu?",
            "user: 2 tahun",
            "assistant: Lamanya keluhan membantu saya memahami kondisinya. Keluhannya sudah berapa lama, Bu?",
            "user: Sejak tadi malam",
            "assistant: Selama ini, apakah si kecil juga mengalami gejala lain atau terlihat jauh lebih lemas, Bu?",
        )
        response = await self.mom.answer(AgentRequest("Tidak ada, masih aktif", history=history))

        self.assertEqual(response.agent, AgentName.MOM)
        self.assertEqual(response.safety_level, SafetyLevel.GENERAL)
        self.assertEqual(len(self.retriever.calls), 1)
        self.assertIn("Anak saya demam", self.retriever.calls[0][0])
        self.assertEqual(self.generator.calls, [])

    async def test_mom_renders_reviewed_evidence_without_model_rewrite(self) -> None:
        history = (
            "user: Anak dua tahun pilek sejak dua hari",
            "assistant: Selama ini, apakah si kecil juga mengalami gejala lain atau terlihat jauh lebih lemas, Bu?",
        )

        response = await self.mom.answer(AgentRequest("Tidak ada, masih aktif", history=history))

        self.assertEqual(response.answer, "Berikut informasi umum dari buku yang tersedia:\n\nEvidence yang sudah direview.")
        self.assertEqual(self.generator.calls, [])
        self.assertEqual(len(response.citations), 1)

    async def test_mom_does_not_filter_health_retrieval_by_recipe_condition(self) -> None:
        history = (
            "user: Anak saya pilek",
            "assistant: Usia si kecil berapa, Bu?",
            "user: 5 tahun",
            "assistant: Pileknya mulai sejak kapan, Bu?",
            "user: sejak 2 hari",
            "assistant: Selain itu, apakah ada demam atau sulit bernapas, Bu?",
        )

        await self.mom.answer(AgentRequest("Tidak ada, masih aktif", history=history))

        self.assertIsNone(self.retriever.calls[0][3])

    async def test_koki_ben_collects_age_then_allergy_before_search(self) -> None:
        first = await self.koki.answer(AgentRequest("Tolong carikan resep untuk anak"))
        self.assertIn("Saya bantu carikan menu", first.answer)
        self.assertTrue(first.answer.endswith("usia si kecil berapa, Bu?"))

        history = (
            "user: Tolong carikan resep untuk anak",
            "assistant: Usia si kecil berapa, Bu?",
        )
        second = await self.koki.answer(AgentRequest("2 tahun", history=history))
        self.assertIn("Saya paham Ibu mencari menu", second.answer)
        self.assertTrue(second.answer.endswith("alergi makanan, Bu?"))

        complete_history = history + (
            "user: 2 tahun",
            "assistant: Si kecil punya alergi makanan, Bu?",
        )
        third = await self.koki.answer(AgentRequest("Tidak ada alergi", history=complete_history))

        self.assertEqual(third.agent, AgentName.KOKI_BEN)
        self.assertEqual(self.retriever.calls[-1][1], Intent.RECIPE)

    async def test_koki_ben_acknowledges_the_requested_food_and_condition(self) -> None:
        response = await self.koki.answer(AgentRequest("Makanan untuk anak 5 tahun yang batuk pilek"))

        self.assertIn("makanan", response.answer.casefold())
        self.assertIn("batuk pilek", response.answer.casefold())
        self.assertTrue(response.answer.endswith("alergi makanan, Bu?"))

    async def test_koki_ben_preserves_food_form_and_target_condition(self) -> None:
        retriever = FormAwareRecipeRetriever()
        koki = SpecialistAgent(SpecialistPolicy.koki_ben(), retriever, NeverGenerator())

        response = await koki.answer(AgentRequest("Makanan untuk anak 5 tahun yang batuk pilek, alergi udang"))

        self.assertEqual(retriever.target_condition, "batuk pilek")
        self.assertTrue(response.answer.startswith("Judul: Nagasari"))
        self.assertNotIn("Kalau Ibu mau", response.answer)
        self.assertFalse(response.offers_handoff)

    async def test_koki_ben_renders_reviewed_recipe_fields_without_llm_rewriting(self) -> None:
        koki = SpecialistAgent(SpecialistPolicy.koki_ben(), FormAwareRecipeRetriever(), NeverGenerator())

        response = await koki.answer(AgentRequest("Makanan untuk anak 5 tahun yang batuk pilek, alergi udang"))

        self.assertEqual(
            response.answer,
            "Judul: Nagasari\n\nBahan:\n- pisang\n\nCara membuat:\n1. Kukus sampai matang.\n\nCatatan:\n- Sajikan hangat.",
        )

    def test_koki_system_prompt_forbids_food_to_drink_substitution(self) -> None:
        self.assertIn("Jangan mengganti permintaan makanan dengan minuman", SYSTEM_PROMPTS[AgentName.KOKI_BEN])

    async def test_koki_ben_uses_short_answers_in_question_context(self) -> None:
        age_history = (
            "user: Tolong carikan resep untuk anak",
            "assistant: Usia si kecil berapa, Bu?",
        )
        age = await self.koki.answer(AgentRequest("5", history=age_history))
        self.assertEqual(age.answer, "Maksud Ibu 5 tahun atau bulan?")

        allergy_history = age_history + (
            "user: 5 tahun",
            "assistant: Si kecil punya alergi makanan, Bu?",
        )
        answer = await self.koki.answer(AgentRequest("tidak ada dok", history=allergy_history))

        self.assertFalse(answer.needs_clarification)
        self.assertEqual(len(self.retriever.calls), 1)

    async def test_mom_clarifies_a_bare_age_without_repeating_the_question(self) -> None:
        history = (
            "user: Anak saya pilek",
            "assistant: Usia si kecil berapa, Bu?",
        )

        response = await self.mom.answer(AgentRequest("5", history=history))

        self.assertEqual(response.answer, "Maksud Ibu 5 tahun atau bulan?")

    async def test_koki_ben_never_returns_recipe_with_stated_allergen(self) -> None:
        koki = SpecialistAgent(SpecialistPolicy.koki_ben(), AllergyConflictRetriever(), self.generator)

        response = await koki.answer(AgentRequest("Cari resep, anak alergi telur dua tahun"))

        self.assertEqual(response.safety_level, SafetyLevel.CAUTION)
        self.assertEqual(response.citations, ())
        self.assertEqual(self.generator.calls, [])

    async def test_koki_ben_grounds_one_complete_recipe_in_one_citation(self) -> None:
        koki = SpecialistAgent(SpecialistPolicy.koki_ben(), TwoRecipeRetriever(), self.generator)

        response = await koki.answer(AgentRequest("Cari resep untuk anak 5 tahun, tidak ada alergi"))

        self.assertTrue(response.answer.startswith("Judul: Resep 1"))
        self.assertEqual(self.generator.calls, [])
        self.assertEqual(len(response.citations), 1)

    async def test_koki_ben_does_not_use_unscoped_recipes_for_babies_under_one(self) -> None:
        response = await self.koki.answer(AgentRequest("Cari resep untuk anak 8 bulan, tidak ada alergi"))

        self.assertEqual(response.safety_level, SafetyLevel.CAUTION)
        self.assertIn("di bawah 1 tahun", response.answer)
        self.assertEqual(self.generator.calls, [])

    async def test_provider_error_returns_safe_message_without_detail(self) -> None:
        mom = SpecialistAgent(SpecialistPolicy.mom(), UnavailableRetriever(), self.generator)
        history = (
            "user: Anak 2 tahun demam sejak tadi malam",
            "assistant: Selama ini, apakah si kecil juga mengalami gejala lain atau terlihat jauh lebih lemas, Bu?",
        )

        response = await mom.answer(AgentRequest("Tidak ada, masih aktif", history=history))

        self.assertEqual(response.safety_level, SafetyLevel.CAUTION)
        self.assertNotIn("private provider detail", response.answer)

if __name__ == "__main__":
    unittest.main()
