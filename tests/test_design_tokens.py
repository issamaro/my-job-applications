# Lean Code — BSD 3-Clause License — Vivian Voss, 2026
# Scope: Smoke-test the editorial body restyle reaches the served bundle.

import re
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

    assert styles["backgroundColor"] == "oklch(0.97 0.01 260)"
    assert styles["color"] == "oklch(0.16 0.04 265)"
    assert styles["fontFamily"].startswith('"Inter Tight"')
    assert styles["fontSize"] == "14px"
    assert styles["lineHeight"] == "21px"
    assert "ss01" in styles["fontFeatureSettings"]
    assert "cv11" in styles["fontFeatureSettings"]
    if styles["webkitFontSmoothing"]:
        assert styles["webkitFontSmoothing"] == "antialiased"


def test_bundle_carries_consolidation_rules():
    bundle = PUBLIC_DIR / "build" / "bundle.css"
    if not bundle.exists():
        pytest.skip("public/build/bundle.css missing — run `bun run build` first")
    css = bundle.read_text()

    assert ".btn:focus-visible" in css
    assert ".pill:focus-visible" in css
    assert "::-webkit-scrollbar" in css
    assert "animation: fadeOut 0.5s ease-out 1.5s forwards" in css


TOKEN_DEFINITION = re.compile(r"(--[a-zA-Z0-9-]+)\s*:")
TOKEN_REFERENCE = re.compile(r"var\(\s*(--[a-zA-Z0-9-]+)")


def read_token_sources():
    repo_root = Path(__file__).parent.parent
    sources = [repo_root / "src" / "styles" / "global.css", repo_root / "src" / "App.svelte"]
    sources += sorted((repo_root / "src" / "components").glob("*.svelte"))
    return sources


def test_all_token_references_resolve():
    sources = read_token_sources()
    defined = set()
    for source in sources:
        defined.update(TOKEN_DEFINITION.findall(source.read_text()))

    unresolved = {}
    for source in sources:
        for name in set(TOKEN_REFERENCE.findall(source.read_text())):
            if name not in defined:
                unresolved.setdefault(name, []).append(source.name)

    assert unresolved == {}, f"token references with no definition anywhere in src/: {unresolved}"
