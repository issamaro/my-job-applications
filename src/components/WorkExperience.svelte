<script>
  import { getWorkExperiences, createWorkExperience, updateWorkExperience, deleteWorkExperience } from '../lib/api.js';
  import { supportsMonthInput } from '../lib/api.js';
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
  let useMonthInput = $state(true);

  const emptyForm = {
    company: '',
    title: '',
    start_date: '',
    end_date: '',
    is_current: false,
    description: '',
    location: ''
  };
  let formData = $state({ ...emptyForm });

  $effect(() => {
    loadData();
    useMonthInput = supportsMonthInput();
  });

  async function loadData() {
    try {
      loading = true;
      items = await getWorkExperiences();
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
      company: item.company || '',
      title: item.title || '',
      start_date: item.start_date || '',
      end_date: item.end_date || '',
      is_current: item.is_current || false,
      description: item.description || '',
      location: item.location || ''
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
    if (!formData.company.trim()) {
      fieldErrors.company = 'Required';
    }
    if (!formData.title.trim()) {
      fieldErrors.title = 'Required';
    }
    if (!formData.start_date) {
      fieldErrors.start_date = 'Required';
    } else if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(formData.start_date)) {
      fieldErrors.start_date = 'Invalid date';
    }
    if (formData.end_date && !/^\d{4}-(0[1-9]|1[0-2])$/.test(formData.end_date)) {
      fieldErrors.end_date = 'Invalid date';
    }
    if (formData.end_date && formData.start_date && formData.end_date < formData.start_date) {
      fieldErrors.end_date = 'End date must be after start date';
    }
    return Object.keys(fieldErrors).length === 0;
  }

  async function save() {
    if (!validate()) return;

    try {
      saving = true;
      const payload = {
        ...formData,
        end_date: formData.is_current ? null : formData.end_date || null
      };

      if (editingId) {
        const updated = await updateWorkExperience(editingId, payload);
        items = items.map(i => i.id === editingId ? updated : i);
      } else {
        const created = await createWorkExperience(payload);
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
      await deleteWorkExperience(confirmDelete);
      items = items.filter(i => i.id !== confirmDelete);
      confirmDelete = null;
      showForm = false;
      editingId = null;
    } catch (e) {
      error = 'Could not delete. Please try again.';
      confirmDelete = null;
    }
  }

  function formatDate(date) {
    if (!date) return '';
    const [year, month] = date.split('-');
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return `${months[parseInt(month) - 1]} ${year}`;
  }
</script>

{#if confirmDelete}
  <ConfirmDialog
    message="Delete this work experience?"
    onConfirm={confirmDeleteAction}
    onCancel={() => confirmDelete = null}
  />
{/if}

{#if loading}
  <div class="skeleton" style="height: 60px; margin-bottom: 8px;"></div>
  <div class="skeleton" style="height: 60px;"></div>
{:else if error}
  <div class="form-error">{error}</div>
{:else if items.length === 0 && !showForm}
  <div class="empty-state">No work experience added yet.</div>
{:else}
  <div class="item-list">
    {#each items as item}
      {#if editingId === item.id && showForm}
        <div class="item">
          <form class="form" onsubmit={(e) => e.preventDefault()}>
            <div class="form-row">
              <label for="company" class="required">Company</label>
              <input
                id="company"
                type="text"
                bind:value={formData.company}
                class:error={fieldErrors.company}
                aria-required="true"
              />
              {#if fieldErrors.company}
                <span class="error-message">{fieldErrors.company}</span>
              {/if}
            </div>

            <div class="form-row">
              <label for="title" class="required">Title</label>
              <input
                id="title"
                type="text"
                bind:value={formData.title}
                class:error={fieldErrors.title}
                aria-required="true"
              />
              {#if fieldErrors.title}
                <span class="error-message">{fieldErrors.title}</span>
              {/if}
            </div>

            <div class="form-row">
              <label for="exp_location">Location</label>
              <input
                id="exp_location"
                type="text"
                bind:value={formData.location}
              />
            </div>

            <div class="form-row-inline">
              <div class="form-row">
                <label for="start_date" class="required">Start</label>
                {#if useMonthInput}
                  <input
                    id="start_date"
                    type="month"
                    bind:value={formData.start_date}
                    class:error={fieldErrors.start_date}
                    aria-required="true"
                  />
                {:else}
                  <input
                    id="start_date"
                    type="text"
                    placeholder="YYYY-MM"
                    pattern="\d{4}-(0[1-9]|1[0-2])"
                    bind:value={formData.start_date}
                    class:error={fieldErrors.start_date}
                    aria-required="true"
                  />
                {/if}
                {#if fieldErrors.start_date}
                  <span class="error-message">{fieldErrors.start_date}</span>
                {/if}
              </div>

              <div class="form-row">
                <label for="end_date">End</label>
                {#if useMonthInput}
                  <input
                    id="end_date"
                    type="month"
                    bind:value={formData.end_date}
                    disabled={formData.is_current}
                    class:error={fieldErrors.end_date}
                  />
                {:else}
                  <input
                    id="end_date"
                    type="text"
                    placeholder="YYYY-MM"
                    pattern="\d{4}-(0[1-9]|1[0-2])"
                    bind:value={formData.end_date}
                    disabled={formData.is_current}
                    class:error={fieldErrors.end_date}
                  />
                {/if}
                {#if fieldErrors.end_date}
                  <span class="error-message">{fieldErrors.end_date}</span>
                {/if}
              </div>
            </div>

            <div class="checkbox-row">
              <input
                id="is_current"
                type="checkbox"
                bind:checked={formData.is_current}
              />
              <label for="is_current">Current position</label>
            </div>

            <div class="form-row">
              <label for="description">Description</label>
              <textarea
                id="description"
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
              <div class="item-title">{item.title} · {item.company}</div>
              <div class="item-subtitle">
                {formatDate(item.start_date)} – {item.is_current ? 'Present' : formatDate(item.end_date)}
                {#if item.location} · {item.location}{/if}
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
        <label for="new_company" class="required">Company</label>
        <input
          id="new_company"
          type="text"
          bind:value={formData.company}
          class:error={fieldErrors.company}
          aria-required="true"
        />
        {#if fieldErrors.company}
          <span class="error-message">{fieldErrors.company}</span>
        {/if}
      </div>

      <div class="form-row">
        <label for="new_title" class="required">Title</label>
        <input
          id="new_title"
          type="text"
          bind:value={formData.title}
          class:error={fieldErrors.title}
          aria-required="true"
        />
        {#if fieldErrors.title}
          <span class="error-message">{fieldErrors.title}</span>
        {/if}
      </div>

      <div class="form-row">
        <label for="new_exp_location">Location</label>
        <input
          id="new_exp_location"
          type="text"
          bind:value={formData.location}
        />
      </div>

      <div class="form-row-inline">
        <div class="form-row">
          <label for="new_start_date" class="required">Start</label>
          {#if useMonthInput}
            <input
              id="new_start_date"
              type="month"
              bind:value={formData.start_date}
              class:error={fieldErrors.start_date}
              aria-required="true"
            />
          {:else}
            <input
              id="new_start_date"
              type="text"
              placeholder="YYYY-MM"
              pattern="\d{4}-(0[1-9]|1[0-2])"
              bind:value={formData.start_date}
              class:error={fieldErrors.start_date}
              aria-required="true"
            />
          {/if}
          {#if fieldErrors.start_date}
            <span class="error-message">{fieldErrors.start_date}</span>
          {/if}
        </div>

        <div class="form-row">
          <label for="new_end_date">End</label>
          {#if useMonthInput}
            <input
              id="new_end_date"
              type="month"
              bind:value={formData.end_date}
              disabled={formData.is_current}
              class:error={fieldErrors.end_date}
            />
          {:else}
            <input
              id="new_end_date"
              type="text"
              placeholder="YYYY-MM"
              pattern="\d{4}-(0[1-9]|1[0-2])"
              bind:value={formData.end_date}
              disabled={formData.is_current}
              class:error={fieldErrors.end_date}
            />
          {/if}
          {#if fieldErrors.end_date}
            <span class="error-message">{fieldErrors.end_date}</span>
          {/if}
        </div>
      </div>

      <div class="checkbox-row">
        <input
          id="new_is_current"
          type="checkbox"
          bind:checked={formData.is_current}
        />
        <label for="new_is_current">Current position</label>
      </div>

      <div class="form-row">
        <label for="new_description">Description</label>
        <textarea
          id="new_description"
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
