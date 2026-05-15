# IMPL_PLAN — restyle-profile-editor

Date: 2026-05-13
Ceremony: M
Source spec: `workbench/1-analyze/spec/FEATURE_SPEC_2026-05-13_restyle-profile-editor.md`
Source UX: `workbench/1-analyze/ux/UX_DESIGN_2026-05-13_restyle-profile-editor.md`
Library notes: `workbench/2-plan/research/SVELTE5_NOTES_2026-05-13_restyle-profile-editor.md`

## Architecture summary

Three structural changes drive everything:

1. A new module-scoped Svelte 5 runes store (`src/lib/profileStore.svelte.js`)
   becomes the single source of truth for the `User` entity. `UserProfile.svelte`
   stops owning its `data` state; `Topbar.svelte` reads `store.initials()`;
   a new Summary section in `ProfileEditor.svelte` writes to the same store.

2. A new presentational component (`src/components/EditorialSection.svelte`)
   renders the numbered editorial section header (`№ NN` eyebrow + `.display`
   title + optional count). Used seven times by `ProfileEditor.svelte`.

3. Seven existing components (`ProfileEditor`, `UserProfile`, `WorkExperience`,
   `Education`, `Skills`, `Languages`, `Projects`) and one legacy file
   (`Section.svelte`) get restyled. `Section.svelte` is deleted (verified
   sole consumer is `ProfileEditor.svelte:2`).

Total: 2 new files, 8 modified files, 1 deleted file, 1 modified test file,
1 new test file.

---

## Files to CREATE

### File 1 — `src/lib/profileStore.svelte.js`

**Purpose:** Module-scoped runes singleton owning the `User` entity, plus
the pure `parseInitials()` helper.

**Scope statement (header line 2):** `Shared profile state — load, save,
initials helper.`

**Exports:**

```js
// Lean Code — BSD 3-Clause License — Vivian Voss, 2026
// Scope: Shared profile state — load, save, initials helper.

import { getUser, updateUser } from './api.js';

export const store = $state({
  profile: {
    full_name: '',
    email: '',
    phone: '',
    location: '',
    linkedin_url: '',
    summary: '',
    photo: null,
  },
  loaded: false,
  saving: false,
  saved: false,
  error: null,
});

let _pending = null;
let _savedTimeout = null;

export function parseInitials(fullName) {
  const tokens = (fullName ?? '').trim().split(/\s+/).filter(Boolean);
  if (tokens.length === 0) return '??';
  if (tokens.length === 1) return tokens[0][0].toUpperCase();
  return (tokens[0][0] + tokens[tokens.length - 1][0]).toUpperCase();
}

export function readInitials() {
  return parseInitials(store.profile.full_name);
}

export async function readProfile() {
  if (store.loaded) return;
  if (_pending) return _pending;

  _pending = (async () => {
    try {
      const result = await getUser();
      if (result) Object.assign(store.profile, result);
      store.loaded = true;
      store.error = null;
    } catch (e) {
      store.error = 'Could not load profile. Please refresh.';
    } finally {
      _pending = null;
    }
  })();

  return _pending;
}

export async function writeProfile() {
  try {
    store.saving = true;
    await updateUser(store.profile);
    store.saved = true;
    if (_savedTimeout) clearTimeout(_savedTimeout);
    _savedTimeout = setTimeout(() => { store.saved = false; }, 2000);
  } catch (e) {
    store.error = 'Could not save. Please try again.';
  } finally {
    store.saving = false;
  }
}
```

**Notes:**

- Verb-prefix audit (per CLAUDE.md lean-code nine-verb table): the store
  uses `readProfile()` (not `load`), `writeProfile()` (not `save`), and
  `parseInitials(fullName)` (not `derive`). `load`, `save`, and `derive`
  are not on the permitted verb list; `read`, `write`, and `parse` are.
- `parseInitials` takes a full-name string and returns the 2-char initial
  format — pure, no DOM access, no store access.
- `_pending` and `_savedTimeout` are plain module-private lets; not
  reactive. Per SVELTE5_NOTES pattern 4.
- `Object.assign(store.profile, result)` mutates the proxy — reactive per
  SVELTE5_NOTES pattern 5.

### File 2 — `src/components/EditorialSection.svelte`

**Purpose:** Reusable numbered-section header primitive. Used 7× in
`ProfileEditor.svelte`; intended for reuse in slices 4–9.

**Scope statement:** `Numbered editorial section header — eyebrow,
display title, optional count.`

**Markup:**

```svelte
<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->
<!-- Scope: Numbered editorial section header — eyebrow, display title, optional count. -->

<script>
  let { number, title, count = null, children } = $props();
</script>

<section class="editorial-section">
  <div class="editorial-section-header">
    <span class="eyebrow num">№ {number}</span>
    <h2 class="display editorial-section-title">{title}</h2>
    {#if count != null}
      <span class="num editorial-section-count">{count}</span>
    {/if}
  </div>
  <div class="editorial-section-body">
    {@render children()}
  </div>
</section>

<style>
  .editorial-section {
    display: flex;
    flex-direction: column;
    gap: 14px;
  }
  .editorial-section-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
  }
  .editorial-section-title {
    font-size: 26px;
    margin: 0;
  }
  .editorial-section-count {
    font-size: 12px;
    color: var(--ink-3);
  }
</style>
```

**Notes:**

