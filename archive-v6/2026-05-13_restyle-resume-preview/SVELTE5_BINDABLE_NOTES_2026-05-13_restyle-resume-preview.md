# Svelte 5 — $bindable + $effect writeback pattern
library: svelte
resolved_id: /sveltejs/svelte
version_constraint: svelte@5.37.0 (latest stable in ^5 at query time)
runtime_constraint: none specified
queried: 2026-05-13
doc_snapshot: context7 source pinned to svelte@5.37.0 / svelte@5.36.17


---


## Version compatibility

Docs confirm runes (`$state`, `$props`, `$bindable`, `$effect`, `$derived`) are the stable Svelte 5 surface. No version gate beyond "Svelte 5 runes mode" was cited for any of the five patterns below. The `$bindable` rune is documented as the canonical two-way-binding primitive; no changelog mention of it being unstable in early ^5 sub-releases was returned by context7.


---


## Patterns


### Q1 — `$bindable()` as a child-exposed prop / parent `bind:` idiom

**Status: VALIDATED — this is the documented canonical idiom.**

Child:
```svelte
<script>
  let { count = $bindable(0) } = $props();
</script>
```

Parent:
```svelte
<WorkExperience bind:count={workExperienceCount} />
```

Source: `documentation/docs/02-runes/06-$bindable.md` and `documentation/docs/03-template-syntax/12-bind.md`.

The docs explicitly state:
- `$bindable` is used inside `$props()` to declare that a prop can be bound to by the parent.
- The parent uses the `bind:` directive. The parent does NOT have to use `bind:` — it can pass a plain prop — but `bind:` is required for two-way flow.
- The default value passed to `$bindable(default)` is returned when the parent does not provide the prop at all.

**Pitfall:** Using `$bindable` on a prop that the parent passes as a plain reactive state proxy (not via `bind:`) and then mutating it from the child triggers `ownership_invalid_mutation`. The `bind:` directive is what grants the child mutation rights.

**Version note:** No specific sub-release gate documented. Pattern is stable across the ^5 range per current docs.


---


### Q2 — Warnings when an `$effect` writes to a `$bindable` prop

**Status: PARTIALLY documented — no warning specific to `$bindable` writeback, but `effect_update_depth_exceeded` is the operative hazard.**

Three warnings were researched:

| Warning | Fires when | Applies here? |
|---|---|---|
| `effect_update_depth_exceeded` | An effect reads and writes the same state, causing it to re-run in a loop beyond Svelte's internal depth limit. Svelte intervenes before a browser crash. | YES — potential, see Q5. |
| `ownership_invalid_mutation` | A child mutates a prop that is a reactive state proxy but was NOT declared `$bindable`. | NO — `$bindable` is the explicit escape hatch that authorises the mutation. Writing `count = items.length` on a `$bindable` prop does NOT trigger this warning. |
| `binding_property_non_reactive` | Not returned by context7 for this query. | Open question — see below. |
| `state_unsafe_mutation` | Not returned by context7 for this query. | Open question — see below. |

Source: `packages/svelte/messages/client-errors/errors.md`, `packages/svelte/messages/client-warnings/warnings.md`, `documentation/docs/02-runes/05-$props.md`.

**Key doc quote on `ownership_invalid_mutation`:** "Mutating unbound props is strongly discouraged... To fix this, either create callback props to communicate changes, or mark the prop as `$bindable`." — confirms `$bindable` is the authorised path and does not itself trigger the warning.


---


### Q3 — Is `untrack()` required, recommended, or harmful for the `$effect` writeback?

**Status: DOCUMENTED — not required in the straightforward case; required only if the effect reads AND writes the same reactive value, causing a loop.**

Doc guidance (verbatim from `documentation/docs/02-runes/04-$effect.md`):

> "In the rare cases where you really _do_ need to write to state in an effect — which you should avoid — you can read the state with `untrack` to avoid adding it as a dependency."

And from `packages/svelte/messages/client-errors/errors.md` (`effect_update_depth_exceeded`):

> "If an effect updates some state that it also depends on, it will re-run, potentially in a loop... you can read the state with `untrack` to avoid adding it as a dependency."

**Applied to `count = items.length`:**

The effect dependency is `items` (read). The write target is `count` (a `$bindable`). These are different reactive values. The effect does NOT read `count` — it only writes it. Therefore the effect's dependency set is `{items}` only, and `count = items.length` does not add `count` as a dependency. No loop is structurally produced by this alone.

`untrack()` is therefore **not required** for this specific shape. It would only be needed if the effect also read `count` (e.g. `count = count + items.length`).

