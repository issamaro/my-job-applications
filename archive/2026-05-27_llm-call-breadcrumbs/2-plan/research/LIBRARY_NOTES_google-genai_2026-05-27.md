library: google-genai (PyPI: google-genai, import: from google import genai)
resolved_id: NOT FOUND in context7 directly — closest match /google-gemini/genai-processors is the pipeline wrapper, NOT the SDK
version_constraint: >=1.0.0
runtime_constraint: Python >= 3.13
queried: 2026-05-27

---

## context7 coverage

context7 does NOT index the `google-genai` Python SDK (`pip install google-genai`).
The only Google GenAI library indexed is `/google-gemini/genai-processors` (pipeline abstraction on top of the SDK)
and `/googleapis/js-genai` (the JavaScript/TypeScript equivalent SDK).

The JS SDK (`/googleapis/js-genai`) shares the same underlying Gemini API schema, so its type definitions
for `GenerateContentResponse` and `GenerateContentResponseUsageMetadata` are authoritative for field names —
the Python SDK exposes the same proto-derived fields under snake_case.


---

## Version compatibility

No Python-SDK-specific version data available from context7.
The `google-genai` package targets Python 3.9+ in practice; Python 3.13 is compatible with no known conflicts.
The `>=1.0.0` constraint is the stable GA surface; 0.x was a pre-release with a different import structure.


---

## Patterns

### 1. usage_metadata shape on GenerateContentResponse

Source: `/googleapis/js-genai` — `GenerateContentResponseUsageMetadata` class definition and API report.

The JS SDK (same proto surface, camelCase → snake_case in Python) defines:

```
GenerateContentResponseUsageMetadata
  prompt_token_count            int | None   — total tokens in the input prompt
  candidates_token_count        int | None   — total tokens in all generated candidates
  cached_content_token_count    int | None   — tokens served from cache
  thoughts_token_count          int | None   — tokens used for model reasoning (Gemini 2.x thinking models)
  tool_use_prompt_token_count   int | None   — tokens in tool-use prompts
  total_token_count             int | None   — prompt + candidates + tool-use total
  prompt_tokens_details         list | None  — per-modality breakdown of prompt tokens
  candidates_tokens_details     list | None  — per-modality breakdown of candidate tokens
  cache_tokens_details          list | None  — per-modality breakdown of cached tokens
  tool_use_prompt_tokens_details list | None — per-modality breakdown of tool-use tokens
  traffic_type                  str | None   — TrafficType enum value
```

All fields are marked **Optional** in the JS SDK type definition; assume the same in Python.

### 2. Exact field names for input / output token counts

| purpose | Python field name | JS equivalent |
|---|---|---|
| input (prompt) tokens | `prompt_token_count` | `promptTokenCount` |
| output (candidates) tokens | `candidates_token_count` | `candidatesTokenCount` |

**Caller's guess was correct for both.**
`prompt_token_count` = input. `candidates_token_count` = output.

### 3. Is usage_metadata always present?

**No.** From the JS SDK definition:

> `usageMetadata` (Optional) — "Usage metadata about the response(s)"

It is typed as optional on `GenerateContentResponse`. In practice the Gemini API omits it on
error responses, safety-blocked responses (where no candidates are returned), and certain streaming
chunks. For non-streaming calls with a normal completion it is reliably present, but the field
itself can be `None` and any individual sub-field can also be `None`.

Confirmed optionality chain: `response.usage_metadata` can be `None`; if present, every sub-field
(including `prompt_token_count` and `candidates_token_count`) is individually optional / `None`.

### 4. Are token-count fields always int?

**No.** Every field on `GenerateContentResponseUsageMetadata` is marked Optional in the JS SDK
(meaning `number | undefined` in TS, `int | None` in Python). They are integers when present.
The spec's defensive `try/except AttributeError` pattern is correct AND insufficient on its own —
a `None` check is also needed before using the values as integers.

Recommended read pattern:

```python
usage = getattr(response, "usage_metadata", None)
input_tokens = int(usage.prompt_token_count) if usage and usage.prompt_token_count is not None else None
output_tokens = int(usage.candidates_token_count) if usage and usage.candidates_token_count is not None else None
```

### 5. Canonical access for text output (non-streaming)

Source: `/googleapis/js-genai` — `GenerateContentResponse` getter methods.

```
response.text   →  str | None   (getter returning text from first candidate)
```

The JS SDK documents `text` as a getter on `GenerateContentResponse` that returns
`string | undefined`. The Python SDK mirrors this: `response.text` is the canonical
one-liner for non-streaming text retrieval. For `response_mime_type="application/json"`,
`response.text` returns the raw JSON string — the caller must then `json.loads(response.text)`.


---

## Deprecated to avoid

none documented — context7 has no Python SDK deprecation notes. The 0.x pre-release import
structure (`import google.generativeai`) is the prior package (`google-generativeai`), not a
deprecated path within `google-genai` >=1.0.0.


---

## Open questions (context7 could not answer)

1. **Python-specific behavior of `response.text` with `response_mime_type="application/json"`**:
   The JS SDK confirms `text` returns the raw string content. Whether the Python SDK auto-parses
   JSON or returns the raw string is not documented in context7. First-party Python SDK docs or
   source at `https://github.com/googleapis/python-genai` should be checked. Safe assumption:
   treat it as a raw string and call `json.loads()` explicitly.

2. **`candidates_token_count` vs `candidate_token_count` spelling**: the JS SDK uses
   `candidatesTokenCount` (plural). Python equivalent is `candidates_token_count`. If the SDK
   uses the singular form `candidate_token_count`, the populated path will silently return `None`
   via the `getattr` guard. **Verify once by printing `vars(response.usage_metadata)` in a live
   test call before shipping.**

3. **`usage_metadata` on safety-blocked responses**: not confirmed whether the field is present
   with zero counts or absent entirely when the response is blocked. The `None` guard above covers
   the absent case.
