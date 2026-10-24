from time import monotonic, sleep
from urllib.parse import urlsplit

from playwright.sync_api import APIRequestContext


class DemoClient:
    def __init__(self, request: APIRequestContext, base_url: str):
        parsed = urlsplit(base_url)
        if parsed.scheme != "http" or parsed.hostname != "127.0.0.1":
            raise ValueError("The demo client only accepts the loopback demo server")
        self.request = request
        self.base_url = base_url.rstrip("/")

    def _get(self, path: str, *, timeout_ms: float = 1000, params=None):
        response = self.request.get(
            f"{self.base_url}{path}", params=params, timeout=timeout_ms
        )
        assert response.ok, f"Demo API returned HTTP {response.status}"
        data = response.json()
        assert isinstance(data, dict), "Expected a JSON object"
        return data

    def wait_ready(self, *, timeout_seconds=2.0, interval_seconds=0.01):
        if timeout_seconds <= 0 or interval_seconds <= 0:
            raise ValueError("Polling timeout and interval must be positive")
        deadline = monotonic() + timeout_seconds
        last_status = None
        while (remaining := deadline - monotonic()) > 0:
            data = self._get("/jobs/demo/status", timeout_ms=max(1, remaining * 1000))
            last_status = data.get("status")
            if last_status == "READY":
                return data
            if last_status == "ERROR":
                raise AssertionError("Demo processing failed: ERROR")
            assert last_status in {"NEW", "PROCESSING"}, f"Unexpected status: {last_status}"
            sleep(min(interval_seconds, max(0, deadline - monotonic())))
        raise TimeoutError(f"Demo processing timed out; last status: {last_status}")

    def iter_items(self, *, page_size=2, max_pages=10):
        if page_size <= 0 or max_pages <= 0:
            raise ValueError("Page size and page limit must be positive")
        for page in range(max_pages):
            data = self._get("/jobs/demo/items", params={"page": page, "size": page_size})
            content = data.get("content")
            assert isinstance(content, list), "Missing or invalid pagination content"
            assert isinstance(data.get("last"), bool), "Missing pagination last flag"
            for item in content:
                yield item
            if data["last"]:
                return
        raise AssertionError("Pagination exceeded the configured page limit")