- The eyebrow is a `<span>` sibling of `<h2>` (not a child), so the
  document outline reads seven clean `<h2>`s. Per FEATURE_SPEC Must-have 2
  and UX_DESIGN A11y note.
- `count = null` default; renders only when caller passes a number.
- No inline comments per lean-code rules.

---

## Files to MODIFY

### File 3 — `src/components/Topbar.svelte`

**Touch points:** lines 4-17 (script), 51 (user circle text).

**Changes:**

1. Import the store and helpers:

   ```js
   import { store, readInitials, readProfile } from '../lib/profileStore.svelte.js';
   ```

2. Add a mount `$effect` that calls `readProfile()`:

   ```js
   $effect(() => {
     void readProfile();
   });
   ```

3. Replace the hard-coded `LM` with the reactive helper:

   ```svelte
   <div class="topbar-user" aria-hidden="true">{readInitials()}</div>
   ```

   Note: `readInitials()` is called on every render, but it's a 3-line
   pure function over `store.profile.full_name`; Svelte tracks the
   property access during render so the circle re-renders when
   `full_name` mutates. No `$derived` needed — but if the inspector
   wants tighter idiom, wrap in a `$derived`:

   ```js
   const initials = $derived(readInitials());
   ```

   **Decision:** use the `$derived` form. It's more idiomatic and
   communicates intent.

**Preserved verbatim:** all `topbar-nav` styling, slot logic, search pill,
font-family, geometry of the user circle.

### File 4 — `src/components/UserProfile.svelte`

**Touch points:** lines 1-77 (entire script), 79-170 (template), 172-189
(styles).

**Changes:**

1. Replace the local `data`, `loading`, `saving`, `saved`, `error`,
   `fieldErrors`, `saveTimeout`, `savedTimeout` state with imports from
   the store + a small remaining local `fieldErrors`:

   ```js
   import { store, readProfile, writeProfile } from '../lib/profileStore.svelte.js';
   import PhotoUpload from './PhotoUpload.svelte';

   let fieldErrors = $state({});
   let saveTimeout = null;

   $effect(() => {
     void readProfile();
     return () => { if (saveTimeout) clearTimeout(saveTimeout); };
   });
   ```

2. The blur-debounce handler stays local but mutates the store:

   ```js
   function handleBlur() {
     if (!store.profile.full_name || !store.profile.email) return;
     if (saveTimeout) clearTimeout(saveTimeout);
     saveTimeout = setTimeout(checkAndWrite, 500);
   }

   function checkAndWrite() {
     fieldErrors = {};
     if (!store.profile.full_name.trim()) fieldErrors.full_name = 'Required';
     if (!store.profile.email.trim()) fieldErrors.email = 'Required';
     else if (!/^[^@]+@[^@]+\.[^@]+$/.test(store.profile.email))
       fieldErrors.email = 'Invalid email address';
     if (Object.keys(fieldErrors).length > 0) return;
     void writeProfile();
   }
   ```

   Renamed `save()` → `checkAndWrite()` to satisfy lean-code one-verb
   rule. Verb-prefix `check` is permitted; the second word `Write` is the
   permitted save verb.

3. Replace the entire template (loading skeleton + form layout) with the
   Identity card layout. Render conditions bind to `store.loaded` and
   `store.error`:

   ```svelte
   {#if !store.loaded && !store.error}
     <div class="form">
       <div class="skeleton" style="width: 100%; height: 40px;"></div>
       <div class="skeleton" style="width: 100%; height: 40px;"></div>
       <div class="skeleton" style="width: 100%; height: 40px;"></div>
     </div>
   {:else if store.error}
     <div class="form-error">{store.error}</div>
   {:else}
     <div class="identity-card">
       <div class="identity-avatar">
         <PhotoUpload bind:photo={store.profile.photo} />
       </div>
       <div class="identity-grid">
         <!-- 5 fields: full_name, email, phone, location, linkedin_url -->
         <div class="form-row">
           <label for="full_name" class="eyebrow required">Full name</label>
           <input id="full_name" class="input" type="text"
                  bind:value={store.profile.full_name}
                  onblur={handleBlur}
                  class:error={fieldErrors.full_name}
                  aria-required="true" />
           {#if fieldErrors.full_name}
             <span class="error-message">{fieldErrors.full_name}</span>
           {/if}
         </div>
         <!-- ... email, phone, location, linkedin_url same shape ... -->
       </div>
     </div>
     {#if store.saved}
       <span class="saved-indicator" class:fading={!store.saving}>Saved</span>
     {/if}
   {/if}
   ```

   **Five form rows total**, in source order: Full name, Email, Phone,
   Location, LinkedIn. The Summary textarea is REMOVED from this
   component (moved to ProfileEditor; see File 6).

4. New scoped styles:

   ```css
   .identity-card {
     display: flex;
     gap: 24px;
     align-items: flex-start;
   }
   .identity-avatar {
     width: 96px;
     height: 96px;
     border-radius: 50%;
     overflow: hidden;
     background: var(--ink);
     color: var(--paper);
     flex-shrink: 0;
     display: grid;
     place-items: center;
   }
   .identity-grid {
     flex: 1;
     display: grid;
     grid-template-columns: 1fr 1fr;
     gap: 12px;
   }
   ```

5. Header file: add the two-line lean-code header (verified absent in
   current file).

**Preserved verbatim:** field IDs, validation regex, validation copy
("Invalid email address", "Required"), 500ms debounce.

### File 5 — `src/components/PhotoUpload.svelte`

