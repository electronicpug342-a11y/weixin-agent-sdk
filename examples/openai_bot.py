from __future__ import annotations

import asyncio
import base64
import os
import sys
from pathlib import Path

from openai import AsyncOpenAI

from weixin_agent import Agent, ChatRequest, ChatResponse, login, start


class OpenAIAgent(Agent):
    def __init__(
        self,
        *,
        api_key: str,
        model: str = "gpt-5.4",
        base_url: str | None = None,
        system_prompt: str | None = None,
        max_history: int = 50,
    ) -> None:
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model
        self._system_prompt = system_prompt
        self._max_history = max_history
        self._conversations: dict[str, list[dict[str, object]]] = {}

    async def chat(self, request: ChatRequest) -> ChatResponse:
        history = self._conversations.setdefault(request.conversation_id, [])
        content: list[dict[str, object]] = []
        if request.text:
            content.append({"type": "text", "text": request.text})

        if request.media and request.media.type == "image":
            image_data = Path(request.media.file_path).read_bytes()
            mime_type = request.media.mime_type or "image/jpeg"
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{base64.b64encode(image_data).decode()}",
                    },
                },
            )
        elif request.media:
            attachment_name = request.media.file_name or Path(request.media.file_path).name
            content.append(
                {
                    "type": "text",
                    "text": f"[Attachment: {request.media.type} - {attachment_name}]",
                },
            )

        if not content:
            return ChatResponse(text="")

        user_message: dict[str, object] = {
            "role": "user",
            "content": (
                content[0]["text"]
                if len(content) == 1 and content[0]["type"] == "text"
                else content
            ),
        }
        history.append(user_message)

        messages: list[dict[str, object]] = []
        if self._system_prompt:
            messages.append({"role": "system", "content": self._system_prompt})
        messages.extend(history)

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
        )
        reply = response.choices[0].message.content or ""
        history.append({"role": "assistant", "content": reply})
        if len(history) > self._max_history:
            del history[: len(history) - self._max_history]
        return ChatResponse(text=reply)


async def main() -> None:
    argv = sys.argv
    command = argv[1] if len(argv) > 1 else ""

    if command == "login":
        await login()
        return

    if command == "start":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise SystemExit("OPENAI_API_KEY is required")
        agent = OpenAIAgent(
            api_key=api_key,
            base_url=os.getenv("OPENAI_BASE_URL"),
            model=os.getenv("OPENAI_MODEL", "gpt-5.4"),
            system_prompt=os.getenv("SYSTEM_PROMPT"),
        )
        await start(agent)
        return

    raise SystemExit(
        "Usage:\n"
        "  python -m examples.openai_bot login\n"
        "  python -m examples.openai_bot start\n\n"
        "Environment variables:\n"
        "  OPENAI_API_KEY   Required for start\n"
        "  OPENAI_BASE_URL  Optional\n"
        "  OPENAI_MODEL     Optional, default gpt-5.4\n"
        "  SYSTEM_PROMPT    Optional\n"
    )


if __name__ == "__main__":
    asyncio.run(main())
