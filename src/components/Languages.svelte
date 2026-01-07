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
  <div class="item-list">
    {#each items as item, index}
      {#if editingId === item.id && showForm}
        <div class="item">
          <form class="form" onsubmit={(e) => e.preventDefault()}>
            <div class="form-row-inline">
              <div class="form-row">
                <label for="name" class="required">Language</label>
                <input
                  id="name"
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
          class="item"
          class:dragging={draggedIndex === index}
          draggable="true"
          ondragstart={(e) => handleDragStart(e, index)}
          ondragover={(e) => handleDragOver(e, index)}
          ondrop={handleDrop}
          ondragend={handleDragEnd}
        >
          <div class="item-header">
            <div class="drag-handle-wrapper">
              <span class="drag-handle" aria-label="Drag to reorder">&#8942;&#8942;</span>
              <div>
                <div class="item-title">{item.name}</div>
                <div class="item-subtitle">{item.level}</div>
              </div>
            </div>
            <button class="edit-btn" onclick={() => edit(item)}>Edit</button>
          </div>
        </div>
      {/if}
    {/each}
  </div>
{/if}

{#if showForm && !editingId}
  <div class="item" style="border-top: 1px solid #e0e0e0; margin-top: 16px;">
    <form class="form" onsubmit={(e) => e.preventDefault()}>
      <div class="form-row-inline">
        <div class="form-row">
          <label for="new_name" class="required">Language</label>
          <input
            id="new_name"
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

{#if saved}
  <span class="saved-indicator" class:fading={!saving}>Saved</span>
{/if}

<style>
  .drag-handle-wrapper {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .drag-handle {
    cursor: grab;
    color: #999;
    font-size: 16px;
    user-select: none;
  }

  .drag-handle:active {
    cursor: grabbing;
  }

  .item.dragging {
    opacity: 0.5;
    background: #f0f0f0;
  }

  .item[draggable="true"] {
    cursor: default;
  }
</style>
