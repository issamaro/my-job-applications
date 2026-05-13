<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->
<!-- Scope: Editorial work-experience list — timeline rows, edit form, count bindable. -->

<script>
  import { getWorkExperiences, createWorkExperience, updateWorkExperience, deleteWorkExperience } from '../lib/api.js';
  import { supportsMonthInput } from '../lib/api.js';
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

  $effect(() => {
    count = items.length;
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
  <div class="exp-list">
    {#each items as item, i}
      {#if editingId === item.id && showForm}
        <div class="exp-edit-block">
          <form class="form" onsubmit={(e) => e.preventDefault()}>
            <div class="form-row">
              <label for="company" class="required">Company</label>
              <input
                id="company"
                class="input"
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
                class="input"
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
                class="input"
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
                    class="input"
                    type="month"
                    bind:value={formData.start_date}
                    class:error={fieldErrors.start_date}
                    aria-required="true"
                  />
                {:else}
                  <input
                    id="start_date"
                    class="input"
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
                    class="input"
                    type="month"
                    bind:value={formData.end_date}
                    disabled={formData.is_current}
                    class:error={fieldErrors.end_date}
                  />
                {:else}
                  <input
                    id="end_date"
                    class="input"
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

{#if showForm && !editingId}
  <div class="exp-add-block">
    <form class="form" onsubmit={(e) => e.preventDefault()}>
      <div class="form-row">
        <label for="new_company" class="required">Company</label>
        <input
          id="new_company"
          class="input"
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
          class="input"
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
          class="input"
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
              class="input"
              type="month"
              bind:value={formData.start_date}
              class:error={fieldErrors.start_date}
              aria-required="true"
            />
          {:else}
            <input
              id="new_start_date"
              class="input"
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
              class="input"
              type="month"
              bind:value={formData.end_date}
              disabled={formData.is_current}
              class:error={fieldErrors.end_date}
            />
          {:else}
            <input
              id="new_end_date"
              class="input"
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

<button class="btn exp-add" onclick={() => add()}>
  <span aria-hidden="true">+</span> Add experience
</button>

{#if saved}
  <span class="saved-indicator" class:fading={!saving}>Saved</span>
{/if}

<style>
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
  .exp-edit-block { padding: 16px 0; border-top: 1px solid var(--rule-soft); }
  .exp-add-block { padding: 16px 0; border-top: 1px solid var(--rule-soft); margin-top: 16px; }
</style>
