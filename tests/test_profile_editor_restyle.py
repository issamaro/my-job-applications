# Lean Code — BSD 3-Clause License — Vivian Voss, 2026
# Scope: Editorial restyle smoke tests for the profile editor.

import json
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


def open_editor(playwright, public_url, full_name="Issa Maro"):
    browser = playwright.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    create_users_mock(page, full_name)
    page.goto(public_url, wait_until="load")
    page.evaluate("() => document.fonts.ready")
    page.wait_for_selector(".editor-main")
    return browser, context, page


def test_editorial_page_frame(public_url):
    with sync_playwright() as playwright:
        browser, context, page = open_editor(playwright, public_url)
        try:
            eyebrow_text = page.evaluate(
                """() => {
                    const el = document.querySelector('.editor-header .eyebrow');
                    return el ? el.textContent.trim() : null;
                }"""
            )
            heading_text = page.evaluate(
                """() => {
                    const el = document.querySelector('.editor-title');
                    return el ? el.textContent.trim() : null;
                }"""
            )
            section_titles = page.evaluate(
                """() => Array.from(document.querySelectorAll('.editorial-section'))
                    .map(s => {
                        const num = s.querySelector('.editorial-section-header .num');
                        const title = s.querySelector('.editorial-section-title');
                        return {
                            number: num ? num.textContent.trim() : null,
                            title: title ? title.textContent.trim() : null,
                        };
                    })"""
            )
            column_max_width = page.evaluate(
                """() => window.getComputedStyle(document.querySelector('.editor-column')).maxWidth"""
            )
        finally:
            context.close()
            browser.close()

    assert eyebrow_text == "Workspace · profile"
    assert heading_text.startswith("Your") and "source of truth" in heading_text
    assert column_max_width == "940px"
    assert len(section_titles) == 7
    assert section_titles[0]["number"] == "№ 01"
    assert section_titles[0]["title"] == "Identity"
    assert section_titles[1]["number"] == "№ 02"
    assert section_titles[1]["title"] == "Summary"
    assert section_titles[2]["number"] == "№ 03"
    assert section_titles[2]["title"] == "Experience"
    assert section_titles[3]["number"] == "№ 04"
    assert section_titles[3]["title"] == "Education"
    assert section_titles[4]["number"] == "№ 05"
    assert section_titles[4]["title"] == "Skills"
    assert section_titles[5]["number"] == "№ 06"
    assert section_titles[5]["title"] == "Languages"
    assert section_titles[6]["number"] == "№ 07"
    assert section_titles[6]["title"] == "Projects"


def test_identity_grid_shape(public_url):
    with sync_playwright() as playwright:
        browser, context, page = open_editor(playwright, public_url)
        try:
            page.wait_for_selector(".identity-card")
            avatar_geom = page.evaluate(
                """() => {
                    const el = document.querySelector('.identity-avatar');
                    if (!el) return null;
                    const style = window.getComputedStyle(el);
                    return {
                        width: style.width,
                        height: style.height,
                        borderRadius: style.borderRadius,
                    };
                }"""
            )
            grid_columns = page.evaluate(
                """() => window.getComputedStyle(document.querySelector('.identity-grid')).gridTemplateColumns"""
            )
            grid_gap = page.evaluate(
                """() => window.getComputedStyle(document.querySelector('.identity-grid')).gap"""
            )
            row_labels = page.evaluate(
                """() => Array.from(document.querySelectorAll('.identity-grid .form-row label'))
                    .map(l => l.textContent.trim())"""
            )
            has_headline = page.evaluate(
                """() => Array.from(document.querySelectorAll('.identity-grid label'))
                    .some(l => /headline|title/i.test(l.textContent))"""
            )
        finally:
            context.close()
            browser.close()

    assert avatar_geom is not None
    assert avatar_geom["width"] == "96px"
    assert avatar_geom["height"] == "96px"
    assert avatar_geom["borderRadius"] == "50%"
    parts = grid_columns.split()
    assert len(parts) == 2, f"expected 2-column grid, got {grid_columns!r}"
    assert grid_gap == "12px"
    assert row_labels == ["Full name", "Email", "Phone", "Location", "LinkedIn"]
    assert has_headline is False


def test_skills_zero_state(public_url):
    def write_skills_empty(route, request):
        if request.method == "GET":
            route.fulfill(status=200, content_type="application/json", body="[]")
        else:
            route.continue_()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        create_users_mock(page, "Issa Maro")
        page.route("**/api/skills", write_skills_empty)
        page.goto(public_url, wait_until="load")
        page.wait_for_selector(".editor-main")
        page.wait_for_selector(".skill-cluster")
        try:
            pill_count = page.evaluate(
                """() => document.querySelectorAll('.skill-cluster .pill').length"""
            )
            add_pill_border_style = page.evaluate(
                """() => {
                    const el = document.querySelector('.skill-pill-add');
                    return el ? window.getComputedStyle(el).borderStyle : null;
                }"""
            )
            legacy_empty_present = page.evaluate(
                """() => {
                    const sections = Array.from(document.querySelectorAll('.editorial-section'));
                    const skills = sections.find(s => {
                        const t = s.querySelector('.editorial-section-title');
                        return t && t.textContent.trim() === 'Skills';
                    });
                    if (!skills) return null;
                    return !!skills.querySelector('.empty-state');
                }"""
            )
            page.click(".skill-pill-add")
            focused_id = page.evaluate("() => document.activeElement?.id")
        finally:
            context.close()
            browser.close()

    assert pill_count == 1
    assert add_pill_border_style == "dashed"
    assert legacy_empty_present is False
    assert focused_id == "skill-input"


