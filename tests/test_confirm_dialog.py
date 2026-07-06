# Lean Code — BSD 3-Clause License — Vivian Voss, 2026
# Scope: ConfirmDialog behavior — Escape cancels regardless of focus position.

import json
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
        {"__init__": lambda self, *a, **kw:
            SimpleHTTPRequestHandler.__init__(self, *a, directory=str(PUBLIC_DIR), **kw)},
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


def create_users_mock(page):
    def write_users_response(route, request):
        if request.method == "GET":
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "full_name": "Issa Maro",
                    "email": "test@example.com",
                }),
            )
        else:
            route.continue_()
    page.route("**/api/users", write_users_response)


def create_skills_mock(page):
    def write_skills_response(route, request):
        if request.method == "GET":
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps([{"id": 1, "name": "Python"}]),
            )
        else:
            route.continue_()
    page.route("**/api/skills", write_skills_response)


def open_skill_delete_dialog(playwright, public_url):
    browser = playwright.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    create_users_mock(page)
    create_skills_mock(page)
    page.goto(public_url, wait_until="load")
    page.wait_for_selector(".skill-remove")
    page.click(".skill-remove")
    page.wait_for_selector(".dialog-backdrop")
    return browser, context, page


def test_escape_cancels_dialog(public_url):
    with sync_playwright() as playwright:
        browser, context, page = open_skill_delete_dialog(playwright, public_url)
        try:
            focused_is_dialog = page.evaluate(
                "() => document.activeElement?.classList.contains('dialog')"
            )
            page.keyboard.press("Escape")
            page.wait_for_selector(".dialog-backdrop", state="detached")
            pill_count = page.evaluate(
                "() => document.querySelectorAll('.skill-cluster .skill-pill:not(.skill-pill-add)').length"
            )
        finally:
            context.close()
            browser.close()

    assert focused_is_dialog is True
    assert pill_count == 1


def test_escape_cancels_after_tab_out(public_url):
    with sync_playwright() as playwright:
        browser, context, page = open_skill_delete_dialog(playwright, public_url)
        try:
            for _ in range(4):
                page.keyboard.press("Tab")
            focused_left_dialog = page.evaluate(
                "() => !document.activeElement?.closest('.dialog')"
            )
            page.keyboard.press("Escape")
            page.wait_for_selector(".dialog-backdrop", state="detached")
        finally:
            context.close()
            browser.close()

    assert focused_left_dialog is True


def test_backdrop_click_cancels_dialog(public_url):
    with sync_playwright() as playwright:
        browser, context, page = open_skill_delete_dialog(playwright, public_url)
        try:
            page.mouse.click(20, 20)
            page.wait_for_selector(".dialog-backdrop", state="detached")
            dialog_click_survives = True
        finally:
            context.close()
            browser.close()

    assert dialog_click_survives is True


def test_dialog_click_keeps_dialog_open(public_url):
    with sync_playwright() as playwright:
        browser, context, page = open_skill_delete_dialog(playwright, public_url)
        try:
            page.click(".dialog-title")
            page.wait_for_timeout(200)
            backdrop_present = page.evaluate(
                "() => !!document.querySelector('.dialog-backdrop')"
            )
        finally:
            context.close()
            browser.close()

    assert backdrop_present is True
