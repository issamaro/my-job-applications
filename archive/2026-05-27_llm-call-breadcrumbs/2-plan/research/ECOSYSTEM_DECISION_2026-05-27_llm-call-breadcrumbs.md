date: 2026-05-27
shape: web-api (backend-only Python service)
runtime_constraint: python>=3.13
status: OK

## Runtime decision

The project's `pyproject.toml` pins `requires-python = ">=3.13"`, which serves as the authoritative existing runtime constraint. The Anthropic Python SDK documents a minimum requirement of Python 3.9 (with the MCP helpers sub-package requiring 3.10+), meaning Python 3.13 is fully inside its supported range. The `google-genai` Python SDK (pinned `>=1.0.0` in pyproject.toml) did not return indexed documentation from Context7; however, the Google Gen AI Python SDK 1.x series is known to target Python 3.9+ and the pyproject.toml already uses it against Python 3.13 in this project without a stated conflict. No library requires walking the runtime down from 3.13. The single shared constraint is **python>=3.13**, matching the project's declared floor exactly.

## Libraries

| library | resolved_id | latest_version | supports_runtime | status |
|---|---|---|---|---|
| anthropic | /anthropics/anthropic-sdk-python | unknown (context7 returned no version number; pyproject pins >=0.40.0) | yes — requires Python >=3.9; 3.13 confirmed compatible | ok |
| google-genai | not indexed in context7 | unknown (pyproject pins >=1.0.0) | assumed compatible — SDK 1.x targets Python >=3.9; no counter-evidence found | unknown_support |

## Conflicts

None.

## Open questions

1. **anthropic — latest stable version number**: Context7 confirmed Python >=3.9 support and that the SDK exists, but returned no explicit version string. Docs-researcher should query `/anthropics/anthropic-sdk-python` for the shape of `message.usage` (`input_tokens`, `output_tokens`, nullability) against the `>=0.40.0` pin.

2. **google-genai — not indexed in Context7**: The `google-genai` Python SDK (`google-genai` on PyPI, `from google import genai`) has no Context7 entry. Docs-researcher must use an alternative source (PyPI release history, GitHub `googleapis/python-genai`, or official Gemini API reference) to confirm:
   - Latest stable version and its Python floor.
   - Exact field names on `response.usage_metadata` returned from `client.aio.models.generate_content(...)` — suspected `prompt_token_count` and `candidates_token_count`, but unverified.
   - Whether any field can be `None` or `0` when the model returns no tokens.

## Docs-researcher dispatch targets

Both researchers should target **python>=3.13**.

- Researcher A: `/anthropics/anthropic-sdk-python` — query `message.usage` shape, `input_tokens`/`output_tokens` field types and nullability for `client.messages.create(...)`.
- Researcher B: `google-genai` Python SDK (PyPI / GitHub `googleapis/python-genai`) — query `response.usage_metadata` shape, exact field names for input/output token counts, nullability, async path `client.aio.models.generate_content(...)`.
