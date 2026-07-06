# Lean Code — BSD 3-Clause License — Vivian Voss, 2026
# Scope: Smoke-test the editorial Topbar shell reaches the served bundle.

import json
import socket
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright


def create_users_mock(page, full_name="Issa Maro"):
    def write_users_response(route, request):
        if request.method == "GET":
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "full_name": full_name,
                    "email": "test@example.com",
                }),
            )
        else:
            route.continue_()
    page.route("**/api/users", write_users_response)


PUBLIC_DIR = Path(__file__).parent.parent / "public"

SLOT_LABELS = [
    "Dashboard",
    "Pipeline",
    "Saved jobs",
    "Profile",
    "Tailor CV",
    "Interview prep",
]

DISABLED_SLOT_IDS = ["dashboard", "pipeline", "jobs", "interview"]


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


def create_loaded_page(playwright, public_url):
    browser = playwright.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    page.goto(public_url, wait_until="load")
    page.evaluate("() => document.fonts.ready")
    page.wait_for_selector(".topbar")
    return browser, context, page


def read_slot_color(page, slot_id):
    return page.evaluate(
        """(id) => {
            const el = document.querySelector(`[data-slot-id="${id}"]`);
            return window.getComputedStyle(el).color;
        }""",
        slot_id,
    )


def read_wordmark_color(page):
    return page.evaluate(
        """() => window.getComputedStyle(document.querySelector('.topbar-wordmark')).color"""
    )


def test_topbar_renders_at_top(public_url):
    with sync_playwright() as playwright:
        browser, context, page = create_loaded_page(playwright, public_url)
        try:
            page.wait_for_selector(".editor-main")
            topbar_parent_tag = page.evaluate(
                """() => document.querySelector('header.topbar').parentElement.tagName"""
            )
            topbar_precedes_screen = page.evaluate(
                """() => {
                    const topbar = document.querySelector('header.topbar');
                    const screen = document.querySelector('.editor-main');
                    if (!topbar || !screen) return false;
                    return topbar.compareDocumentPosition(screen) & Node.DOCUMENT_POSITION_FOLLOWING;
                }"""
            )
            wordmark_present = page.evaluate("() => !!document.querySelector('.topbar-wordmark')")
            slot_labels = page.evaluate(
                """() => Array.from(document.querySelectorAll('.topbar-slot')).map(el => el.textContent.trim())"""
            )
        finally:
            context.close()
            browser.close()

    assert topbar_parent_tag == "BODY"
    assert topbar_precedes_screen
    assert wordmark_present is True
    assert slot_labels == SLOT_LABELS


def test_no_legacy_tab_nav(public_url):
    with sync_playwright() as playwright:
        browser, context, page = create_loaded_page(playwright, public_url)
        try:
            legacy_present = page.evaluate(
                """() => !!document.querySelector('.tab-nav, [role="tablist"]')"""
            )
            resume_generator_button_present = page.evaluate(
                """() => Array.from(document.querySelectorAll('button')).some(b => b.textContent.trim() === 'Resume Generator')"""
            )
        finally:
            context.close()
            browser.close()

    assert legacy_present is False
    assert resume_generator_button_present is False


def test_active_slot_treatment(public_url):
    with sync_playwright() as playwright:
        browser, context, page = create_loaded_page(playwright, public_url)
        try:
            wordmark_color = read_wordmark_color(page)
            profile_color = read_slot_color(page, "profile")
            tailor_color = read_slot_color(page, "tailor")
            profile_border_width = page.evaluate(
                """() => window.getComputedStyle(document.querySelector('[data-slot-id="profile"]')).borderBottomWidth"""
            )
            profile_aria_current = page.evaluate(
                """() => document.querySelector('[data-slot-id="profile"]').getAttribute('aria-current')"""
            )
        finally:
            context.close()
            browser.close()

    assert profile_color == wordmark_color
    assert tailor_color != wordmark_color
    assert profile_border_width == "1px"
    assert profile_aria_current == "page"