**Pitfall:** If the parent's template re-renders and passes a new `count` value back to the child (e.g. the parent modifies `workExperienceCount` independently), that would change `count` inside the child, but the child's `$effect` only re-runs when `items` changes — not when `count` changes (because `count` is only written, never read, in the effect). So no loop from that direction either.


---


### Q4 — Idiomatic alternatives for "child has reactive state, parent reads a derived value"

**Status: DOCUMENTED — three alternatives exist; none is strictly more idiomatic than `$bindable` for this use-case.**

**Option A — `bind:this` + instance export (functions only)**

The docs show that in Svelte 5 runes mode, `export function foo()` from a child's `<script>` is accessible via `bind:this={ref}` as `ref.foo()`. However the migration guide explicitly states:

> "Bindings to component exports are not allowed [in runes mode]. Having `export const foo = ...` and then `<A bind:foo />` causes an error. Use `bind:this` instead — `<A bind:this={a} />` — and access the export as `a.foo`."

**Limitation:** `bind:this` gives imperative method/property access, NOT reactive tracking. Reading `ref.count` in the parent template does NOT auto-update when `count` changes inside the child. This approach is for imperative API calls, not reactive data flow. Not a valid replacement here.

**Option B — `export const` / `export function` bound directly via `bind:foo`**

Explicitly disallowed in runes mode per migration guide (cited above). Will error.

**Option C — Shared `.svelte.js` runed module**

Not explicitly documented as the canonical alternative in the snippets returned. Context7 did not return a doc snippet showing a `.svelte.js` shared store as the recommended pattern for this specific "child count → parent" use case. This is an open question (see below).

**Conclusion:** For "child has internal array, parent needs `array.length` as a reactive integer," `$bindable` + `$effect` writeback is the only fully-documented reactive path from child to parent in Svelte 5 runes mode. The `$derived` alternative only applies inside a single component scope.


---


### Q5 — Re-render loop risk: does parent re-render re-trigger the child's `$effect`?

**Status: DOCUMENTED — the specific shape used here does NOT loop, but the general class of loop is real and has a hard error.**

**Mechanism of `effect_update_depth_exceeded` (verbatim from docs):**

> "Maximum update depth exceeded. This typically indicates that an effect reads and writes the same piece of state. If an effect updates some state that it also depends on, it will re-run, potentially in a loop: (Svelte intervenes before this can crash your browser tab.)"

**Applied to the described pattern:**

- Child `$effect` reads `items`, writes `count`.
- Parent re-renders because `workExperienceCount` (bound to `count`) changed.
- Parent re-render does NOT change `items` inside the child.
- The child's `$effect` only re-runs when its tracked dependencies (`items`) change.
- Therefore the parent re-render does not re-trigger the child's `$effect`.

**The loop is structurally absent** because the write target (`count`) and the read dependency (`items`) are distinct reactive values.

**Svelte's documented termination guarantee:** Svelte does NOT guarantee termination in a general sense — it intervenes and throws `effect_update_depth_exceeded` as a hard error if the depth is exceeded. There is no silent infinite loop; the framework crashes loudly rather than hanging the tab. This is the safety net, not a loop-free guarantee.

**Concrete loop that WOULD occur** (to avoid):

```svelte
// WRONG — effect reads count AND writes count
$effect(() => {
  count = items.length + count; // reads count → writes count → re-runs → error
});
```

The pattern in the plan (`count = items.length`) does not read `count`, so this pitfall does not apply.


---


## Deprecated to avoid

- `export const foo = ...` combined with `bind:foo` on a component — disallowed in runes mode, will error.
- Using `$:` reactive statements for side effects — Svelte 4 legacy, replaced by `$effect` in Svelte 5.
- Mutating a prop that is a reactive state proxy without `$bindable` — triggers `ownership_invalid_mutation`.


---


## Open questions

1. **`binding_property_non_reactive` and `state_unsafe_mutation`** — context7 did not return documentation for these two specific warning identifiers in the context of `$bindable` writeback. Recommend checking `packages/svelte/messages/client-warnings/warnings.md` in the sveltejs/svelte repo directly for the full warning registry.

2. **Shared `.svelte.js` runed module as idiomatic alternative** — context7 did not return a canonical doc example showing a `.svelte.js` shared reactive module used as the recommended pattern for cross-component derived state. Web search or the official Svelte 5 blog posts may have more specific guidance.

3. **Sub-release where `$bindable` became stable** — context7 returned no changelog or release-notes snippet pinning a specific ^5.x.0 stabilisation point. The docs treat it as uniformly stable across Svelte 5.
