# weixin-agent-sdk

参考 [`wong2/weixin-agent-sdk`](https://github.com/wong2/weixin-agent-sdk) 实现的 Python 版微信 Agent SDK。

顶层 API 保持同样的三件事：

- `Agent`
- `login()`
- `start(agent)`

## Quick Start

```bash
uv venv .venv
uv sync --dev --extra openai
source .venv/bin/activate
python -m examples.openai_bot login
OPENAI_API_KEY=sk-xxx python -m examples.openai_bot start
```

## Public API

```python
from weixin_agent import Agent, ChatRequest, ChatResponse, login, start
```

```python
class EchoAgent:
    async def chat(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(text=f"You said: {request.text}")
```

`start()` is a long-running coroutine. Stop it by cancelling the task, for example via
`Ctrl-C` when it is wrapped by `asyncio.run()`.

## Notes

- Uses long polling via `ilink/bot/getupdates`.
- Persists account credentials and `get_updates_buf` under `~/.openclaw/openclaw-weixin/`.
- Supports text, image, video, file, and voice message metadata.
- Voice messages are currently passed through as `audio/silk` when no transcription is available.
