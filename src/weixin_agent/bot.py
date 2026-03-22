from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import UTC, datetime

import qrcode

from weixin_agent.api import DEFAULT_ILINK_BOT_TYPE, WeixinApiClient
from weixin_agent.models import Agent, LoginOptions, StartOptions
from weixin_agent.runtime import monitor_weixin
from weixin_agent.storage import (
    DEFAULT_BASE_URL,
    WeixinAccountData,
    list_account_ids,
    normalize_account_id,
    register_account_id,
    resolve_account,
    save_account,
)


def _print_qr_code(url: str, log: Callable[[str], None]) -> None:
    try:
        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.make(fit=True)
        qr.print_ascii(tty=False)
    except Exception:
        log(f"QR code URL: {url}")


async def login(options: LoginOptions | None = None) -> str:
    options = options or LoginOptions()
    log = options.log or print
    base_url = options.base_url or DEFAULT_BASE_URL
    api_client = WeixinApiClient(base_url)

    try:
        log("Starting Weixin QR login...")
        qr_payload = await api_client.fetch_qr_code(bot_type=DEFAULT_ILINK_BOT_TYPE)
        qrcode_value = qr_payload.get("qrcode")
        qrcode_url = qr_payload.get("qrcode_img_content")
        if not isinstance(qrcode_value, str) or not isinstance(qrcode_url, str):
            raise ValueError("QR code response is missing qrcode or qrcode_img_content")

        log("")
        _print_qr_code(qrcode_url, log)
        log("")
        log("Waiting for scan...")

        refresh_count = 1
        deadline = asyncio.get_running_loop().time() + 480
        while asyncio.get_running_loop().time() < deadline:
            status_payload = await api_client.poll_qr_status(qrcode=qrcode_value)
            status = status_payload.get("status")
            if status == "wait":
                continue
            if status == "scaned":
                log("QR scanned, waiting for confirmation...")
                continue
            if status == "expired":
                refresh_count += 1
                if refresh_count > 3:
                    raise TimeoutError("QR code expired too many times")
                log(f"QR expired, refreshing ({refresh_count}/3)")
                qr_payload = await api_client.fetch_qr_code(bot_type=DEFAULT_ILINK_BOT_TYPE)
                qrcode_value = qr_payload["qrcode"]
                qrcode_url = qr_payload["qrcode_img_content"]
                _print_qr_code(qrcode_url, log)
                continue
            if status == "confirmed":
                bot_token = status_payload.get("bot_token")
                account_id = status_payload.get("ilink_bot_id")
                resolved_base_url = status_payload.get("baseurl") or base_url
                user_id = status_payload.get("ilink_user_id")
                if not isinstance(bot_token, str) or not isinstance(account_id, str):
                    raise ValueError("Login confirmed but bot_token or ilink_bot_id is missing")
                normalized_id = normalize_account_id(account_id)
                save_account(
                    normalized_id,
                    WeixinAccountData(
                        token=bot_token,
                        saved_at=datetime.now(tz=UTC).isoformat(),
                        base_url=str(resolved_base_url),
                        user_id=str(user_id) if user_id else None,
                    ),
                )
                register_account_id(normalized_id)
                log("Connected to Weixin successfully.")
                return normalized_id
        raise TimeoutError("Login timed out")
    finally:
        await api_client.aclose()


async def start(agent: Agent, options: StartOptions | None = None) -> None:
    options = options or StartOptions()
    log = options.log or print
    account_id = options.account_id
    if not account_id:
        account_ids = list_account_ids()
        if not account_ids:
            raise RuntimeError("No logged-in account found. Run login() first.")
        account_id = account_ids[0]
        if len(account_ids) > 1:
            log(f"[weixin] multiple accounts found, using the first one: {account_id}")

    account = resolve_account(account_id)
    if not account.configured:
        raise RuntimeError(f"Account {account.account_id} has no token. Run login() first.")

    api_client = WeixinApiClient(account.base_url, token=account.token)
    log(f"[weixin] starting bot, account={account.account_id}")
    try:
        await monitor_weixin(
            api_client=api_client,
            account=account,
            agent=agent,
            log=log,
        )
    finally:
        await api_client.aclose()
