import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import parse_qs, urlsplit

import pytest
from playwright.sync_api import sync_playwright

from portfolio.api_client import DemoClient

pytestmark = pytest.mark.api


@pytest.fixture
def demo_service():
    state = {
        "statuses": ["NEW", "PROCESSING", "READY"],
        "pages": [
            {"content": [{"id": "demo-item-1"}, {"id": "demo-item-2"}], "last": False},
            {"content": [{"id": "demo-item-3"}], "last": True},
        ],
        "requests": [],
        "http_status": 200,
    }

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            parsed = urlsplit(self.path)
            state["requests"].append(self.path)
            code = state["http_status"]
            if parsed.path == "/jobs/demo/status":
                statuses = state["statuses"]
                status = statuses.pop(0) if len(statuses) > 1 else statuses[0]
                payload = {"status": status}
            elif parsed.path == "/jobs/demo/items":
                page = int(parse_qs(parsed.query).get("page", ["0"])[0])
                payload = state["pages"][page] if page < len(state["pages"]) else state["pages"][-1]
            else:
                code, payload = 404, {"error": "Unknown demo endpoint"}
            body = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    try:
        yield state, f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


@pytest.fixture
def client(demo_service):
    _, base_url = demo_service
    with sync_playwright() as playwright:
        context = playwright.request.new_context()
        try:
            yield DemoClient(context, base_url)
        finally:
            context.dispose()


def test_waits_for_ready_before_fetching_all_pages(client, demo_service):
    state, _ = demo_service
    assert client.wait_ready() == {"status": "READY"}
    items = list(client.iter_items())
    assert [item["id"] for item in items] == ["demo-item-1", "demo-item-2", "demo-item-3"]
    assert sum("/status" in path for path in state["requests"]) == 3
    assert sum("/items" in path for path in state["requests"]) == 2


@pytest.mark.parametrize("status", ["ERROR", "UNEXPECTED"])
def test_processing_errors_fail_instead_of_skipping(client, demo_service, status):
    demo_service[0]["statuses"] = [status]
    with pytest.raises(AssertionError, match=status):
        client.wait_ready()


def test_polling_stops_at_deadline(client, demo_service):
    demo_service[0]["statuses"] = ["NEW"]
    with pytest.raises(TimeoutError, match="NEW"):
        client.wait_ready(timeout_seconds=0.08, interval_seconds=0.01)


def test_http_error_is_reported(client, demo_service):
    demo_service[0]["http_status"] = 503
    with pytest.raises(AssertionError, match="503"):
        client.wait_ready()


def test_empty_final_page_is_valid(client, demo_service):
    demo_service[0]["pages"] = [{"content": [], "last": True}]
    assert list(client.iter_items()) == []


def test_missing_pagination_flag_is_not_silent_success(client, demo_service):
    demo_service[0]["pages"] = [{"content": []}]
    with pytest.raises(AssertionError, match="last flag"):
        list(client.iter_items())


def test_unbounded_pagination_is_rejected(client, demo_service):
    demo_service[0]["pages"] = [{"content": [], "last": False}]
    with pytest.raises(AssertionError, match="page limit"):
        list(client.iter_items(max_pages=2))
