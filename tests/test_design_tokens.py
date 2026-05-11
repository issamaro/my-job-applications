# Lean Code — BSD 3-Clause License — Vivian Voss, 2026
# Scope: Smoke-test the editorial body restyle reaches the served bundle.

import socket
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright


PUBLIC_DIR = Path(__file__).parent.parent / "public"


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def create_public_server(port):
    handler = type(
        "PublicHandler",
        (SimpleHTTPRequestHandler,),
        {"__init__": lambda self, *a, **kw: SimpleHTTPRequestHandler.__init__(self, *a, directory=str(PUBLIC_DIR), **kw)},
    )
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


@pytest.fixture
def public_url():
    if not (PUBLIC_DIR / "build" / "bundle.css").exists():
        pytest.skip("public/build/bundle.css missing — run `bun run build` first")
    port = find_free_port()
    server = create_public_server(port)
    yield f"http://127.0.0.1:{port}/"
    server.shutdown()


def read_body_computed_styles(page):
    return page.evaluate("""() => {
        const computed = window.getComputedStyle(document.body);
        return {
            backgroundColor:     computed.backgroundColor,
            color:               computed.color,
            fontFamily:          computed.fontFamily,
            fontSize:            computed.fontSize,
            lineHeight:          computed.lineHeight,
            fontFeatureSettings: computed.fontFeatureSettings,
            webkitFontSmoothing: computed.getPropertyValue('-webkit-font-smoothing'),
        };
    }""")


def test_body_renders_editorial_tokens(public_url):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            context = browser.new_context()
            page = context.new_page()
            page.goto(public_url, wait_until="load")
            page.evaluate("() => document.fonts.ready")
            styles = read_body_computed_styles(page)
            context.close()
        finally:
            browser.close()

    assert styles["backgroundColor"] == "rgb(244, 241, 236)"
    assert styles["color"] == "rgb(26, 24, 20)"
    assert styles["fontFamily"].startswith('"Inter Tight"')
    assert styles["fontSize"] == "14px"
    assert styles["lineHeight"] == "21px"
    assert "ss01" in styles["fontFeatureSettings"]
    assert "cv11" in styles["fontFeatureSettings"]
    if styles["webkitFontSmoothing"]:
        assert styles["webkitFontSmoothing"] == "antialiased"
