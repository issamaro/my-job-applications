<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->
<!-- Scope: Editorial languages grid — CEFR cards, drag reorder, edit form, count bindable. -->

<script>
  import { getLanguages, createLanguage, updateLanguage, deleteLanguage, reorderLanguages } from '../lib/api.js';
  import ConfirmDialog from './ConfirmDialog.svelte';

  const CEFR_LEVELS = [
    { value: 'A1', label: 'A1 (Beginner)' },
    { value: 'A2', label: 'A2 (Elementary)' },
    { value: 'B1', label: 'B1 (Intermediate)' },
    { value: 'B2', label: 'B2 (Upper Intermediate)' },
    { value: 'C1', label: 'C1 (Advanced)' },
    { value: 'C2', label: 'C2 (Proficient)' }
  ];

  let { count = $bindable(0) } = $props();

  let items = $state([]);
  let loading = $state(true);
  let error = $state(null);
  let editingId = $state(null);
  let showForm = $state(false);
  let saving = $state(false);
  let saved = $state(false);
  let savedTimeout = null;
  let confirmDelete = $state(null);
  let fieldErrors = $state({});
  let draggedIndex = $state(null);

  const emptyForm = {
    name: '',
    level: ''
  };
  let formData = $state({ ...emptyForm });

  $effect(() => {
    loadData();
  });

  $effect(() => {
    count = items.length;
  });

  async function loadData() {
    try {
      loading = true;
      items = await getLanguages();
    } catch (e) {
      error = 'Could not load profile. Please refresh.';
    } finally {
      loading = false;
    }
  }

  export function add() {
    editingId = null;
    formData = { ...emptyForm };
    showForm = true;
    fieldErrors = {};
  }

  function readCefrLabel(level) {
    const entry = CEFR_LEVELS.find(l => l.value === level);
    return entry ? entry.label : level;
  }

  function edit(item) {
    editingId = item.id;
    formData = {
      name: item.name || '',
      level: item.level || ''
    };
    showForm = true;
    fieldErrors = {};
  }

  function cancel() {
    showForm = false;
    editingId = null;
    fieldErrors = {};
  }

  function validate() {
    fieldErrors = {};
    if (!formData.name.trim()) {
      fieldErrors.name = 'Required';
    }
    if (!formData.level) {
      fieldErrors.level = 'Required';
    }
    return Object.keys(fieldErrors).length === 0;
  }

  async function save() {
    if (!validate()) return;

    try {
      saving = true;
      const payload = {
        name: formData.name.trim(),
        level: formData.level
      };

      if (editingId) {
        const updated = await updateLanguage(editingId, payload);
        items = items.map(i => i.id === editingId ? updated : i);
      } else {
        const created = await createLanguage(payload);
        items = [...items, created];
      }
      showForm = false;
      editingId = null;
      saved = true;
      if (savedTimeout) clearTimeout(savedTimeout);
      savedTimeout = setTimeout(() => { saved = false; }, 2000);
    } catch (e) {
      error = 'Could not save. Please try again.';
    } finally {
      saving = false;
    }
  }

  function requestDelete() {
    confirmDelete = editingId;
  }

  async function confirmDeleteAction() {
    try {
      await deleteLanguage(confirmDelete);
      items = items.filter(i => i.id !== confirmDelete);
      confirmDelete = null;
      showForm = false;
      editingId = null;
    } catch (e) {
      error = 'Could not delete. Please try again.';
      confirmDelete = null;
    }
  }

  function handleDragStart(e, index) {
    draggedIndex = index;
    e.dataTransfer.effectAllowed = 'move';
  }

  function handleDragOver(e, index) {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === index) return;

    const newItems = [...items];
    const draggedItem = newItems[draggedIndex];
    newItems.splice(draggedIndex, 1);
    newItems.splice(index, 0, draggedItem);
    items = newItems;
    draggedIndex = index;
  }

  async function handleDrop(e) {
    e.preventDefault();
    if (draggedIndex === null) return;

    const reorderData = items.map((item, index) => ({
      id: item.id,
      display_order: index
    }));

    try {
      await reorderLanguages(reorderData);
    } catch (err) {
      error = 'Could not save order. Please try again.';
      await loadData();
    }
    draggedIndex = null;
  }

  function handleDragEnd() {
    draggedIndex = null;
  }
</script>