**Touch points:** none structural — only a `bind:photo` consumer change
in File 4. Verify the `bind:photo` prop signature still works after
moving the bound value from a local `$state` to a store property.

**Risk:** `bind:photo={store.profile.photo}` MAY trigger Svelte 5 strict
mode warning about binding to a prop of an imported reactive object.
Per SVELTE5_NOTES pattern 8: `bind:value` against `store.profile.x`
works. Same should hold for any `bind:photo` against a property — but
this is `bind:` against a *custom prop* on a child component, not a
DOM input. Custom-prop bindings in Svelte 5 require the child to
declare the prop with `$bindable()`. Need to read PhotoUpload's
current `$props()` declaration before edit.

**Plan-phase verification:** read `src/components/PhotoUpload.svelte`
and confirm whether `photo` is currently declared as `$bindable()`. If
yes, no change needed. If not, the parent (File 4) cannot use `bind:`
and must use a callback pattern instead.

### File 6 — `src/components/ProfileEditor.svelte`

**Touch points:** entire file (currently 78 lines). Largest single rewrite.

**Changes:**

1. Add lean-code header (currently missing).

2. Import the new components:

   ```js
   import EditorialSection from './EditorialSection.svelte';
   import UserProfile from './UserProfile.svelte';
   import WorkExperience from './WorkExperience.svelte';
   import Education from './Education.svelte';
   import Skills from './Skills.svelte';
   import Projects from './Projects.svelte';
   import Languages from './Languages.svelte';
   import ImportModal from './ImportModal.svelte';
   import Toast from './Toast.svelte';
   import { store, writeProfile } from '../lib/profileStore.svelte.js';
   ```

   `Section` import dropped.

3. Replace the template:

   ```svelte
   <Toast bind:message={toastMessage} type="success" />
   <ImportModal bind:open={importModalOpen} onSuccess={handleImportSuccess} onClose={handleImportClose} />

   <main class="editor-main">
     <div class="editor-column">
       <header class="editor-header">
         <div>
           <div class="eyebrow">Workspace · profile</div>
           <h1 class="display editor-title">Your <span class="serif-italic">source of truth</span>.</h1>
           <p class="editor-sub">The single profile every tailored CV draws from. Edit once, ship anywhere.</p>
         </div>
         <div class="profile-header">
           <button class="btn" onclick={() => importModalOpen = true} bind:this={importButtonRef}>
             Import JSON
           </button>
         </div>
       </header>

       <div class="editor-sections">
         <EditorialSection number="01" title="Identity">
           <UserProfile />
         </EditorialSection>

         <EditorialSection number="02" title="Summary">
           <div class="form-row">
             <label for="summary" class="eyebrow">Summary</label>
             <textarea id="summary" class="textarea"
                       bind:value={store.profile.summary}
                       onblur={handleSummaryBlur}></textarea>
           </div>
         </EditorialSection>

         <EditorialSection number="03" title="Experience" count={workExperienceCount}>
           <WorkExperience bind:this={workExperienceRef} bind:count={workExperienceCount} />
         </EditorialSection>

         <!-- ... Education 04, Skills 05, Languages 06, Projects 07 same pattern ... -->
       </div>
     </div>
   </main>
   ```

   - `.profile-header` class preserved on the action wrapper (covers
     existing playwright tests).
   - Each child component (`WorkExperience`, `Education`, `Skills`,
     `Languages`, `Projects`) now exposes a `count` `$bindable()` prop
     that ProfileEditor binds to and passes into `EditorialSection`.

4. Summary blur handler:

   ```js
   let summaryTimeout = null;
   function handleSummaryBlur() {
     if (summaryTimeout) clearTimeout(summaryTimeout);
     summaryTimeout = setTimeout(() => { void writeProfile(); }, 500);
   }
   ```

5. State setup:

   ```js
   let workExperienceRef = $state(null);
   let educationRef = $state(null);
   let skillsRef = $state(null);
   let languagesRef = $state(null);
   let projectsRef = $state(null);
   let importModalOpen = $state(false);
   let importButtonRef = $state(null);
   let toastMessage = $state(null);
   let workExperienceCount = $state(0);
   let educationCount = $state(0);
   let skillsCount = $state(0);
   let languagesCount = $state(0);
   let projectsCount = $state(0);
   ```

6. Scoped styles:

   ```css
   .editor-main {
     padding: var(--d-pad) 0;
     background: var(--paper);
   }
   .editor-column {
     max-width: 940px;
     margin: 0 auto;
     padding: 0 36px;
   }
   .editor-header {
     display: flex;
     align-items: flex-end;
     justify-content: space-between;
     margin-bottom: 28px;
   }
   .editor-title {
     font-size: 44px;
     margin: 0;
   }
   .editor-sub {
     margin-top: 8px;
     color: var(--ink-3);
     font-size: 13px;
     max-width: 520px;
   }
   .editor-sections {
     display: flex;
     flex-direction: column;
     gap: 36px;
   }
   ```

   The existing `.profile-header` rule (margin-bottom) is dropped since
   the action button now sits in the right column of the editor-header.

7. **App.svelte caveat.** `App.svelte:26` currently wraps the editor in
   `<div class="container">`. That container's `max-width: 800px` and
   centred padding (from `global.css:175-179`) would constrain the new
   editor's 940px column. **Resolution:** the new ProfileEditor opens
   with its own `<main class="editor-main">` and the 940px column lives
   inside it. The outer `.container` from `App.svelte` either needs to
   be removed for the profile screen, OR ProfileEditor's `.editor-main`
   uses `margin-left: calc(50% - 50vw)` etc. to break out.

   **Decision:** modify `App.svelte` to drop `.container` around the
   editor (the editor now self-frames). Simpler. See File 11.

