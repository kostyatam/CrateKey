import json

import anthropic
import structlog

log = structlog.get_logger()

SYSTEM_PROMPT = (
    "You parse raw web page titles from music platforms into structured data. "
    'Respond with JSON only — no preamble, no markdown fences: {"artist": string | null, "track": string | null}. '
    "Strip platform suffixes (e.g. ' - YouTube', '| Free Listening on SoundCloud'), "
    "featuring credits stay in the track name."
)


class ParsedTitle:
    def __init__(self, artist: str | None, track: str | None) -> None:
        self.artist = artist
        self.track = track


class TitleParser:
    """LLM title parsing — see CLAUDE.md: claude-haiku-4-5-20251001, JSON only."""

    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001") -> None:
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    async def parse(self, title: str) -> ParsedTitle | None:
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=256,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": title}],
            )
        except anthropic.APIError as exc:
            log.warning("title_parser.request_failed", error=str(exc))
            return None

        text = next((b.text for b in response.content if b.type == "text"), "")
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            log.warning("title_parser.invalid_json", raw=text[:200])
            return None

        artist = data.get("artist")
        track = data.get("track")
        if not artist or not track:
            return None
        return ParsedTitle(artist=artist, track=track)
