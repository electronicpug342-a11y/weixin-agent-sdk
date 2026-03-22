from __future__ import annotations

import base64
import json
import random
from importlib.metadata import PackageNotFoundError, version
from typing import Any

import httpx

from weixin_agent.storage import load_config_route_tag

DEFAULT_LONG_POLL_TIMEOUT_S = 35.0
DEFAULT_API_TIMEOUT_S = 15.0
DEFAULT_CONFIG_TIMEOUT_S = 10.0
DEFAULT_ILINK_BOT_TYPE = "3"
SESSION_EXPIRED_ERRCODE = -14


def build_base_info() -> dict[str, str]:
    try:
        package_version = version("weixin-agent-sdk")
    except PackageNotFoundError:
        package_version = "0.1.0"
    return {"channel_version": package_version}


def random_wechat_uin() -> str:
    raw = str(random.randint(0, 2**32 - 1)).encode()
    return base64.b64encode(raw).decode()


class WeixinApiClient:
    def __init__(self, base_url: str, token: str | None = None) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.token = token.strip() if token else None
        self._client = httpx.AsyncClient(base_url=self.base_url, follow_redirects=True)

    async def aclose(self) -> None:
        await self._client.aclose()

    def _build_headers(self, body: str, account_id: str | None = None) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "AuthorizationType": "ilink_bot_token",
            "Content-Length": str(len(body.encode())),
            "X-WECHAT-UIN": random_wechat_uin(),
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        route_tag = load_config_route_tag(account_id)
        if route_tag:
            headers["SKRouteTag"] = route_tag
        return headers

    async def _post_json(
        self,
        endpoint: str,
        payload: dict[str, Any],
        *,
        timeout: float,
        account_id: str | None = None,
    ) -> dict[str, Any]:
        body = json.dumps(payload)
        response = await self._client.post(
            endpoint,
            content=body,
            headers=self._build_headers(body, account_id=account_id),
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()

    async def _get_json(
        self,
        endpoint: str,
        *,
        params: dict[str, Any],
        timeout: float,
        headers: dict[str, str] | None = None,
        account_id: str | None = None,
    ) -> dict[str, Any]:
        merged_headers = headers.copy() if headers else {}
        route_tag = load_config_route_tag(account_id)
        if route_tag:
            merged_headers["SKRouteTag"] = route_tag
        response = await self._client.get(
            endpoint,
            params=params,
            headers=merged_headers or None,
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()

    async def get_updates(
        self,
        *,
        get_updates_buf: str,
        timeout: float = DEFAULT_LONG_POLL_TIMEOUT_S,
        account_id: str | None = None,
    ) -> dict[str, Any]:
        try:
            return await self._post_json(
                "ilink/bot/getupdates",
                {
                    "get_updates_buf": get_updates_buf,
                    "base_info": build_base_info(),
                },
                timeout=timeout,
                account_id=account_id,
            )
        except httpx.TimeoutException:
            return {"ret": 0, "msgs": [], "get_updates_buf": get_updates_buf}

    async def get_upload_url(
        self,
        payload: dict[str, Any],
        *,
        account_id: str | None = None,
    ) -> dict[str, Any]:
        return await self._post_json(
            "ilink/bot/getuploadurl",
            {**payload, "base_info": build_base_info()},
            timeout=DEFAULT_API_TIMEOUT_S,
            account_id=account_id,
        )

    async def send_message(self, payload: dict[str, Any], *, account_id: str | None = None) -> None:
        await self._post_json(
            "ilink/bot/sendmessage",
            {**payload, "base_info": build_base_info()},
            timeout=DEFAULT_API_TIMEOUT_S,
            account_id=account_id,
        )

    async def get_config(
        self,
        *,
        ilink_user_id: str,
        context_token: str | None,
        account_id: str | None = None,
    ) -> dict[str, Any]:
        return await self._post_json(
            "ilink/bot/getconfig",
            {
                "ilink_user_id": ilink_user_id,
                "context_token": context_token,
                "base_info": build_base_info(),
            },
            timeout=DEFAULT_CONFIG_TIMEOUT_S,
            account_id=account_id,
        )

    async def send_typing(self, payload: dict[str, Any], *, account_id: str | None = None) -> None:
        await self._post_json(
            "ilink/bot/sendtyping",
            {**payload, "base_info": build_base_info()},
            timeout=DEFAULT_CONFIG_TIMEOUT_S,
            account_id=account_id,
        )

    async def fetch_qr_code(
        self,
        *,
        bot_type: str = DEFAULT_ILINK_BOT_TYPE,
        account_id: str | None = None,
    ) -> dict[str, Any]:
        return await self._get_json(
            "ilink/bot/get_bot_qrcode",
            params={"bot_type": bot_type},
            timeout=DEFAULT_API_TIMEOUT_S,
            account_id=account_id,
        )

    async def poll_qr_status(
        self,
        *,
        qrcode: str,
        account_id: str | None = None,
    ) -> dict[str, Any]:
        try:
            return await self._get_json(
                "ilink/bot/get_qrcode_status",
                params={"qrcode": qrcode},
                headers={"iLink-App-ClientVersion": "1"},
                timeout=DEFAULT_LONG_POLL_TIMEOUT_S,
                account_id=account_id,
            )
        except httpx.TimeoutException:
            return {"status": "wait"}
