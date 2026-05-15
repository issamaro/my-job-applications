// Lean Code — BSD 3-Clause License — Vivian Voss, 2026
// Scope: Svelte 5 runes patterns for the restyle-profile-editor feature (slice 3).

---
library: svelte
resolved_id: /sveltejs/svelte
version_constraint: ^5.0.0
runtime_constraint: none
queried: 2026-05-13
---

## Version compatibility

Svelte 5 ships universal reactivity via runes. All patterns below require `.svelte.js` / `.svelte.ts` file extensions for non-component reactive modules. The runes API (`$state`, `$derived`, `$effect`, `$props`) is stable as of 5.x.

---

## Patterns

### 1. Module-scoped runes store (singleton)

Canonical form — export the `$state` object directly:

```js
// file: profile.svelte.js
export const profile = $state({
  full_name: '',
  title: '',
  summary: '',
});
```

Components import and mutate properties directly:

```js
import { profile } from './profile.svelte.js';
profile.full_name = 'Issa';
```

**Pitfall:** Do NOT `export let count = $state(0)` with a bare primitive — Svelte cannot track cross-module reassignment of a let binding. Object properties are fine; primitive lets are not.

**Second valid pattern** (when the raw state must be private): use a module-private `let` and export getter/setter functions:

```js
let _count = $state(0);
export function getCount() { return _count; }
export function increment() { _count += 1; }
```

For a profile store with an object, the `export const store = $state({...})` form is simpler and canonical.

Source: `$state.md` — "Sharing state by exporting an object with $state properties"; `stores.md` — "Defining Shared Reactive State with Svelte Runes".

---

### 2. Cross-component reactivity from module-scoped state

**Yes — confirmed.** Any component that reads `store.profile.full_name` in its template will reactively re-render when that property mutates, regardless of which component performed the mutation. The Svelte docs show exactly this pattern: one component mutates `userState.name`, another renders it, and reactivity flows automatically.

Source: `stores.md` — "Importing and Using Shared $state in a Svelte Component".

---

### 3. `$effect` on mount for async load

Pattern:

```svelte
<script>
  import { store } from './store.svelte.js';

  $effect(() => {
    void store.load();
  });
</script>
```

Semantics:
- `$effect` runs after the component mounts (after the DOM is created).
- Return a function from the callback for cleanup — it fires before re-run and on component destroy.
- `void` suppresses the Promise return value; `$effect` does not accept an async callback directly (returning a Promise instead of `undefined | (() => void)` is incorrect).

**Idempotent load called by two components (Topbar + UserProfile):** Safe as long as `store.load()` itself coalesces in-flight requests (see pattern 4). `$effect` will fire once per component mount — so `store.load()` is called twice. With promise coalescing in the store, the second call returns the already-in-flight promise and no duplicate fetch occurs.

`onMount` from `svelte` is an alternative — it accepts async callbacks directly and its return value is the cleanup function. Either approach works; `$effect` is the runes-native choice.

Source: `$effect.md` — "An effect can return a teardown function"; `$effect.md` — "Understanding lifecycle".

---

### 4. In-flight promise coalescing

No Svelte-specific mechanism. Implement in the store module as a plain JS variable:

```js
// profile.svelte.js
export const profile = $state({ full_name: '', loading: false });

let _pending = null;

export function readProfile() {
  if (_pending) return _pending;
  profile.loading = true;
  _pending = fetch('/api/profile')
    .then(r => r.json())
    .then(data => { Object.assign(profile, data); })
    .finally(() => { profile.loading = false; _pending = null; });
  return _pending;
}
```

`_pending` is a module-level let (not `$state`) — it is not reactive, just a guard. No Svelte-specific gotcha here.

Source: no Svelte-specific doc; pattern derived from standard JS module singleton behavior confirmed by `/sveltejs/svelte` docs.

---

### 5. `$state` with nested objects — deep mutation

**Deeply reactive by default.** Mutating `store.profile.full_name = 'Issa'` is reactive without spreading. Svelte wraps the object in a Proxy that tracks property-level writes.

Use `$state.raw` only when you want to opt out of deep reactivity (e.g., large API payloads that are only ever reassigned wholesale). With `$state.raw`, property mutation has no effect — only full reassignment triggers reactivity.

```js
// Deep mutation — reactive, correct for profile store:
store.profile.full_name = 'Issa'; // triggers re-render

// $state.raw — NOT deeply reactive:
let raw = $state.raw({ full_name: '' });
raw.full_name = 'Issa'; // NO effect
raw = { full_name: 'Issa' }; // OK, triggers re-render
```

