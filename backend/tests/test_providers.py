import unittest
from unittest.mock import patch

from app.domain.models import Intent
from app.infrastructure.providers import SupabaseKnowledgeRetriever


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return [{
            "chunk_id": "recipe-1",
            "source_title": "Buku",
            "title": "Nagasari",
            "content": "Resep Nagasari",
            "content_type": "recipe",
            "target_condition": "batuk pilek",
            "entity_payload": {"ingredients": ["pisang"]},
            "semantic_similarity": 0.9,
        }]


class FakeClient:
    def __init__(self, **kwargs):
        self.payload = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def post(self, url, *, headers, json):
        self.payload = json
        return FakeResponse()


class ProviderTests(unittest.IsolatedAsyncioTestCase):
    async def test_recipe_search_sends_condition_and_keeps_recipe_shape(self):
        client = FakeClient()
        retriever = SupabaseKnowledgeRetriever(
            "https://example.supabase.co", "secret", embedding_model="model", timeout_seconds=1
        )
        retriever._embed = lambda query: [0.0]

        with patch("app.infrastructure.providers.httpx.AsyncClient", return_value=client):
            chunks = await retriever.search(
                "makanan batuk pilek", intent=Intent.RECIPE, top_k=5, target_condition="batuk pilek"
            )

        self.assertEqual(client.payload["p_filter_target_condition"], "batuk pilek")
        self.assertEqual(chunks[0].entity_payload["title"], "Nagasari")
        self.assertEqual(chunks[0].entity_payload["target_condition"], "batuk pilek")


if __name__ == "__main__":
    unittest.main()
