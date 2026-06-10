import httpx
import structlog

log = structlog.get_logger()

BASE_URL = "https://api.getsongbpm.com"


class GetSongBPMResult:
    def __init__(self, key: str | None, mode: str | None, bpm: float | None) -> None:
        self.key = key
        self.mode = mode
        self.bpm = bpm


class GetSongBPMClient:
    """Name-based key/BPM lookup — step 3 of the resolution hierarchy."""

    def __init__(self, api_key: str, http: httpx.AsyncClient | None = None) -> None:
        self._api_key = api_key
        self._http = http or httpx.AsyncClient(base_url=BASE_URL, timeout=10.0)

    async def search(self, artist: str, track: str) -> GetSongBPMResult | None:
        try:
            response = await self._http.get(
                "/search/",
                params={
                    "api_key": self._api_key,
                    "type": "both",
                    "lookup": f"song:{track} artist:{artist}",
                },
            )
            response.raise_for_status()
        except (httpx.HTTPStatusError, httpx.TransportError) as exc:
            log.warning("getsongbpm.request_failed", error=str(exc))
            return None

        body = response.json()
        results = body.get("search")
        if not isinstance(results, list) or not results:
            return None

        first = results[0]
        key = first.get("key_of")
        bpm = first.get("tempo")
        if key is None and bpm is None:
            return None

        mode: str | None = None
        if isinstance(key, str):
            mode = "minor" if key.endswith("m") else "major"

        return GetSongBPMResult(
            key=key,
            mode=mode,
            bpm=float(bpm) if bpm is not None else None,
        )
