# Playwright Python — Library Notes

```
library: playwright (Python binding)
resolved_id: /websites/playwright_dev_python
version_constraint: >=1.40.0
runtime_constraint: python>=3.13
queried: 2026-05-11
```

---

## Version compatibility

Playwright Python >= 1.40.0 is required (per pyproject.toml). Python 3.13 is supported —
Playwright Python tracks CPython releases closely and 3.13 is within the supported range.
No version-specific conflicts identified from docs queried.

`playwright install` (or `playwright install chromium`) must be run once on any fresh
checkout to download browser binaries. There is no automatic guard — the test will fail
with an error about missing executables if the binary is absent. See "Binary guard pattern"
below.

---

## Patterns

### 1. `sync_playwright()` context manager

Canonical import and usage — no pytest-playwright plugin required:

```python
from playwright.sync_api import sync_playwright, Playwright

def run(playwright: Playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com")
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
```

Inside a plain pytest function (no plugin):

```python
from playwright.sync_api import sync_playwright

def test_smoke():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        # ... assertions ...
        context.close()
        browser.close()
```

Pitfalls:
- Do NOT use `async_playwright` — this is the sync path.
- The `with sync_playwright() as playwright:` block does NOT auto-close the browser.
  You must call `browser.close()` (and `context.close()`) explicitly, or use a try/finally.
- Source: playwright.dev/python/docs/library, playwright.dev/python/docs/api/class-frame

---

### 2. `page.evaluate(expression)` — computed style dict in one round trip

Signature (sync):

```python
result = page.evaluate(expression)          # expression only
result = page.evaluate(expression, arg)     # expression + serializable argument
```

Fetching multiple computed style values in a single round trip — return a dict from JS:

```python
styles = page.evaluate("""() => {
    const computed = window.getComputedStyle(document.body);
    return {
        backgroundColor:       computed.backgroundColor,
        color:                 computed.color,
        fontFamily:            computed.fontFamily,
        fontSize:              computed.fontSize,
        lineHeight:            computed.lineHeight,
        fontFeatureSettings:   computed.fontFeatureSettings,
        webkitFontSmoothing:   computed.webkitFontSmoothing,  // see note below
    };
}""")
assert styles["backgroundColor"] == "rgb(244, 241, 236)"
```

Note on `-webkit-font-smoothing`: this is a non-standard CSS property. `getComputedStyle`
may not expose it in Chromium headless. Use `document.body.style.webkitFontSmoothing`
or query via `page.evaluate("() => document.body.style.webkitFontSmoothing")` if
`getComputedStyle` returns an empty string. Treat as an open question — see section below.

Pitfalls:
- The return value must be JSON-serializable. A plain dict of strings is fine.
- Do NOT use the async form (`await page.evaluate(...)`) in the sync API.
- Source: playwright.dev/python/docs/evaluating, playwright.dev/python/docs/api/class-page

---

### 3. `page.goto(url)` — wait_until and font loading

Signature:

```python
page.goto(url)
page.goto(url, wait_until="load")   # default
page.goto(url, wait_until="networkidle")   # DISCOURAGED (see below)
```

`wait_until` options: `"commit"`, `"domcontentloaded"`, `"load"` (default), `"networkidle"`.

The docs explicitly mark `networkidle` as **DISCOURAGED** for testing:
> "Don't use this method for testing, rely on web assertions to assess readiness instead."

For font loading — `document.fonts.ready` is a browser Promise. Use
`page.wait_for_function` after `goto` to block until fonts are ready:

```python
page.goto("http://localhost:<port>/", wait_until="load")
page.wait_for_function("() => document.fonts.ready.then(() => true)")
```

Or equivalently, evaluate and rely on the Promise resolving:

```python
page.goto("http://localhost:<port>/", wait_until="load")
page.evaluate("() => document.fonts.ready")
```

`page.evaluate` waits for returned Promises to resolve, so the second form is clean and
sufficient. Fonts will be fully loaded before control returns.

Pitfalls:
- `wait_until="load"` fires when the `load` event fires, which includes stylesheets but
  does NOT guarantee all web fonts have finished rendering. Use `document.fonts.ready`.
- `networkidle` is explicitly discouraged by the docs — don't use it.
- Source: playwright.dev/python/docs/api/class-page, playwright.dev/python/docs/api/class-frame

