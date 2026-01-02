<script>
  import { getSkills, createSkills, deleteSkill } from '../lib/api.js';
  import ConfirmDialog from './ConfirmDialog.svelte';

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

  export function add() {
    // Focus the input when Add is clicked
    const input = document.getElementById('skill-input');
    if (input) input.focus();
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
      // Reload to get proper alphabetical order
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
    message="Remove this skill?"
    onConfirm={confirmDeleteAction}
    onCancel={() => confirmDelete = null}
  />
{/if}

{#if loading}
  <div class="skeleton" style="height: 40px;"></div>
{:else if error}
  <div class="form-error">{error}</div>
{:else}
  {#if items.length === 0}
    <div class="empty-state">No skills added yet.</div>
  {:else}
    <div class="tags">
      {#each items as item}
        <span class="tag">
          {item.name}
          <button
            class="tag-remove"
            onclick={() => requestDelete(item.id)}
            aria-label="Remove {item.name}"
          >×</button>
        </span>
      {/each}
    </div>
  {/if}

  <div class="form" style="margin-top: 16px;">
    <div class="form-row">
      <label for="skill-input">Add skills (comma-separated)</label>
      <div style="display: flex; gap: 8px;">
        <input
          id="skill-input"
          type="text"
          placeholder="Python, FastAPI, SQL"
          bind:value={inputValue}
          onkeydown={handleKeydown}
          disabled={saving}
        />
        <button class="btn btn-primary" onclick={addSkills} disabled={saving || !inputValue.trim()}>
          {saving ? 'Adding...' : 'Add'}
        </button>
      </div>
    </div>
  </div>

  {#if saved}
    <span class="saved-indicator" class:fading={!saving}>Saved</span>
  {/if}
{/if}