def test_disabled_slots_inert(public_url):
    with sync_playwright() as playwright:
        browser, context, page = create_loaded_page(playwright, public_url)
        try:
            findings = page.evaluate(
                """(ids) => ids.map(id => {
                    const el = document.querySelector(`[data-slot-id="${id}"]`);
                    return {
                        id,
                        ariaDisabled: el.getAttribute('aria-disabled'),
                        tabindex: el.getAttribute('tabindex'),
                        pointerEvents: window.getComputedStyle(el).pointerEvents,
                    };
                })""",
                DISABLED_SLOT_IDS,
            )
            pre_click_resume_present = page.evaluate(
                """() => !!document.querySelector('.resume-generator')"""
            )
            page.click('[data-slot-id="dashboard"]', force=True)
            post_click_resume_present = page.evaluate(
                """() => !!document.querySelector('.resume-generator')"""
            )
            post_click_profile_present = page.evaluate(
                """() => !!document.querySelector('.profile-header')"""
            )
        finally:
            context.close()
            browser.close()

    for finding in findings:
        assert finding["ariaDisabled"] == "true", finding
        assert finding["tabindex"] == "-1", finding
        assert finding["pointerEvents"] == "none", finding
    assert pre_click_resume_present is False
    assert post_click_resume_present is False
    assert post_click_profile_present is True


def test_click_tailor_routes(public_url):
    with sync_playwright() as playwright:
        browser, context, page = create_loaded_page(playwright, public_url)
        try:
            page.click('[data-slot-id="tailor"]')
            page.wait_for_selector(".resume-generator")
            resume_present = page.evaluate(
                """() => !!document.querySelector('.resume-generator')"""
            )
            profile_present_after = page.evaluate(
                """() => !!document.querySelector('.profile-header')"""
            )
            wordmark_color = read_wordmark_color(page)
            tailor_color_after = read_slot_color(page, "tailor")
            profile_color_after = read_slot_color(page, "profile")
            tailor_aria_current = page.evaluate(
                """() => document.querySelector('[data-slot-id="tailor"]').getAttribute('aria-current')"""
            )
        finally:
            context.close()
            browser.close()

    assert resume_present is True
    assert profile_present_after is False
    assert tailor_color_after == wordmark_color
    assert profile_color_after != wordmark_color
    assert tailor_aria_current == "page"


def test_wordmark_renders(public_url):
    with sync_playwright() as playwright:
        browser, context, page = create_loaded_page(playwright, public_url)
        try:
            wordmark = page.evaluate(
                """() => {
                    const italic = document.querySelector('.topbar-wordmark-italic');
                    const roman = document.querySelector('.topbar-wordmark-roman');
                    const dot = document.querySelector('.topbar-wordmark-dot');
                    const italicStyle = window.getComputedStyle(italic);
                    const romanStyle = window.getComputedStyle(roman);
                    const dotStyle = window.getComputedStyle(dot);
                    return {
                        italicText: italic.textContent,
                        romanText: roman.textContent,
                        italicFontStyle: italicStyle.fontStyle,
                        romanFontStyle: romanStyle.fontStyle,
                        italicFontFamily: italicStyle.fontFamily,
                        romanFontFamily: romanStyle.fontFamily,
                        italicFontWeight: italicStyle.fontWeight,
                        romanFontWeight: romanStyle.fontWeight,
                        dotBackground: dotStyle.backgroundColor,
                        dotWidth: dotStyle.width,
                        dotHeight: dotStyle.height,
                        dotTransform: dotStyle.transform,
                        firstChildOfTopbarHasWordmarkClass: document.querySelector('.topbar').firstElementChild.classList.contains('topbar-wordmark'),
                    };
                }"""
            )
        finally:
            context.close()
            browser.close()

    assert wordmark["italicText"] == "my"
    assert wordmark["romanText"] == "CV"
    assert wordmark["italicFontStyle"] == "italic"
    assert wordmark["romanFontStyle"] == "normal"
    assert "Instrument Serif" in wordmark["italicFontFamily"]
    assert "Instrument Serif" in wordmark["romanFontFamily"]
    assert wordmark["italicFontWeight"] in ("400", "normal")
    assert wordmark["romanFontWeight"] in ("600", "bold")
    assert wordmark["dotBackground"] == "oklch(0.56 0.24 265)"
    assert wordmark["dotWidth"] == "4px"
    assert wordmark["dotHeight"] == "4px"
    assert "matrix" in wordmark["dotTransform"] or "translateY" in wordmark["dotTransform"]
    assert wordmark["firstChildOfTopbarHasWordmarkClass"] is True


