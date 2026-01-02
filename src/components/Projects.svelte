<script>
  import { getProjects, createProject, updateProject, deleteProject } from '../lib/api.js';
  import ConfirmDialog from './ConfirmDialog.svelte';

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
  <div class="item-list">
    {#each items as item}
      {#if editingId === item.id && showForm}
        <div class="item">
          <form class="form" onsubmit={(e) => e.preventDefault()}>
            <div class="form-row">
              <label for="name" class="required">Name</label>
              <input
                id="name"
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
                type="url"
                bind:value={formData.url}
              />
            </div>

            <div class="form-row">
              <label for="technologies">Technologies</label>
              <input
                id="technologies"
                type="text"
                placeholder="Svelte, Python, SQL"
                bind:value={formData.technologies}
              />
            </div>

            <div class="form-row">
              <label for="proj_description">Description</label>
              <textarea
                id="proj_description"
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
        <div class="item">
          <div class="item-header">
            <div>
              <div class="item-title">{item.name}</div>
              <div class="item-subtitle">
                {#if item.technologies}{item.technologies}{/if}
                {#if item.url}
                  {#if item.technologies} · {/if}
                  <a href={item.url} target="_blank" rel="noopener">{item.url}</a>
                {/if}
              </div>
            </div>
            <button class="edit-btn" onclick={() => edit(item)}>Edit</button>
          </div>
          {#if item.description}
            <div class="item-description">{item.description}</div>
          {/if}
        </div>
      {/if}
    {/each}
  </div>
{/if}

{#if showForm && !editingId}
  <div class="item" style="border-top: 1px solid #e0e0e0; margin-top: 16px;">
    <form class="form" onsubmit={(e) => e.preventDefault()}>
      <div class="form-row">
        <label for="new_name" class="required">Name</label>
        <input
          id="new_name"
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
          type="url"
          bind:value={formData.url}
        />
      </div>

      <div class="form-row">
        <label for="new_technologies">Technologies</label>
        <input
          id="new_technologies"
          type="text"
          placeholder="Svelte, Python, SQL"
          bind:value={formData.technologies}
        />
      </div>

      <div class="form-row">
        <label for="new_proj_description">Description</label>
        <textarea
          id="new_proj_description"
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

{#if saved}
  <span class="saved-indicator" class:fading={!saving}>Saved</span>
{/if}
