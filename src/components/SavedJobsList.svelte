<script>
  import ConfirmDialog from './ConfirmDialog.svelte';
  import SavedJobItem from './SavedJobItem.svelte';
  import { getJobs, deleteJob, getJob } from '../lib/api.js';

  let { onLoad, onSelectResume, selectedId = null } = $props();

  let jobs = $state([]);
  let loading = $state(true);
  let error = $state(null);
  let collapsed = $state(false);
  let deleteId = $state(null);
  let deleteResumeCount = $state(0);

  $effect(() => {
    loadJobs();
  });

  async function loadJobs() {
    error = null;
    try {
      jobs = await getJobs();
    } catch (e) {
      console.error('Failed to load jobs:', e);
      error = 'Could not load saved jobs. Please refresh the page.';
    } finally {
      loading = false;
    }
  }

  async function handleLoad(id, textPreview, title) {
    try {
      // Fetch full job to get complete original_text
      const job = await getJob(id);
      onLoad(id, job.original_text, title);
    } catch (e) {
      console.error('Failed to load job:', e);
    }
  }

  function confirmDelete(id, resumeCount) {
    deleteId = id;
    deleteResumeCount = resumeCount;
  }

  async function handleDelete() {
    if (deleteId) {
      try {
        await deleteJob(deleteId);
        jobs = jobs.filter(j => j.id !== deleteId);
      } catch (e) {
        console.error('Failed to delete job:', e);
      }
      deleteId = null;
    }
  }

  export function refresh() {
    loadJobs();
  }
</script>

<div class="saved-jobs-section">
  <button
    class="saved-jobs-header"
    onclick={() => collapsed = !collapsed}
    aria-expanded={!collapsed}
  >
    <h3>Saved Jobs</h3>
    <span class="collapse-toggle">{collapsed ? '[+]' : '[-]'}</span>
  </button>

  {#if !collapsed}
  <div class="saved-jobs-content">
    {#if loading}
      <div class="skeleton"></div>
      <div class="skeleton"></div>
      <div class="skeleton"></div>
    {:else if error}
      <div class="error-state">
        <p>{error}</p>
      </div>
    {:else if jobs.length === 0}
      <div class="empty-state">
        <p>No job applications yet. Paste a job description above to get started.</p>
      </div>
    {:else}
      {#each jobs as job, index}
        <SavedJobItem
          {job}
          selected={selectedId === job.id}
          autoExpand={index === 0}
          onLoad={handleLoad}
          onDelete={confirmDelete}
          {onSelectResume}
        />
      {/each}
    {/if}
  </div>
  {/if}
</div>

{#if deleteId}
<ConfirmDialog
  title="Delete Job?"
  message={`This will delete the job and ${deleteResumeCount} generated resume${deleteResumeCount !== 1 ? 's' : ''}. This cannot be undone.`}
  onConfirm={handleDelete}
  onCancel={() => deleteId = null}
/>
{/if}

<style>
  .saved-jobs-section {
    margin-top: var(--spacing-section);
  }

  .saved-jobs-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    padding: var(--spacing-grid);
    background: none;
    border: 1px solid var(--color-border);
    border-radius: 2px;
    cursor: pointer;
    text-align: left;
    font-family: inherit;

    h3 {
      margin: 0;
    }

    &:hover {
      background: rgb(0 0 0 / 0.02);
    }

    &:focus {
      outline: 2px solid var(--color-primary);
      outline-offset: 2px;
    }
  }

  .collapse-toggle {
    font-family: monospace;
    color: rgb(var(--color-text-rgb) / 0.6);
  }

  .saved-jobs-content {
    border: 1px solid var(--color-border);
    border-top: none;
    border-radius: 0 0 2px 2px;
  }

  .error-state {
    padding: var(--spacing-section);
    text-align: center;
    color: var(--color-error);

    p {
      margin: 0;
    }
  }
</style>