def test_initials_helper_edge_cases(public_url):
    cases = [
        ("Issa Maro", "IM"),
        ("Ada", "A"),
        ("  Ada   Byron  Lovelace ", "AL"),
        ("", "??"),
        ("   ", "??"),
    ]
    with sync_playwright() as playwright:
        for full_name, expected in cases:
            browser = playwright.chromium.launch()
            context = browser.new_context()
            page = context.new_page()
            create_users_mock(page, full_name)
            page.goto(public_url, wait_until="load")
            page.wait_for_selector(".editor-main")
            page.wait_for_function(
                f"() => document.querySelector('.topbar-user')?.textContent?.trim() === {json.dumps(expected)}"
            )
            actual = page.evaluate(
                "() => document.querySelector('.topbar-user').textContent.trim()"
            )
            context.close()
            browser.close()
            assert actual == expected, f"parseInitials({full_name!r}) DOM={actual!r}, expected {expected!r}"


def test_readprofile_coalesces_one_request(public_url):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        call_count = {"n": 0}
        def write_users_response(route, request):
            if request.method == "GET":
                call_count["n"] += 1
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
        page.goto(public_url, wait_until="load")
        page.wait_for_selector(".editor-main")
        page.wait_for_timeout(500)
        try:
            assert call_count["n"] == 1, (
                f"readProfile coalescing failed: "
                f"{call_count['n']} GETs to /api/users (expected 1)"
            )
        finally:
            context.close()
            browser.close()


def test_no_legacy_color_tokens_in_components():
    forbidden = re.compile(r'--color-border|--color-primary-rgb|--color-text-rgb|#e0e0e0')
    repo_root = Path(__file__).parent.parent
    files = [
        "src/components/ProfileEditor.svelte",
        "src/components/UserProfile.svelte",
        "src/components/WorkExperience.svelte",
        "src/components/Education.svelte",
        "src/components/Skills.svelte",
        "src/components/Languages.svelte",
        "src/components/Projects.svelte",
    ]
    for f in files:
        content = (repo_root / f).read_text()
        matches = forbidden.findall(content)
        assert matches == [], f"{f} contains legacy color tokens: {matches}"


def test_no_token_bypass_in_overlay_components():
    forbidden = re.compile(
        r'#008800|#cc0000|#aa0000|#f0f0f0|rgb\(204 102 0'
        r'|--color-text-secondary|--color-bg,'
    )
    repo_root = Path(__file__).parent.parent
    files = [
        "src/components/Toast.svelte",
        "src/components/LanguageSelector.svelte",
        "src/components/PhotoUpload.svelte",
        "src/components/ImportModal.svelte",
        "src/components/ConfirmDialog.svelte",
    ]
    for f in files:
        content = (repo_root / f).read_text()
        matches = forbidden.findall(content)
        assert matches == [], f"{f} bypasses editorial tokens: {matches}"


def test_overlay_styles_reach_bundle():
    bundle = PUBLIC_DIR / "build" / "bundle.css"
    if not bundle.exists():
        pytest.skip("public/build/bundle.css missing — run `bun run build` first")
    css = bundle.read_text()

    assert re.search(r"\.toast-success[^{}]*\{[^}]*var\(--positive\)", css)
    assert re.search(r"\.toast-error[^{}]*\{[^}]*var\(--negative\)", css)
    assert re.search(r"\.warning-box[^{}]*\{[^}]*var\(--warn-soft\)", css)
    assert "#008800" not in css
    assert "rgb(204 102 0" not in css
    assert "--color-text-secondary" not in css


def test_summary_textarea_renders_serif_treatment(public_url):
    with sync_playwright() as playwright:
        browser, context, page = open_editor(playwright, public_url)
        try:
            styles = page.evaluate(
                """() => {
                    const el = document.querySelector('.summary-textarea');
                    if (!el) return null;
                    const computed = window.getComputedStyle(el);
                    return {
                        fontFamily: computed.fontFamily,
                        fontStyle: computed.fontStyle,
                        fontSize: computed.fontSize,
                    };
                }"""
            )
        finally:
            context.close()
            browser.close()

    assert styles is not None, "summary textarea not found"
    assert styles["fontStyle"] == "italic"
    assert styles["fontSize"] == "18px"
    assert "Instrument Serif" in styles["fontFamily"]
