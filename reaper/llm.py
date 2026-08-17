"""Thin wrapper around the Anthropic Messages API.

One Conversation instance carries the cached system prompt plus the running
message history, so the three workflow steps build on one another and the
locked context is written to cache once and read cheaply thereafter.
"""

from __future__ import annotations

import json
from typing import Any

from reaper.config import DEFAULT_MODEL

try:
    import anthropic
except ImportError:  # pragma: no cover - surfaced to the user at runtime
    anthropic = None


class LLMUnavailable(RuntimeError):
    pass


def _client() -> "anthropic.Anthropic":
    if anthropic is None:
        raise LLMUnavailable(
            "The 'anthropic' package is not installed. Run: pip install anthropic"
        )
    try:
        return anthropic.Anthropic()
    except Exception as exc:  # noqa: BLE001 - re-raise as a clear message
        raise LLMUnavailable(
            "Could not initialise the Anthropic client. Set ANTHROPIC_API_KEY "
            "(or run `ant auth login`). Original error: %s" % exc
        ) from exc


class Conversation:
    """Stateful multi-turn conversation with a cached system prompt."""

    def __init__(self, system_prompt: str, model: str | None = None) -> None:
        self.client = _client()
        self.model = model or DEFAULT_MODEL
        # Cache the large locked system prompt so later turns read it cheaply.
        self.system = [
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ]
        self.messages: list[dict[str, Any]] = []

    def _send(self, max_tokens: int, output_config: dict | None = None) -> Any:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": self.system,
            "messages": self.messages,
            "thinking": {"type": "adaptive"},
            "output_config": {"effort": "high"},
        }
        if output_config:
            # output_config.format is incompatible with thinking display but fine
            # with adaptive thinking; merge the format in.
            kwargs["output_config"] = {"effort": "high", **output_config}
        return self.client.messages.create(**kwargs)

    def ask_text(self, prompt: str, max_tokens: int = 16000) -> str:
        """Send a user turn, append the assistant reply, return its text."""
        self.messages.append({"role": "user", "content": prompt})
        # Stream to stay under HTTP timeouts on large resume outputs.
        with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            system=self.system,
            messages=self.messages,
            thinking={"type": "adaptive"},
            output_config={"effort": "high"},
        ) as stream:
            message = stream.get_final_message()
        text = _text_of(message)
        self.messages.append({"role": "assistant", "content": message.content})
        return text

    def ask_json(self, prompt: str, schema: dict, max_tokens: int = 8000) -> dict:
        """Send a user turn and get back JSON validated against a schema."""
        self.messages.append({"role": "user", "content": prompt})
        message = self._send(
            max_tokens,
            output_config={"format": {"type": "json_schema", "schema": schema}},
        )
        text = _text_of(message)
        self.messages.append({"role": "assistant", "content": message.content})
        return json.loads(text)


def _text_of(message: Any) -> str:
    return "".join(b.text for b in message.content if getattr(b, "type", None) == "text")