def test_disabled_slots_visual_treatment(public_url):
    with sync_playwright() as playwright:
        browser, context, page = create_loaded_page(playwright, public_url)
        try:
            reference_ink_4_color = page.evaluate(
                """() => {
                    const probe = document.createElement('span');
                    probe.style.color = 'var(--ink-4)';
                    probe.style.display = 'none';
                    document.body.appendChild(probe);
                    const value = window.getComputedStyle(probe).color;
                    probe.remove();
                    return value;
                }"""
            )
            wordmark_color = read_wordmark_color(page)
            findings = page.evaluate(
                """(ids) => ids.map(id => {
                    const el = document.querySelector(`[data-slot-id="${id}"]`);
                    const style = window.getComputedStyle(el);
                    return { id, color: style.color, cursor: style.cursor };
                })""",
                DISABLED_SLOT_IDS,
            )
        finally:
            context.close()
            browser.close()

    assert reference_ink_4_color != ""
    assert reference_ink_4_color != wordmark_color
    for finding in findings:
        assert finding["color"] == reference_ink_4_color, finding
        assert finding["cursor"] == "not-allowed", finding


def test_search_pill_content(public_url):
    with sync_playwright() as playwright:
        browser, context, page = create_loaded_page(playwright, public_url)
        try:
            pill = page.evaluate(
                """() => {
                    const el = document.querySelector('.topbar-search');
                    const kbd = document.querySelector('.topbar-search-kbd');
                    return {
                        text: el.textContent,
                        kbdText: kbd.textContent.trim(),
                        kbdFontFamily: window.getComputedStyle(kbd).fontFamily,
                    };
                }"""
            )
            pre_click_view_state = page.evaluate(
                """() => !!document.querySelector('.profile-header')"""
            )
            page.click('.topbar-search')
            post_click_view_state = page.evaluate(
                """() => !!document.querySelector('.profile-header')"""
            )
        finally:
            context.close()
            browser.close()

    assert "Find a job, resume" in pill["text"]
    assert pill["kbdText"] == "⌘K"
    assert "JetBrains Mono" in pill["kbdFontFamily"]
    assert pre_click_view_state == post_click_view_state


def test_user_initials_circle(public_url):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        create_users_mock(page, "Issa Maro")
        page.goto(public_url, wait_until="load")
        page.wait_for_selector(".editor-main")
        page.wait_for_function(
            "() => document.querySelector('.topbar-user')?.textContent?.trim() === 'IM'"
        )
        try:
            user = page.evaluate(
                """() => {
                    const el = document.querySelector('.topbar-user');
                    const style = window.getComputedStyle(el);
                    return {
                        text: el.textContent.trim(),
                        width: style.width,
                        height: style.height,
                        borderRadius: style.borderRadius,
                        background: style.backgroundColor,
                        color: style.color,
                        fontFamily: style.fontFamily,
                        fontStyle: style.fontStyle,
                    };
                }"""
            )
        finally:
            context.close()
            browser.close()

    assert user["text"] == "IM"
    assert user["width"] == "30px"
    assert user["height"] == "30px"
    assert user["borderRadius"] == "50%"
    assert user["background"] == "oklch(0.16 0.04 265)"
    assert user["color"] == "oklch(0.97 0.01 260)"
    assert "Instrument Serif" in user["fontFamily"]
    assert user["fontStyle"] == "italic"


def test_keyboard_skips_disabled_slots(public_url):
    with sync_playwright() as playwright:
        browser, context, page = create_loaded_page(playwright, public_url)
        try:
            page.evaluate("() => document.body.focus()")
            page.keyboard.press("Tab")
            first_focused = page.evaluate(
                """() => document.activeElement.getAttribute('data-slot-id')"""
            )
            page.keyboard.press("Tab")
            second_focused = page.evaluate(
                """() => document.activeElement.getAttribute('data-slot-id')"""
            )
            page.keyboard.press("Tab")
            third_focused = page.evaluate(
                """() => document.activeElement.getAttribute('data-slot-id')"""
            )
        finally:
            context.close()
            browser.close()

    assert first_focused == "profile"
    assert second_focused == "tailor"
    assert third_focused not in DISABLED_SLOT_IDS


def test_keyboard_activates_slot(public_url):
    with sync_playwright() as playwright:
        browser, context, page = create_loaded_page(playwright, public_url)
        try:
            page.focus('[data-slot-id="tailor"]')
            page.keyboard.press("Enter")
            page.wait_for_selector(".resume-generator")
            after_enter = page.evaluate(
                """() => !!document.querySelector('.resume-generator')"""
            )
            page.focus('[data-slot-id="profile"]')
            page.keyboard.press("Space")
            page.wait_for_selector(".profile-header")
            after_space = page.evaluate(
                """() => !!document.querySelector('.profile-header')"""
            )
        finally:
            context.close()
            browser.close()

    assert after_enter is True
    assert after_space is True
