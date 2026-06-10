<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->
<!-- Scope: Editorial skills cluster — pill chips, dashed add pill, count bindable. -->

<script>
  import { getSkills, createSkills, deleteSkill } from '../lib/api.js';
  import ConfirmDialog from './ConfirmDialog.svelte';

  let { count = $bindable(0) } = $props();

  let items = $state([]);
  let loading = $state(true);
  let error = $state(null);
  let inputValue = $state('');
  let saving = $state(false);
  let saved = $state(false);
  let savedTimeout = null;
  let confirmDelete = $state(null);

  $effect(() => {
    loadData();
  });

  $effect(() => {
    count = items.length;
  });

  async function loadData() {
    try {
      loading = true;
      items = await getSkills();
    } catch (e) {
      error = 'Could not load profile. Please refresh.';
    } finally {
      loading = false;
    }
  }

  function focusInput() {
    document.getElementById('skill-input')?.focus();
  }

  async function handleKeydown(e) {
    if (e.key === 'Enter' && inputValue.trim()) {
      e.preventDefault();
      await addSkills();
    }
  }

  async function addSkills() {
    if (!inputValue.trim()) return;

    try {
      saving = true;
      const newSkills = await createSkills(inputValue);
      await loadData();
      inputValue = '';
      saved = true;
      if (savedTimeout) clearTimeout(savedTimeout);
      savedTimeout = setTimeout(() => { saved = false; }, 2000);
    } catch (e) {
      error = 'Could not save. Please try again.';
    } finally {
      saving = false;
    }
  }

  function requestDelete(id) {
    confirmDelete = id;
  }

  async function confirmDeleteAction() {
    try {
      await deleteSkill(confirmDelete);
      items = items.filter(i => i.id !== confirmDelete);
      confirmDelete = null;
    } catch (e) {
      error = 'Could not delete. Please try again.';
      confirmDelete = null;
    }
  }
</script>

{#if confirmDelete}
  <ConfirmDialog
    title="Remove this skill?"
    onConfirm={confirmDeleteAction}
    onCancel={() => confirmDelete = null}
  />
{/if}

{#if loading}
  <div class="skeleton" style="height: 40px;"></div>
{:else if error}
  <div class="form-error">{error}</div>
{:else}
  <div class="skill-cluster">
    {#each items as item}
      <span class="pill skill-pill">
        {item.name}
        <button
          class="skill-remove"
          onclick={() => requestDelete(item.id)}
          aria-label="Remove {item.name}"
        >×</button>
      </span>
    {/each}
    <button class="pill skill-pill-add" onclick={focusInput}>+ add</button>
  </div>

  <div class="skill-input-row">
    <input
      id="skill-input"
      class="input"
      type="text"
      placeholder="Python, FastAPI, SQL"
      bind:value={inputValue}
      onkeydown={handleKeydown}
      disabled={saving}
    />
    <button
      class="btn btn-primary"
      onclick={addSkills}
      disabled={saving || !inputValue.trim()}
    >
      {saving ? 'Adding...' : 'Add'}
    </button>
  </div>

  {#if saved}
    <span class="saved-indicator" class:fading={!saving}>Saved</span>
  {/if}
{/if}

<style>
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
</style>
