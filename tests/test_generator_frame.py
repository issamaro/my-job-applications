# Lean Code — BSD 3-Clause License — Vivian Voss, 2026
# Scope: Smoke-test the temporary generator input frame — deleted with slice 6 (tailor-cv-screen).

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


def test_generator_input_frame_geometry(public_url):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(viewport={"width": 1512, "height": 860})
        page = context.new_page()
        page.goto(public_url, wait_until="load")
        page.wait_for_selector(".topbar")
        page.click('[data-slot-id="tailor"]')
        page.wait_for_selector(".generator-frame")
        try:
            geometry = page.evaluate(
                """() => {
                    const frame = document.querySelector('.generator-frame');
                    const rect = frame.getBoundingClientRect();
                    return {
                        maxWidth: window.getComputedStyle(frame).maxWidth,
                        left: rect.left,
                        right: rect.right,
                        innerWidth: window.innerWidth,
                    };
                }"""
            )
        finally:
            context.close()
            browser.close()

    assert geometry["maxWidth"] == "800px"
    assert geometry["left"] > 0
    assert geometry["right"] < geometry["innerWidth"]
    assert abs(geometry["left"] - (geometry["innerWidth"] - geometry["right"])) <= 1