---

### 4. `browser.new_context()` + `context.new_page()` vs `browser.new_page()`

The docs are explicit:

> `browser.new_page()` is a convenience API that should only be used for single-page
> scenarios and short snippets. Production code and testing frameworks should explicitly
> create `browser.new_context()` followed by `browser_context.new_page()` to control
> their exact life times.

Recommended pattern for a pytest fixture:

```python
context = browser.new_context()
page = context.new_page()
# ... test ...
context.close()
browser.close()
```

`browser.new_page()` is fine for a throwaway smoke test. For a test file that may grow,
use the explicit context pattern from the start.

Pitfalls:
- Closing the page returned by `browser.new_page()` also closes its implicitly created
  context. This can cause surprising teardown ordering if you hold references.
- Source: playwright.dev/python/docs/api/class-browser

---

### 5. Headless mode default

From the docs:
> "By default, Playwright executes browser automation in headless mode, meaning the
> browser UI is not visible."

`headless=True` is the default. You do not need to pass it explicitly. To run headed
(for local debugging only):

```python
browser = playwright.chromium.launch(headless=False, slow_mo=100)
```

For CI and the smoke test, omit the argument entirely:

```python
browser = playwright.chromium.launch()   # headless by default
```

Pitfalls:
- Being explicit with `headless=True` is harmless and documents intent — acceptable.
- Source: playwright.dev/python/docs/debug

---

### 6. Closing / cleanup inside `with sync_playwright()`

The `with sync_playwright() as p:` block does NOT auto-close browsers or contexts.
You own the lifecycle. Pattern with try/finally for safe teardown:

```python
with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    try:
        context = browser.new_context()
        page = context.new_page()
        # ... test body ...
        context.close()
    finally:
        browser.close()
```

Or as a pytest fixture:

```python
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture()
def chromium_page():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        yield page
        context.close()
        browser.close()
```

Pitfalls:
- Omitting `browser.close()` leaves a zombie process in the test run.
- The `with` block alone is not sufficient teardown.
- Source: playwright.dev/python/docs/library, playwright.dev/python/docs/api/class-browser

---

### Binary guard pattern (fail-fast if `playwright install` was not run)

No built-in guard is documented. A reliable pattern:

```python
import shutil
import pytest

def check_chromium_binary():
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as playwright:
            playwright.chromium.launch().close()
    except Exception as error:
        pytest.skip(f"Chromium binary not installed — run: playwright install chromium\n{error}")
```

Call this at the top of the test or in the fixture before `launch()`.

---

## pytest-playwright plugin — verdict

pip name: `pytest-playwright`  
uv: `uv add --dev pytest-playwright`

It provides `page`, `browser`, `context`, and `playwright` fixtures automatically,
eliminating the manual `sync_playwright()` boilerplate. It also handles headless/headed
toggling via `--headed` CLI flag and installs cleanup automatically.

For a single smoke test it is lightweight overhead unless the project already uses it.
If `tests/` grows beyond one or two files, adding it pays off quickly. It is NOT
required — the manual fixture shown in pattern 6 is fully equivalent.

---

## Deprecated APIs to avoid

- `networkidle` as a `wait_until` value — docs mark it explicitly as discouraged for
  testing. Use `"load"` + `page.evaluate("() => document.fonts.ready")` instead.
- No other deprecated APIs encountered in the queried patterns.

---

## Open questions

1. **`webkitFontSmoothing` via `getComputedStyle`** — `-webkit-font-smoothing` is
   non-standard. Chromium headless may return an empty string from `getComputedStyle`.
   The correct property key and whether it is readable in headless Chromium was not
   confirmed by context7 docs. Recommend querying
   `window.getComputedStyle(document.body).getPropertyValue("-webkit-font-smoothing")`
   and verifying against a headed run or skipping the assertion if it returns `""`.

2. **`document.fonts.ready` in `page.evaluate` (sync)** — The sync `page.evaluate`
   docs confirm it waits for returned Promises to resolve, but no Python-specific example
   for `document.fonts.ready` appeared in the docs. The pattern shown above is derived
   from the general Promise-resolution guarantee — treat as verified-by-inference, not
   by an explicit doc example.