Source: `$state.md` — "Using $state.raw for Non-Deeply Reactive State"; `best-practices.md`.

---

### 6. Snippets vs prop passing (`{#snippet}` / `{@render}`)

`{#snippet}` + `{@render}` is the Svelte 5 replacement for named slots. Slots are deprecated in Svelte 5 but still functional. The two are not interchangeable when the child uses `{@render}` — you cannot pass slot content to a component expecting `{@render}`.

Decision for this slice: the rejection of snippets for the Summary section stands. Snippets are a content-projection tool, not a state-sharing tool — not relevant to the runes store work.

Source: `v5-migration-guide.md` — "Replacing Named Slots with Props and Render Tags"; `snippet.md`.

---

### 7. Testing module-scoped runes from non-Svelte code (Playwright)

Context7 returned no Svelte-specific docs on this. Based on the module semantics:

- Module-scoped `$state` values are JS Proxy objects that live in the browser's module registry.
- `page.evaluate()` can read DOM output (e.g., `document.querySelector('[data-testid="full-name"]').textContent`) but cannot directly import ES module state without an exposed global.
- For `parseInitials`, the function is pure JS — test it directly in Python/Pytest via `page.evaluate('parseInitials("Issa Casas")')` only if the function is attached to `window`. Otherwise, test through DOM assertions.

**Recommendation:** expose the function via `window.__parseInitials = parseInitials` in a test-only build, or test solely through DOM output.

Listed under open questions — no clean doc answer found.

---

### 8. `bind:value` against a store property

**Works directly.** `bind:value` accepts any assignable expression, including a property path into a reactive `$state` object:

```svelte
<input bind:value={store.profile.full_name} />
```

This two-way binds: DOM input updates `store.profile.full_name`, and mutations to `store.profile.full_name` update the DOM input. No intermediate `$derived` needed.

Source: `bind.md` — "Basic input value binding"; `bind.md` — "Bind to Component Prop with bind:property".

---

### 9. Child `$bindable()` count prop + parent `bind:count`, with `$effect` writeback

**Status: VALIDATED canonical idiom.** Full research notes in
`workbench/2-plan/research/SVELTE5_BINDABLE_NOTES_2026-05-13_restyle-profile-editor.md`.

Child:

```svelte
<script>
  let { count = $bindable(0) } = $props();
  let items = $state([]);
  $effect(() => { count = items.length; });
</script>
```

Parent:

```svelte
<script>
  let workExperienceCount = $state(0);
</script>
<WorkExperience bind:count={workExperienceCount} />
```

Three load-bearing facts from the bindable notes:

- `$bindable()` is the documented authorisation for child-to-parent mutation
  (without it the child write triggers `ownership_invalid_mutation`).
- `untrack()` is NOT required here. The effect reads `items` (its only
  tracked dependency) and writes `count` — two distinct reactive values,
  no self-dependency loop.
- Hard rule: never read AND write the same variable inside one `$effect`.
  `count = count + items.length` triggers `effect_update_depth_exceeded`
  and crashes loudly. The plan's shape `count = items.length` (write-only
  on `count`) is safe.

**Disqualified alternatives** (from the same notes):

- `bind:this` gives imperative access only; reading `ref.count` is not
  reactive — not a valid path for parent-side derived integers.
- `export const foo = ...` + `<Component bind:foo />` is disallowed in
  runes mode (hard error).

Source: `documentation/docs/02-runes/04-$effect.md`, `06-$bindable.md`,
`packages/svelte/messages/client-errors/errors.md`.

---

## Deprecated to avoid

- `<slot>` / slot-based content passing — deprecated in Svelte 5, superseded by snippets.
- Svelte 4 `writable` / `readable` stores — still work but the runes approach (`$state` in `.svelte.js`) is the preferred replacement per the docs.
- `export const foo = ...` + parent `bind:foo` — disallowed in runes mode (hard error).
- Mutating a parent-passed reactive prop without `$bindable()` — triggers `ownership_invalid_mutation`.
- Reading AND writing the same state inside one `$effect` — triggers `effect_update_depth_exceeded`.

---

## Open questions

1. **Testing module-scoped runes via Playwright `page.evaluate`** — Context7 has no Svelte-specific guidance. The answer depends on whether functions are exposed on `window`. Fall back to first-party Svelte testing docs or Vitest + `@testing-library/svelte` for unit-level testing of `parseInitials`.