{#if confirmDelete}
  <ConfirmDialog
    message="Delete this language?"
    onConfirm={confirmDeleteAction}
    onCancel={() => confirmDelete = null}
  />
{/if}

{#if loading}
  <div class="skeleton" style="height: 60px; margin-bottom: 8px;"></div>
{:else if error}
  <div class="form-error" role="alert">{error}</div>
{:else if items.length === 0 && !showForm}
  <div class="empty-state">No languages added yet.</div>
{:else}
  <div class="lang-grid">
    {#each items as item, index}
      {#if editingId === item.id && showForm}
        <div class="lang-edit-block">
          <form class="form" onsubmit={(e) => e.preventDefault()}>
            <div class="form-row-inline">
              <div class="form-row">
                <label for="name" class="required">Language</label>
                <input
                  id="name"
                  class="input"
                  type="text"
                  bind:value={formData.name}
                  class:error={fieldErrors.name}
                  aria-required="true"
                  aria-invalid={!!fieldErrors.name}
                  aria-describedby={fieldErrors.name ? 'name-error' : undefined}
                />
                {#if fieldErrors.name}
                  <span id="name-error" class="error-message" role="alert">{fieldErrors.name}</span>
                {/if}
              </div>

              <div class="form-row">
                <label for="level" class="required">Level</label>
                <select
                  id="level"
                  class="input"
                  bind:value={formData.level}
                  class:error={fieldErrors.level}
                  aria-required="true"
                  aria-invalid={!!fieldErrors.level}
                  aria-describedby={fieldErrors.level ? 'level-error' : undefined}
                >
                  <option value="">Select level</option>
                  {#each CEFR_LEVELS as lvl}
                    <option value={lvl.value}>{lvl.label}</option>
                  {/each}
                </select>
                {#if fieldErrors.level}
                  <span id="level-error" class="error-message" role="alert">{fieldErrors.level}</span>
                {/if}
              </div>
            </div>

            <div class="form-actions">
              <button class="btn btn-primary" onclick={save} disabled={saving}>
                {saving ? 'Saving...' : 'Save'}
              </button>
              <button class="btn" onclick={cancel}>Cancel</button>
              <button type="button" class="delete-link" onclick={requestDelete}>Delete</button>
            </div>
          </form>
        </div>
      {:else}
        <div
          class="lang-card"
          class:dragging={draggedIndex === index}
          draggable="true"
          ondragstart={(e) => handleDragStart(e, index)}
          ondragover={(e) => handleDragOver(e, index)}
          ondrop={handleDrop}
          ondragend={handleDragEnd}
        >
          <div class="lang-label">
            <div class="lang-name">{item.name}</div>
            <div class="lang-level">{readCefrLabel(item.level)}</div>
          </div>
          <span class="num lang-code">{item.level}</span>
          <button class="btn btn-ghost lang-edit" onclick={() => edit(item)}>Edit</button>
        </div>
      {/if}
    {/each}
  </div>
{/if}

{#if showForm && !editingId}
  <div class="lang-add-block">
    <form class="form" onsubmit={(e) => e.preventDefault()}>
      <div class="form-row-inline">
        <div class="form-row">
          <label for="new_name" class="required">Language</label>
          <input
            id="new_name"
            class="input"
            type="text"
            bind:value={formData.name}
            class:error={fieldErrors.name}
            aria-required="true"
            aria-invalid={!!fieldErrors.name}
            aria-describedby={fieldErrors.name ? 'new-name-error' : undefined}
          />
          {#if fieldErrors.name}
            <span id="new-name-error" class="error-message" role="alert">{fieldErrors.name}</span>
          {/if}
        </div>

        <div class="form-row">
          <label for="new_level" class="required">Level</label>
          <select
            id="new_level"
            class="input"
            bind:value={formData.level}
            class:error={fieldErrors.level}
            aria-required="true"
            aria-invalid={!!fieldErrors.level}
            aria-describedby={fieldErrors.level ? 'new-level-error' : undefined}
          >
            <option value="">Select level</option>
            {#each CEFR_LEVELS as lvl}
              <option value={lvl.value}>{lvl.label}</option>
            {/each}
          </select>
          {#if fieldErrors.level}
            <span id="new-level-error" class="error-message" role="alert">{fieldErrors.level}</span>
          {/if}
        </div>
      </div>

      <div class="form-actions">
        <button class="btn btn-primary" onclick={save} disabled={saving}>
          {saving ? 'Saving...' : 'Save'}
        </button>
        <button class="btn" onclick={cancel}>Cancel</button>
      </div>
    </form>
  </div>
{/if}

<button class="btn lang-add" onclick={() => add()}>
  <span aria-hidden="true">+</span> Add language
</button>

{#if saved}
  <span class="saved-indicator" class:fading={!saving}>Saved</span>
{/if}

<style>
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
  .lang-add { margin-top: 12px; font-size: 12px; }
  .lang-edit-block {
    grid-column: 1 / -1;
    padding: 16px 0;
    border-top: 1px solid var(--rule-soft);
  }
  .lang-add-block {
    padding: 16px 0;
    border-top: 1px solid var(--rule-soft);
    margin-top: 16px;
  }
</style>
