<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->
<!-- Scope: Editorial projects list — 2-col rows, edit form, count bindable. -->

<script>
  import { getProjects, createProject, updateProject, deleteProject } from '../lib/api.js';
  import ConfirmDialog from './ConfirmDialog.svelte';

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

  const emptyForm = {
    name: '',
    description: '',
    technologies: '',
    url: '',
    start_date: '',
    end_date: ''
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
      items = await getProjects();
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
      description: item.description || '',
      technologies: item.technologies || '',
      url: item.url || '',
      start_date: item.start_date || '',
      end_date: item.end_date || ''
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
    return Object.keys(fieldErrors).length === 0;
  }

  async function save() {
    if (!validate()) return;

    try {
      saving = true;
      const payload = {
        ...formData,
        start_date: formData.start_date || null,
        end_date: formData.end_date || null
      };

      if (editingId) {
        const updated = await updateProject(editingId, payload);
        items = items.map(i => i.id === editingId ? updated : i);
      } else {
        const created = await createProject(payload);
        items = [...items, created];
        await loadData();
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
      await deleteProject(confirmDelete);
      items = items.filter(i => i.id !== confirmDelete);
      confirmDelete = null;
      showForm = false;
      editingId = null;
    } catch (e) {
      error = 'Could not delete. Please try again.';
      confirmDelete = null;
    }
  }
</script>

{#if confirmDelete}
  <ConfirmDialog
    message="Delete this project?"
    onConfirm={confirmDeleteAction}
    onCancel={() => confirmDelete = null}
  />
{/if}

{#if loading}
  <div class="skeleton" style="height: 60px; margin-bottom: 8px;"></div>
{:else if error}
  <div class="form-error">{error}</div>
{:else if items.length === 0 && !showForm}
  <div class="empty-state">No projects added yet.</div>
{:else}
  <div class="proj-list">
    {#each items as item, i}
      {#if editingId === item.id && showForm}
        <div class="proj-edit-block">
          <form class="form" onsubmit={(e) => e.preventDefault()}>
            <div class="form-row">
              <label for="name" class="required">Name</label>
              <input
                id="name"
                class="input"
                type="text"
                bind:value={formData.name}
                class:error={fieldErrors.name}
                aria-required="true"
              />
              {#if fieldErrors.name}
                <span class="error-message">{fieldErrors.name}</span>
              {/if}
            </div>

            <div class="form-row">
              <label for="proj_url">URL</label>
              <input
                id="proj_url"
                class="input"
                type="url"
                bind:value={formData.url}
              />
            </div>

            <div class="form-row">
              <label for="technologies">Technologies</label>
              <input
                id="technologies"
                class="input"
                type="text"
                placeholder="Svelte, Python, SQL"
                bind:value={formData.technologies}
              />
            </div>

            <div class="form-row">
              <label for="proj_description">Description</label>
              <textarea
                id="proj_description"
                class="textarea"
                bind:value={formData.description}
              ></textarea>
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
          <button class="btn btn-ghost proj-edit" onclick={() => edit(item)}>Edit</button>
        </div>
      {/if}
    {/each}
  </div>
{/if}

{#if showForm && !editingId}
  <div class="proj-add-block">
    <form class="form" onsubmit={(e) => e.preventDefault()}>
      <div class="form-row">
        <label for="new_name" class="required">Name</label>
        <input
          id="new_name"
          class="input"
          type="text"
          bind:value={formData.name}
          class:error={fieldErrors.name}
          aria-required="true"
        />
        {#if fieldErrors.name}
          <span class="error-message">{fieldErrors.name}</span>
        {/if}
      </div>

      <div class="form-row">
        <label for="new_proj_url">URL</label>
        <input
          id="new_proj_url"
          class="input"
          type="url"
          bind:value={formData.url}
        />
      </div>

      <div class="form-row">
        <label for="new_technologies">Technologies</label>
        <input
          id="new_technologies"
          class="input"
          type="text"
          placeholder="Svelte, Python, SQL"
          bind:value={formData.technologies}
        />
      </div>

      <div class="form-row">
        <label for="new_proj_description">Description</label>
        <textarea
          id="new_proj_description"
          class="textarea"
          bind:value={formData.description}
        ></textarea>
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

<button class="btn proj-add" onclick={() => add()}>
  <span aria-hidden="true">+</span> Add project
</button>

{#if saved}
  <span class="saved-indicator" class:fading={!saving}>Saved</span>
{/if}

<style>
  .proj-list { display: flex; flex-direction: column; }
  .proj-row {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 18px;
    padding: 16px 0;
  }
  .proj-row.not-first { border-top: 1px solid var(--rule-soft); }
  .proj-name { font-size: 14px; font-weight: 600; }
  .proj-sub { font-size: 12px; color: var(--ink-3); margin-top: 2px; }
  .proj-desc {
    font-size: 13px; color: var(--ink-2);
    margin-top: 8px; line-height: 1.55;
    white-space: pre-wrap;
  }
  .proj-edit { padding: 4px 8px; font-size: 11px; }
  .proj-add { margin-top: 12px; font-size: 12px; }
  .proj-edit-block { padding: 16px 0; border-top: 1px solid var(--rule-soft); }
  .proj-add-block { padding: 16px 0; border-top: 1px solid var(--rule-soft); margin-top: 16px; }
</style>
