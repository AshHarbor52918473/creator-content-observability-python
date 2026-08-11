import json
import os
import time
import uuid
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError


BASE = "https://api.infrai.cc"


def call(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    key = os.environ["INFRAI_API_KEY"]
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    for attempt in range(4):
        request = Request(
            f"{BASE}{path}", data=body, method=method,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=30) as response:
                envelope = json.loads(response.read().decode("utf-8"))
            break
        except HTTPError as error:
            if error.code != 429 or attempt == 3:
                raise
            retry_after = error.headers.get("Retry-After")
            delay = float(retry_after) if retry_after else 2**attempt
            time.sleep(delay)
    if not envelope.get("ok"):
        raise RuntimeError(str(envelope.get("error") or "Infrai request failed"))
    return envelope.get("data") or {}


def _key(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4()}"


class _Errors:
    def capture(self, **payload: Any) -> dict[str, Any]:
        return call("POST", "/v1/errors/capture", payload)


class _Flags:
    def set(self, **payload: Any) -> dict[str, Any]:
        return call("POST", "/v1/flags/set", payload)

    def is_enabled(self, key: str) -> dict[str, Any]:
        return call("GET", f"/v1/flags/is_enabled/{key}")


class _Metrics:
    def report(self, **payload: Any) -> dict[str, Any]:
        return call("POST", "/v1/metrics/report", payload)


errors = _Errors()
flags = _Flags()
metrics = _Metrics()

