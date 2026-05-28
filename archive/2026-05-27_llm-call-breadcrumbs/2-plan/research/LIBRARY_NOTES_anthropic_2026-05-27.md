# Library Notes — anthropic Python SDK

```
library: anthropic
resolved_id: /anthropics/anthropic-sdk-python
installed_version: 0.75.0
version_constraint: >=0.40.0
runtime_constraint: Python >= 3.13
queried: 2026-05-27
source: .venv/lib/python3.13/site-packages/anthropic/types/usage.py (ground truth)
```

---

## Version compatibility

- `anthropic==0.75.0` is installed in this project's `.venv`.
- The package is generated from the OpenAPI spec via Stainless; the class
  definitions below are verbatim from the installed source.
- Python >= 3.13 is fully supported (no conflicts observed in package metadata).

---

## Patterns

### 1. `Usage` object — complete field inventory

Source: `.venv/lib/python3.13/site-packages/anthropic/types/usage.py`

```python
class Usage(BaseModel):
    input_tokens: int
    output_tokens: int
    cache_creation_input_tokens: Optional[int] = None
    cache_read_input_tokens: Optional[int] = None
    cache_creation: Optional[CacheCreation] = None
    server_tool_use: Optional[ServerToolUsage] = None
    service_tier: Optional[Literal["standard", "priority", "batch"]] = None
```

Full field table:

| Field | Type | Nullable / default |
|-------|------|--------------------|
| `input_tokens` | `int` | **Required — never None** |
| `output_tokens` | `int` | **Required — never None** |
| `cache_creation_input_tokens` | `int` | `Optional[int] = None` |
| `cache_read_input_tokens` | `int` | `Optional[int] = None` |
| `cache_creation` | `CacheCreation` | `Optional[CacheCreation] = None` |
| `server_tool_use` | `ServerToolUsage` | `Optional[ServerToolUsage] = None` |
| `service_tier` | `Literal["standard","priority","batch"]` | `Optional[...] = None` |

### 2. `input_tokens` / `output_tokens` nullability

`input_tokens` and `output_tokens` are declared as **bare `int`** with no
`Optional` wrapper and no default value. In Pydantic `BaseModel` semantics that
means they are **required fields** — the SDK will raise a validation error
rather than return a `Message` object where either is absent.

Conclusion: on any successful (non-exception) response, `message.usage.input_tokens`
and `message.usage.output_tokens` are always `int`, never `None`.

The `getattr(message.usage, "input_tokens", None)` pattern in the FEATURE_SPEC
is therefore safe but over-defensive: the fallback to `None` can only fire if
the attribute physically does not exist on the object, which cannot happen with
a properly deserialized `Usage`. In practice the expression always resolves to
an `int`. This means the NULL branch in the DB column is theoretically
unreachable for the Claude provider; tests only need to cover the populated
branch.

### 3. Nested types on `Usage`

**`CacheCreation`** (`.venv/…/anthropic/types/cache_creation.py`):

```python
class CacheCreation(BaseModel):
    ephemeral_1h_input_tokens: int   # required, never None
    ephemeral_5m_input_tokens: int   # required, never None
```

Present only when prompt caching with ephemeral TTLs is used. The parent field
`usage.cache_creation` is `Optional` — it is `None` when no ephemeral cache was
created.

**`ServerToolUsage`** (`.venv/…/anthropic/types/server_tool_usage.py`):

```python
class ServerToolUsage(BaseModel):
    web_search_requests: int   # required, never None
```

Present only when the model invoked a server-side tool (e.g., web search). The
parent field `usage.server_tool_use` is `Optional` — `None` on ordinary text
responses.

### 4. `message.content[0].text` access pattern

Confirmed canonical for non-streaming responses. From SDK README and Foundry
docs, both sync and async paths use this pattern:

```python
# sync
message = client.messages.create(model=..., max_tokens=..., messages=[...])
text = message.content[0].text

# async
message = await client.messages.create(model=..., max_tokens=..., messages=[...])
text = message.content[0].text
```

Context7 docs note: "Currently the API will only ever return 1 content block."
For a standard text generation request, `content[0]` is always a `TextBlock`
with a `.text` attribute. Guard with `content[0].type == "text"` only if the
request can also return tool-use blocks.

### 5. Breaking changes in `Usage` shape between 0.40.0 and 0.75.0

Context7 did not return changelog entries for this range. Ground-truth
observation from the installed 0.75.0 source: the class is auto-generated from
the OpenAPI spec. Fields present beyond a minimal `{input_tokens, output_tokens}`
baseline are all `Optional` with `= None` defaults, so older code that only
reads `input_tokens` / `output_tokens` continues to work. No field was removed
or had its type changed to `Optional` in the installed version.

The addition of `server_tool_use` and `service_tier` (newer fields) as
`Optional = None` means code running against 0.40.x that didn't reference those
fields is unaffected. No breaking change for the token-capture use case.

---

## Deprecated to avoid

none documented in the installed version for the `Usage` / `Message` surface
relevant to this slice.

---

## Open questions

- The exact version at which `cache_creation` (the nested object) was added vs.
  `cache_creation_input_tokens` (the flat int) is unknown — context7 did not
  surface a changelog. Both exist in 0.75.0. If the project must remain
  compatible with 0.40.x, treat `cache_creation` as always-None for safety
  (it is `Optional`) and read `cache_creation_input_tokens` directly.
- `service_tier` semantics ("standard" vs. "priority" vs. "batch") are not
  documented in the snippets context7 returned; consult the Anthropic API
  reference if tier-aware billing is needed.
