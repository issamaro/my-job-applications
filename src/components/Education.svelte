<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->
<!-- Scope: Editorial education list — year-prefixed rows, edit form, count bindable. -->

<script>
  import { getEducation, createEducation, updateEducation, deleteEducation } from '../lib/api.js';
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
    institution: '',
    degree: '',
    field_of_study: '',
    graduation_year: '',
    gpa: '',
    notes: ''
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
      items = await getEducation();
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
      institution: item.institution || '',
      degree: item.degree || '',
      field_of_study: item.field_of_study || '',
      graduation_year: item.graduation_year?.toString() || '',
      gpa: item.gpa?.toString() || '',
      notes: item.notes || ''
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
    if (!formData.institution.trim()) {
      fieldErrors.institution = 'Required';
    }
    if (!formData.degree.trim()) {
      fieldErrors.degree = 'Required';
    }
    return Object.keys(fieldErrors).length === 0;
  }

  async function save() {
    if (!validate()) return;

    try {
      saving = true;
      const payload = {
        ...formData,
        graduation_year: formData.graduation_year ? parseInt(formData.graduation_year) : null,
        gpa: formData.gpa ? parseFloat(formData.gpa) : null
      };

      if (editingId) {
        const updated = await updateEducation(editingId, payload);
        items = items.map(i => i.id === editingId ? updated : i);
      } else {
        const created = await createEducation(payload);
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
      await deleteEducation(confirmDelete);
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
    title="Delete this education entry?"
    onConfirm={confirmDeleteAction}
    onCancel={() => confirmDelete = null}
  />
{/if}

{#if loading}
  <div class="skeleton" style="height: 60px; margin-bottom: 8px;"></div>
{:else if error}
  <div class="form-error">{error}</div>
{:else if items.length === 0 && !showForm}
  <div class="empty-state">No education added yet.</div>
{:else}
  <div class="edu-list">
    {#each items as item, i}
      {#if editingId === item.id && showForm}
        <div class="edu-edit-block">
          <form class="form" onsubmit={(e) => e.preventDefault()}>
            <div class="form-row">
              <label for="institution" class="required">Institution</label>
              <input
                id="institution"
                class="input"
                type="text"
                bind:value={formData.institution}
                class:error={fieldErrors.institution}
                aria-required="true"
              />
              {#if fieldErrors.institution}
                <span class="error-message">{fieldErrors.institution}</span>
              {/if}
            </div>

            <div class="form-row-inline">
              <div class="form-row">
                <label for="degree" class="required">Degree</label>
                <input
                  id="degree"
                  class="input"
                  type="text"
                  bind:value={formData.degree}
                  class:error={fieldErrors.degree}
                  aria-required="true"
                />
                {#if fieldErrors.degree}
                  <span class="error-message">{fieldErrors.degree}</span>
                {/if}
              </div>

              <div class="form-row">
                <label for="field_of_study">Field</label>
                <input
                  id="field_of_study"
                  class="input"
                  type="text"
                  bind:value={formData.field_of_study}
                />
              </div>
            </div>

            <div class="form-row-inline">
              <div class="form-row">
                <label for="graduation_year">Year</label>
                <input
                  id="graduation_year"
                  class="input"
                  type="number"
                  min="1900"
                  max="2100"
                  bind:value={formData.graduation_year}
                />
              </div>

              <div class="form-row">
                <label for="gpa">GPA</label>
                <input
                  id="gpa"
                  class="input"
                  type="number"
                  step="0.01"
                  min="0"
                  max="4"
                  bind:value={formData.gpa}
                />
              </div>
            </div>

            <div class="form-row">
              <label for="notes">Notes</label>
              <textarea
                id="notes"
                class="textarea"
                bind:value={formData.notes}
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
        <div class="edu-row" class:not-first={i > 0}>
          <div class="edu-year num">{item.graduation_year || ''}</div>
          <div>
            <div class="edu-title">
              {item.degree}{item.field_of_study ? ` ${item.field_of_study}` : ''}
            </div>
            <div class="edu-institution">{item.institution}</div>
            {#if item.notes}
              <div class="edu-notes">{item.notes}</div>
            {/if}
          </div>
          <button class="btn btn-ghost edu-edit" onclick={() => edit(item)}>Edit</button>
        </div>
      {/if}
    {/each}
  </div>
{/if}

{#if showForm && !editingId}
  <div class="edu-add-block">
    <form class="form" onsubmit={(e) => e.preventDefault()}>
      <div class="form-row">
        <label for="new_institution" class="required">Institution</label>
        <input
          id="new_institution"
          class="input"
          type="text"
          bind:value={formData.institution}
          class:error={fieldErrors.institution}
          aria-required="true"
        />
        {#if fieldErrors.institution}
          <span class="error-message">{fieldErrors.institution}</span>
        {/if}
      </div>

      <div class="form-row-inline">
        <div class="form-row">
          <label for="new_degree" class="required">Degree</label>
          <input
            id="new_degree"
            class="input"
            type="text"
            bind:value={formData.degree}
            class:error={fieldErrors.degree}
            aria-required="true"
          />
          {#if fieldErrors.degree}
            <span class="error-message">{fieldErrors.degree}</span>
          {/if}
        </div>

        <div class="form-row">
          <label for="new_field_of_study">Field</label>
          <input
            id="new_field_of_study"
            class="input"
            type="text"
            bind:value={formData.field_of_study}
          />
        </div>
      </div>

      <div class="form-row-inline">
        <div class="form-row">
          <label for="new_graduation_year">Year</label>
          <input
            id="new_graduation_year"
            class="input"
            type="number"
            min="1900"
            max="2100"
            bind:value={formData.graduation_year}
          />
        </div>

        <div class="form-row">
          <label for="new_gpa">GPA</label>
          <input
            id="new_gpa"
            class="input"
            type="number"
            step="0.01"
            min="0"
            max="4"
            bind:value={formData.gpa}
          />
        </div>
      </div>

      <div class="form-row">
        <label for="new_notes">Notes</label>
        <textarea
          id="new_notes"
          class="textarea"
          bind:value={formData.notes}
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

<button class="btn edu-add" onclick={() => add()}>
  <span aria-hidden="true">+</span> Add education
</button>

{#if saved}
  <span class="saved-indicator" class:fading={!saving}>Saved</span>
{/if}

<style>
  .edu-list { display: flex; flex-direction: column; }
  .edu-row {
    display: grid;
    grid-template-columns: 70px 1fr auto;
    gap: 18px;
    padding: 12px 0;
  }
  .edu-row.not-first { border-top: 1px solid var(--rule-soft); }
  .edu-year { font-size: 11px; color: var(--ink-3); }
  .edu-title { font-size: 14px; font-weight: 600; }
  .edu-institution { font-size: 12px; color: var(--ink-3); margin-top: 2px; }
  .edu-notes {
    font-size: 13px; color: var(--ink-2);
    margin-top: 8px; line-height: 1.55;
    white-space: pre-wrap;
  }
  .edu-edit { padding: 4px 8px; font-size: 11px; }
  .edu-add { margin-top: 12px; font-size: 12px; }
  .edu-edit-block { padding: 16px 0; border-top: 1px solid var(--rule-soft); }
  .edu-add-block { padding: 16px 0; border-top: 1px solid var(--rule-soft); margin-top: 16px; }
</style>
