import hashlib
import hmac
import uuid

import httpx

from app.config import settings


class N8NClient:
    def __init__(self):
        self.base = settings.N8N_WEBHOOK_BASE
        self.secret = settings.N8N_WEBHOOK_SECRET

    def _sign(self, payload: str) -> str:
        return hmac.new(self.secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

    async def trigger_analysis(self, analysis_id: uuid.UUID, payload: dict) -> dict:
        url = f"{self.base}/webhook/analysis-intake"
        async with httpx.AsyncClient(timeout=30) as client:
            body = {"analysis_id": str(analysis_id), **payload}
            import json
            raw = json.dumps(body)
            resp = await client.post(
                url,
                json=body,
                headers={
                    "X-Webhook-Signature": self._sign(raw),
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            return resp.json()


n8n_client = N8NClient()
