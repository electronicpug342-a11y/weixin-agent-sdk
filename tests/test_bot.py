import asyncio

import pytest

from weixin_agent.bot import start
from weixin_agent.models import ChatRequest, ChatResponse, StartOptions
from weixin_agent.storage import ResolvedWeixinAccount


class DummyAgent:
    async def chat(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(text=request.text)


@pytest.mark.asyncio
async def test_start_is_cancelled_via_task_cancellation(monkeypatch: pytest.MonkeyPatch) -> None:
    closed = False

    class DummyClient:
        def __init__(self, base_url: str, token: str | None = None) -> None:
            self.base_url = base_url
            self.token = token

        async def aclose(self) -> None:
            nonlocal closed
            closed = True

    account = ResolvedWeixinAccount(
        account_id="test-account",
        base_url="https://example.com",
        cdn_base_url="https://cdn.example.com",
        token="token",
        enabled=True,
        configured=True,
    )

    async def fake_monitor_weixin(**_: object) -> None:
        await asyncio.Event().wait()

    monkeypatch.setattr("weixin_agent.bot.resolve_account", lambda account_id: account)
    monkeypatch.setattr("weixin_agent.bot.WeixinApiClient", DummyClient)
    monkeypatch.setattr("weixin_agent.bot.monitor_weixin", fake_monitor_weixin)

    task = asyncio.create_task(start(DummyAgent(), StartOptions(account_id=account.account_id)))

    await asyncio.sleep(0)
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    assert closed is True
