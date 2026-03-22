from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Literal, Protocol

IncomingMediaType = Literal["image", "audio", "video", "file"]
OutgoingMediaType = Literal["image", "video", "file"]
LoggerFn = Callable[[str], None]


@dataclass(slots=True)
class IncomingMedia:
    type: IncomingMediaType
    file_path: str
    mime_type: str
    file_name: str | None = None


@dataclass(slots=True)
class OutgoingMedia:
    type: OutgoingMediaType
    url: str
    file_name: str | None = None


@dataclass(slots=True)
class ChatRequest:
    conversation_id: str
    text: str
    media: IncomingMedia | None = None


@dataclass(slots=True)
class ChatResponse:
    text: str | None = None
    media: OutgoingMedia | None = None


class Agent(Protocol):
    def chat(self, request: ChatRequest) -> Awaitable[ChatResponse]: ...


@dataclass(slots=True)
class LoginOptions:
    base_url: str | None = None
    log: LoggerFn | None = None


@dataclass(slots=True)
class StartOptions:
    account_id: str | None = None
    log: LoggerFn | None = None
