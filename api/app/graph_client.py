"""Microsoft Graph metadata-only client (optional – no content ever read)."""

from __future__ import annotations

import httpx
from app.config import get_settings


class GraphClient:
    """Fetches ONLY metadata from Microsoft 365. NEVER reads message bodies,
    subjects, attachments, or meeting descriptions."""

    TOKEN_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    GRAPH_URL = "https://graph.microsoft.com/v1.0"

    # Permitted fields – privacy-first
    MAIL_SELECT = "receivedDateTime,sentDateTime,importance,isRead"
    CALENDAR_SELECT = "start,end,organizer,attendees,responseStatus,showAs"

    def __init__(self):
        s = get_settings()
        self.tenant_id = s.graph_tenant_id
        self.client_id = s.graph_client_id
        self.client_secret = s.graph_client_secret
        self._token: str | None = None

    async def _get_token(self) -> str:
        if self._token:
            return self._token
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.TOKEN_URL.format(tenant=self.tenant_id),
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": "https://graph.microsoft.com/.default",
                },
            )
            resp.raise_for_status()
            self._token = resp.json()["access_token"]
            return self._token

    async def _get(self, path: str, params: dict | None = None) -> dict:
        token = await self._get_token()
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.GRAPH_URL}{path}",
                headers={"Authorization": f"Bearer {token}"},
                params=params or {},
            )
            resp.raise_for_status()
            return resp.json()

    async def get_calendar_events(self, user_id: str, start: str, end: str) -> list[dict]:
        """Get calendar event METADATA only."""
        data = await self._get(
            f"/users/{user_id}/calendarView",
            params={
                "startDateTime": start,
                "endDateTime": end,
                "$select": self.CALENDAR_SELECT,
                "$top": "200",
            },
        )
        return data.get("value", [])

    async def get_mail_metadata(self, user_id: str, start: str, end: str) -> list[dict]:
        """Get mail METADATA only – no subject, body, preview, attachments."""
        data = await self._get(
            f"/users/{user_id}/messages",
            params={
                "$filter": f"receivedDateTime ge {start} and receivedDateTime le {end}",
                "$select": self.MAIL_SELECT,
                "$top": "200",
            },
        )
        return data.get("value", [])
