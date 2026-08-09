import unittest
from uuid import uuid4

from httpx import ASGITransport, AsyncClient

from app.main import app


class ChatApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_mom_follow_up_uses_section_contract(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/v1/chat",
                json={"request_id": str(uuid4()), "question": "Anak saya demam"},
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["route"], "knowledge")
        self.assertEqual(payload["sections"][0]["agent"], "mom")
        self.assertIn("pasti Ibu jadi kepikiran", payload["sections"][0]["answer"])
        self.assertTrue(payload["sections"][0]["answer"].endswith("usia si kecil berapa, Bu?"))
        self.assertTrue(payload["needs_clarification"])


if __name__ == "__main__":
    unittest.main()