### File 7 — `src/components/WorkExperience.svelte`

**Touch points:** lines 150-432 (full rendered output). Two distinct
markup blocks must both be restyled:

- **Primary `{#each}` block** (~lines 165-307) — the existing-experiences
  list shown in steady state.
- **Inline `{#if showForm && !editingId}` block** (~lines 309-428) — the "Add new"
  form rendered when the user clicks the add-experience action.

Both blocks contain `<input>` and `<textarea>` elements that today
inherit legacy form styling. The restyle must apply `.input` /
`.textarea` classes (per slice 1 primitives) to both blocks, not just
the primary list. The `#e0e0e0` border at line 310 sits inside the
inline form block, not the primary block.

No `<style>` block exists in this file today — purely inherited.

**Changes:**

1. Add lean-code header.

2. Expose count to parent:

   ```js
   let { count = $bindable(0) } = $props();
   $effect(() => { count = items.length; });
   ```

3. Replace the row markup:

   ```svelte
   {:else}
     <div class="exp-list">
       {#each items as item, i}
         {#if editingId === item.id && showForm}
           <!-- inline edit form, restyled but structurally same -->
         {:else}
           <div class="exp-row" class:not-first={i > 0}>
             <div class="exp-dates num">
               <div>{formatDate(item.start_date)}</div>
               <div class="exp-dash">—</div>
               <div>{item.is_current ? 'Present' : formatDate(item.end_date)}</div>
             </div>
             <div class="exp-body">
               <div class="exp-title">
                 {item.title} <span class="exp-company">· {item.company}</span>
               </div>
               {#if item.location}
                 <div class="exp-location">{item.location}</div>
               {/if}
               {#if item.description}
                 <div class="exp-desc">{item.description}</div>
               {/if}
             </div>
             <button class="btn btn-ghost exp-edit" onclick={() => edit(item)}>Edit</button>
           </div>
         {/if}
       {/each}
     </div>
   {/if}

   <button class="btn exp-add" onclick={() => add()}>
     <span aria-hidden="true">+</span> Add experience
   </button>
   ```

4. Add scoped styles:

   ```css
   .exp-list { display: flex; flex-direction: column; }
   .exp-row {
     display: grid;
     grid-template-columns: 110px 1fr auto;
     gap: 18px;
     padding: 16px 0;
   }
   .exp-row.not-first { border-top: 1px solid var(--rule-soft); }
   .exp-dates { font-size: 11px; color: var(--ink-3); }
   .exp-dash { color: var(--ink-4); }
   .exp-title { font-size: 14px; font-weight: 600; }
   .exp-company { color: var(--ink-3); font-weight: 400; }
   .exp-location { font-size: 12px; color: var(--ink-3); margin-top: 2px; }
   .exp-desc {
     font-size: 13px; color: var(--ink-2);
     margin-top: 8px; line-height: 1.55;
     white-space: pre-wrap;
   }
   .exp-edit { padding: 4px 8px; font-size: 11px; }
   .exp-add { margin-top: 12px; font-size: 12px; }
   ```

5. The inline edit form's `<input>`, `<textarea>`, `<select>` get the
   `.input` / `.textarea` class added. Legacy `#e0e0e0` border in line
   310 is replaced with `var(--rule-soft)`.

6. The existing `formatDate()` helper at line 142 is reused verbatim.

**Preserved verbatim:** field IDs, validation logic, error messages,
all api calls, edit/delete flows, confirm-dialog, current-position
checkbox.

### File 8 — `src/components/Education.svelte`

**Touch points:** rendered output (lines 142-247), one inline `#e0e0e0`
at line 251.

**Changes mirror File 7** but with the Education row pattern (3-col grid
`70px 1fr auto`, gap 18px, padding `12px 0`, year-prefixed):

```svelte
<div class="edu-row" class:not-first={i > 0}>
  <div class="edu-year num">{item.graduation_year || ''}</div>
  <div>
    <div class="edu-title">
      {item.degree}{item.field_of_study ? ` ${item.field_of_study}` : ''}
    </div>
    <div class="edu-institution">{item.institution}</div>
  </div>
  <button class="btn btn-ghost" onclick={() => edit(item)}>Edit</button>
</div>
```

Add count `$bindable()`. Replace `#e0e0e0` with `var(--rule-soft)`. Add
lean-code header.

### File 9 — `src/components/Skills.svelte`

**Touch points:** entire template (lines 77-129) + entire `<style>` block
(lines 131-167).

**Changes:**

1. Add lean-code header.

2. Expose count:

   ```js
   let { count = $bindable(0) } = $props();
   $effect(() => { count = items.length; });
   ```

3. Replace the template:

   ```svelte
   {#if !loading && !error}
     <div class="skill-cluster">
       {#each items as item}
         <span class="pill skill-pill">
           {item.name}
           <button class="skill-remove" onclick={() => requestDelete(item.id)}
                   aria-label="Remove {item.name}">×</button>
         </span>
       {/each}
       <button class="pill skill-pill-add" onclick={focusInput}>+ add</button>
     </div>

     <div class="skill-input-row">
       <input id="skill-input" class="input" type="text"
              placeholder="Python, FastAPI, SQL"
              bind:value={inputValue}
              onkeydown={handleKeydown}
              disabled={saving} />
       <button class="btn btn-primary" onclick={addSkills}
               disabled={saving || !inputValue.trim()}>
         {saving ? 'Adding...' : 'Add'}
       </button>
     </div>

     {#if saved}
       <span class="saved-indicator" class:fading={!saving}>Saved</span>
     {/if}
   {/if}
   ```

   The legacy `<div class="empty-state">No skills added yet.</div>` is
   gone. The dashed pill is the empty-state affordance.

4. Add `focusInput()`:

   ```js
   function focusInput() {
     document.getElementById('skill-input')?.focus();
   }
   ```

   `add()` function (the existing `export function add()`) is preserved
   for ProfileEditor's old API contract; it now just calls
   `focusInput()`. **Or** drop it — `ProfileEditor.svelte` no longer
   wraps Skills in a `<Section onAdd={…}>`. Drop the `add()` export.

5. New scoped styles:

   ```css
   .skill-cluster {
     display: flex;
     flex-wrap: wrap;
     gap: 6px;
   }
   .skill-pill {
     padding: 5px 10px;
     font-size: 12px;
     background: var(--paper-2);
     border: 1px solid var(--rule-soft);
     border-radius: var(--r-sm);
     color: var(--ink);
     text-transform: none;
     letter-spacing: 0;
     font-family: var(--font-ui);
   }
   .skill-pill-add {
     background: transparent;
     border: 1px dashed var(--rule);
     color: var(--ink-3);
     cursor: pointer;
   }
   .skill-remove {
     padding: 0;
     margin-left: 4px;
     font-size: 14px;
     line-height: 1;
     color: var(--ink-3);
     background: none;
     border: none;
     cursor: pointer;
   }
   .skill-remove:hover { color: var(--negative); }
   .skill-input-row {
     display: flex;
     gap: 8px;
     margin-top: 16px;
   }
   ```

   The `.pill` primitive from `global.css:283-296` is mono+uppercase by
   default — Skills overrides `font-family`, `text-transform`, and
   `letter-spacing` back to body text, because the design shows
   sentence-case 12px Inter skill labels, not 10px mono uppercase.

   **NOTE:** this overrides the editorial `.pill` primitive's
   typographic register. Document in the inspector checklist for
   designer sign-off.

6. Eliminate legacy color references: drop the `rgb(var(--color-primary-rgb) / 0.1)`
   background, `rgb(var(--color-primary-rgb) / 0.3)` border, and
   `rgb(var(--color-text-rgb) / 0.6)` color from `.tag-remove`.

### File 10 — `src/components/Languages.svelte`

**Touch points:** rendered output (lines 175-258), one `#e0e0e0` at line
261, scoped style block (lines 315-341).

**Changes:**

1. Add lean-code header.
2. Add count `$bindable()`.
3. Replace the `item-list` with a 2-column grid:

   ```svelte
   <div class="lang-grid">
     {#each items as item, index}
       <div class="lang-card"
            class:dragging={draggedIndex === index}
            draggable="true"
            ondragstart={(e) => handleDragStart(e, index)}
            ondragover={(e) => handleDragOver(e, index)}
            ondrop={handleDrop}
            ondragend={handleDragEnd}>
         <div class="lang-label">
           <div class="lang-name">{item.name}</div>
           <div class="lang-level">{cefrLabel(item.level)}</div>
         </div>
         <span class="num lang-code">{item.level}</span>
         <button class="btn btn-ghost lang-edit" onclick={() => edit(item)}>Edit</button>
       </div>
     {/each}
   </div>
   ```

   `cefrLabel(level)` — helper to translate `"B2"` → `"B2 (Upper Intermediate)"`
   using the existing `CEFR_LEVELS` array. Add this helper above the
   template; verb `parse` per lean-code? No — `parse` is for format
   transforms. This is a lookup. Use **`readCefrLabel(level)`**.

4. Drop the legacy drag-handle visual; instead, the entire `.lang-card`
   is draggable (HTML5 `draggable="true"`). The cursor changes to grab.

5. Add scoped styles:

   ```css
   .lang-grid {
     display: grid;
     grid-template-columns: 1fr 1fr;
     gap: 8px;
   }
   .lang-card {
     display: grid;
     grid-template-columns: 1fr auto auto;
     align-items: baseline;
     gap: 8px;
     padding: 10px 14px;
     background: var(--paper-2);
     border: 1px solid var(--rule-soft);
     border-radius: var(--r-sm);
     cursor: grab;
   }
   .lang-card.dragging { opacity: 0.5; }
   .lang-name { font-size: 13px; font-weight: 500; }
   .lang-level { font-size: 11px; color: var(--ink-3); margin-top: 1px; }
   .lang-code { font-size: 11px; color: var(--ink-3); }
   .lang-edit { padding: 4px 8px; font-size: 11px; }
   ```

6. Replace `#e0e0e0` with `var(--rule-soft)` in the add-form border-top.

### File 11 — `src/components/Projects.svelte`

**Touch points:** rendered output (lines 138-217), one `#e0e0e0` at line
220.

**Changes mirror File 8** but with the Projects row pattern (2-col grid
`1fr auto`, name + technologies/url subtitle + description):

```svelte
<div class="proj-row" class:not-first={i > 0}>
  <div>
    <div class="proj-name">{item.name}</div>
    {#if item.technologies || item.url}
      <div class="proj-sub">
        {#if item.technologies}{item.technologies}{/if}
        {#if item.url}
          {#if item.technologies} · {/if}
          <a href={item.url} target="_blank" rel="noopener">{item.url}</a>
        {/if}
      </div>
    {/if}
    {#if item.description}
      <div class="proj-desc">{item.description}</div>
    {/if}
  </div>
  <button class="btn btn-ghost" onclick={() => edit(item)}>Edit</button>
</div>
```

Add count `$bindable()`. Drop `#e0e0e0`. Add lean-code header.

### File 12 — `src/App.svelte`

**Touch points:** lines 25-32.

**Changes:**

Drop the `.container` wrapper around ProfileEditor — the new editor
self-frames with its own `<main class="editor-main">` 940px column.
Keep the container around the Resume Generator (out of scope here).

```svelte
<Topbar {activeTab} onTabChange={updateActiveTab} />

{#if activeTab === 'profile'}
  <ProfileEditor />
{:else if activeTab === 'resume'}
  <div class="container">
    <ResumeGenerator />
  </div>
{/if}
```

**Note:** existing tests use `.container` only in selectors like
`document.querySelector('.container')` (verified via grep — see
`tests/test_topbar_shell.py:91`). Confirm: that test checks
`topbar.compareDocumentPosition(container) & Node.DOCUMENT_POSITION_FOLLOWING`
— it requires *some* `.container` element to exist. After the change,
`.container` only renders when `activeTab === 'resume'`, not when
`'profile'`. **The test fails.** Resolution: keep an outer `.container`
wrapper around `{#if}` AND the editor self-frames inside it; OR update
the test. Simplest: change the test to check that Topbar is the first
direct child of `<body>` (it should be).

**Plan-phase decision:** keep App.svelte simpler — just change the test
file (File 14) to drop the `.container` co-positioning check (replace
with a "Topbar is first child of body" check that's robust to either
container or no container).

Wait — actually, re-reading `test_topbar_shell.py:81-107`:
- `test_topbar_renders_at_top` checks `topbar.compareDocumentPosition(container)`. If `.container` doesn't exist, `container` is null and the boolean short-circuits to `false`.
- The test ALSO checks `topbar_parent_tag == "BODY"` and `wordmark_present`.

The cleanest fix: keep `.container` wrapping the editor for legacy
reasons, but override its `max-width` for the profile screen. Two-line
add to `App.svelte`:

```svelte
<div class={activeTab === 'profile' ? 'container container-wide' : 'container'}>
```

And `global.css` gets a new `.container-wide` rule that overrides
`max-width` to `unset` so the inner editor's 940px column dominates.

**Adopted plan:** add `.container-wide` (no max-width, no padding) and
apply it conditionally. ProfileEditor still owns its 940px column inside.

```svelte
<Topbar {activeTab} onTabChange={updateActiveTab} />

<div class="container" class:container-wide={activeTab === 'profile'}>
  {#if activeTab === 'profile'}
    <ProfileEditor />
  {:else if activeTab === 'resume'}
    <ResumeGenerator />
  {/if}
</div>
```

Add to `src/styles/global.css`:

```css
.container-wide {
  max-width: none;
  padding: 0;
}
```

Net effect: `.container` element still exists (legacy tests pass), but
its constraints are nullified on the profile screen.

### File 13 — `src/styles/global.css`

**Touch points:** add `.container-wide` rule (see File 12).

That's the only change. The editorial primitives (`.eyebrow`, `.display`,
`.serif-italic`, `.input`, `.textarea`, `.btn`, `.btn-primary`,
`.btn-ghost`, `.pill`, `.num`, `.card`) are already there from slice 1.

---

## Files to DELETE

### File X — `src/components/Section.svelte`

Verified single consumer: `ProfileEditor.svelte:2`. After File 6's
rewrite, that import is gone. Delete the file.

**Sanity check before deletion (build phase):**

```bash
grep -rn "from.*Section\.svelte\|import Section" src/ tests/
```

Expected: zero matches after File 6 lands. If there are unexpected
consumers, leave `Section.svelte` and just stop importing it.

---

## Tests

### Modify — `tests/test_topbar_shell.py`

**Single case to update:** `test_user_initials_circle` (line 334).

**Replacement assertion logic:**

The test currently asserts `user["text"] == "LM"`. After wiring, the
text equals `parseInitials(profile.full_name)`. Since the editor calls
`getUser()` on mount and the test stack does not run a FastAPI backend,
the test mocks the `/api/users` GET at the Playwright route layer. The
store's production code stays pure — no `localStorage` branch, no
test-only short-circuit baked into the shipped bundle.

**Helper added** to the same test file (duplicate the 8-line helper into
`test_profile_editor_restyle.py` and `test_topbar_shell.py`; extract to
`tests/conftest.py` only if a third test file needs it):

```python
import json

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
```

**Updated test:**

```python
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
```

**Why the visual-style assertions are preserved (MN-E fix):** the
original `test_user_initials_circle` asserted geometry (`width`,
`height`, `borderRadius`), brand colours (`background`, `color`), and
typography (`fontFamily`, `fontStyle`) in addition to text content.
Dropping those would silently lose coverage for the topbar circle's
visual contract. The new version preserves all eight assertions; only
the text expectation changes (`LM` → `IM`) and a `wait_for_function`
gates on the initials having resolved post-fetch.

**Why route-interception (not a production hook, not localStorage, not a
live backend):**

- `page.route` intercepts at the network layer; `getUser()` runs its
  normal `fetch` call and receives a synthetic response. The store's
  coalescing logic (`_pending`, `store.loaded`) is exercised exactly as
  in production.
- Each test installs its own route on its own `page`; the route tears
  down with the browser context. No cross-test state, no production
  leakage.
- The store's `readProfile()` stays a single-job function (per
  CLAUDE.md lean-code): "Load from the API and populate the store." No
  test-mode branch, no `localStorage` read, nothing user-spoofable from
  DevTools.

Earlier drafts of this plan considered a `localStorage` short-circuit
inside `readProfile()` (a `mycv:test_full_name` key read on every
production load). **Rejected** during M5 review — leaked a test code
path into the production bundle, made the Topbar's apparent profile
user-spoofable via DevTools console, and silently invalidated the M4
coalescing test (the hook would short-circuit before `getUser()` and
the test would trivially pass with 0 GETs).

### Add — `tests/test_profile_editor_restyle.py`

New Playwright suite covering Scenarios 1, 2b, 3b, 5 (re-verified post-restyle),
8, 10, 11, 12 from the FEATURE_SPEC.

**Structure** (one test per scenario, shared `public_url` fixture from
the existing `test_topbar_shell.py` pattern — copy the fixture or
extract to `conftest.py`):

```python
# Lean Code — BSD 3-Clause License — Vivian Voss, 2026
# Scope: Editorial restyle smoke tests for the profile editor.

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


def test_editorial_page_frame(public_url): ...   # Scenario 1
def test_identity_grid_shape(public_url): ...   # Scenario 2b
def test_skills_zero_state(public_url): ...     # Scenario 3b
def test_legacy_color_tokens_absent(public_url): ...  # Scenario 8 — done via grep, no Playwright needed; could be a separate non-Playwright test
def test_initials_helper_edge_cases(public_url): ...  # Scenario 7b — DOM-based
def test_readprofile_coalesces_one_request(public_url): ...  # M4 regression guard — store double-load coalescing
```

**`test_readprofile_coalesces_one_request` — guards the store coalescing
invariant.** Both `Topbar.svelte` and `UserProfile.svelte` call
`readProfile()` from `$effect` on mount; the store's `_pending` IIFE must
ensure `getUser()` runs only once. Without this test, a future refactor
that inserts an `await` between the `_pending = null` reset and the
`if (_pending)` guard would silently double the `/api/users` GET on every
page load and ship undetected.

```python
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
```

Note: this test uses its own inline route handler (not the shared
`create_users_mock`) because it needs to count calls. Both approaches
intercept at the same Playwright network layer; the coalescing path
under test is identical.

**Scenarios deferred to manual inspection:** 4 (drag), 5 (Experience
shape — covered by `test_work_experiences.py` for behaviour + manual
visual), 6 (initials update after save — depends on backend), 9
(existing tests pass — meta-scenario), 10/11/12 (full save + reload
round-trips depend on backend).

### Manual inspection bullets (for Phase 3 `inspector` agent)

Each bullet is one assertion the human reviewer ticks Pass / Fail. The
`inspector` agent surfaces these via `AskUserQuestion`.

- **MI-4 (Scenario 4 — Languages drag preserved).** In the Languages
  section, drag the second row to the first slot using the row's drag
  handle. Drop it. Expected: rows swap visually; the saved order
  persists after a page reload. Fail if rows don't swap, swap reverts
  on hover-out, or order is not persisted.
- **MI-5 (Scenario 5 — Experience timeline shape).** Open Experience
  with at least one entry. Expected: each row renders as a date-rail
  on the left (year + dash separator) + title/company/description
  block on the right; chronological order most-recent first. Fail if
  rail and content visually overlap, dates render mid-row, or order is
  reversed.
- **MI-6 (Scenario 6 — Topbar initials update on Identity save).** In
  the Identity card, change Full name from `Issa Maro` to `Ada Lovelace`
  and blur the field. Expected: after the 500ms debounce, the Topbar
  user circle text changes from `IM` to `AL` without a page reload.
  Fail if the circle stays `IM` until reload, or shows stale initials
  longer than ~1s after blur.
- **MI-10 (Scenario 10 — Summary round-trip).** Type a non-empty
  summary, blur, hard-reload the page. Expected: the summary content
  reappears in the textarea verbatim. Fail if the textarea is empty,
  truncated, or shows a previous value.
- **MI-11 (Scenario 11 — Education edit round-trip).** Open an existing
  education entry, change the institution, save, reload. Expected: the
  new institution renders in the list. Fail if the old value persists.
- **MI-12 (Scenario 12 — Project edit round-trip).** Same as MI-11 for
  Projects: edit a project name, save, reload. Expected: new name
  persists.

MI-6, MI-10, MI-11, MI-12 require the FastAPI dev server (`uvicorn`)
running; otherwise the inspector should record `Skip` and note "backend
not running".

**For Scenario 8 — legacy tokens absent:** make it a pure pytest test
(no Playwright):

```python
def test_no_legacy_color_tokens_in_components():
    import re
    forbidden = re.compile(r'--color-border|--color-primary-rgb|--color-text-rgb|#e0e0e0')
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
        content = Path(f).read_text()
        matches = forbidden.findall(content)
        assert matches == [], f"{f} contains legacy color tokens: {matches}"
```

Place in `tests/test_profile_editor_restyle.py` as a non-Playwright test
function (no fixtures needed).

---

## Library patterns to use (cite SVELTE5_NOTES)

- Pattern 1: `export const store = $state({...})` form — used in File 1.
- Pattern 2: cross-component reactivity — Topbar (File 3), UserProfile
  (File 4), ProfileEditor (File 6) all read/write the same store, no
  pub-sub.
- Pattern 3: `$effect(() => { void readProfile(); })` — File 3 and File 4.
- Pattern 4: `_pending` promise coalescing — File 1.
- Pattern 5: deep mutation via proxy — `store.profile.x = ...` in
  multiple files.
- Pattern 6: rejected `{#snippet}` approach confirmed unnecessary.
- Pattern 7: testing initials via DOM, not via `page.evaluate` of the
  module — new test file uses DOM assertions only.
- Pattern 8: `bind:value={store.profile.full_name}` — File 4.
- Pattern 9: child `$bindable()` count prop + parent `bind:count` + child
  `$effect(() => { count = items.length; })` — Files 7-11 (six children).
  Validated as canonical idiom; see
  `workbench/2-plan/research/SVELTE5_BINDABLE_NOTES_2026-05-13_restyle-profile-editor.md`.
  Hazard: never read AND write the same variable inside one `$effect`
  (would trigger `effect_update_depth_exceeded`). The shape above is
  write-only on `count` — safe.

---

## Risks

1. **PhotoUpload `bind:photo`.** File 5 plan-phase verification step:
   read `PhotoUpload.svelte` and confirm `photo` is declared
   `$bindable()`. If not, change File 4 to a callback pattern.
2. **`.container` test dependency.** Resolved via File 12's
   `.container-wide` override — `.container` element still exists.
2b. **`test_design_tokens.py` regression risk.** Inspected at plan time
   (M6 fix). The test reads `getComputedStyle(document.body)` and
   asserts only on `backgroundColor`, `color`, `fontFamily`, `fontSize`,
   `lineHeight`, `fontFeatureSettings`, `-webkit-font-smoothing`.
   Adding `.container-wide` to `global.css` targets the `.container-wide`
   class, not `body`, so it cannot affect any of the seven computed
   properties asserted by the test. No counter/hash/selector-enumeration
   logic exists. **Verified — adding `.container-wide` is safe for this
   test.**
3. **Skills pill primitive override.** Inspector checklist item — does
   the design accept Skills' sentence-case 12px Inter pill labels (vs.
   the editorial `.pill` mono uppercase default)?
4. **Lean-code function-name compliance.** Several existing functions
   (`save`, `add`, `edit`, `cancel`, `validate`, `formatDate`) violate
   lean-code rules. The slice **does not** rename them — they're
   pre-existing, out of scope. Only NEW functions introduced by this
   slice follow lean-code. Document as a follow-up. The new
   `profileStore.svelte.js` uses `readProfile`, `writeProfile`,
   `parseInitials`, `readInitials`. The Playwright tests use
   `create_users_mock` / `write_users_response` to intercept `/api/users`
   GETs at the network layer; no test-only branch exists in the store.
5. **CEFR helper.** New helper `readCefrLabel(level)` in File 10 —
   verb-prefix `read` is correct.
6. **Photo state during save** — verified at plan time (MN4 fix).
   `PhotoUpload.svelte` posts cropped images to its own endpoint
   (`POST /api/photos`); the `photo` field on the user record is
   independent of the photo bytes. Today, `UserProfile.svelte` already
   passes `data.photo` into `updateUser`, but the backend `UserUpdate`
   Pydantic schema does not include a `photo` field — so the value is
   silently dropped at the API boundary. After the refactor,
   `bind:photo={store.profile.photo}` continues to mirror the upload
   into the store, and `writeProfile()` continues to call `updateUser`
   with the same dropped-on-the-server semantics. **Net behaviour
   unchanged.** No save-coupling required.

---

## Build & verify steps

1. Create File 1 (profileStore) — unit test parseInitials manually in
   browser console.
2. Create File 2 (EditorialSection) — visually verify in Storybook-less
   harness by mounting alone if needed; otherwise verify via File 6.
3. Modify File 3 (Topbar) — `bun run build` and check `??` shows for
   the unloaded/empty profile; under `pytest tests/test_topbar_shell.py`
   the mocked `GET /api/users` response feeds `parseInitials` so the
   circle reads `IM`.
4. Modify File 4 (UserProfile) — verify Identity card renders, fields
   bind, validation works, save fires `PUT /api/users`.
5. Verify File 5 (PhotoUpload) bind works.
6. Modify File 6 (ProfileEditor) — verify all 7 sections render with
   editorial headers.
7. Modify File 7 (WorkExperience) — verify timeline rendering.
8. Modify File 8 (Education) — verify year-prefixed list.
9. Modify File 9 (Skills) — verify pill cluster + dashed add pill.
10. Modify File 10 (Languages) — verify 2-col grid + drag.
11. Modify File 11 (Projects) — verify row pattern.
12. Modify File 12 (App) — verify `.container-wide` doesn't break the
    Topbar layout.
13. Modify File 13 (global.css) — single rule add.
14. Delete File X (Section.svelte) — `grep` proves no consumers; delete.
15. Modify `tests/test_topbar_shell.py::test_user_initials_circle`.
16. Add `tests/test_profile_editor_restyle.py`.
17. Run `bun run build && pytest tests/` — expect zero failures.
18. Run manual inspector checklist (see CHECKLIST_*.md).
