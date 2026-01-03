<script>
  import ConfirmDialog from './ConfirmDialog.svelte';
  import SavedJobItem from './SavedJobItem.svelte';
  import { getJobDescriptions, deleteJobDescription, getJobDescription } from '../lib/api.js';

  let { onLoad, selectedId = null } = $props();

  let jobs = $state([]);
  let loading = $state(true);
  let collapsed = $state(false);
  let deleteId = $state(null);
  let deleteResumeCount = $state(0);

  $effect(() => {
    loadJobs();
  });

  async function loadJobs() {
    try {
      jobs = await getJobDescriptions();
    } catch (e) {
      console.error('Failed to load job descriptions:', e);
    } finally {
      loading = false;
    }
  }

  async function handleLoad(id, rawTextPreview, title) {
    try {
      // Fetch full job description to get complete raw_text
      const job = await getJobDescription(id);
      onLoad(id, job.raw_text, title);
    } catch (e) {
      console.error('Failed to load job description:', e);
    }
  }

  function confirmDelete(id, resumeCount) {
    deleteId = id;
    deleteResumeCount = resumeCount;
  }

  async function handleDelete() {
    if (deleteId) {
      try {
        await deleteJobDescription(deleteId);
        jobs = jobs.filter(j => j.id !== deleteId);
      } catch (e) {
        console.error('Failed to delete job description:', e);
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
    <h3>Saved Job Descriptions</h3>
    <span class="collapse-toggle">{collapsed ? '[+]' : '[-]'}</span>
  </button>

  {#if !collapsed}
  <div class="saved-jobs-content">
    {#if loading}
      <div class="skeleton"></div>
      <div class="skeleton"></div>
      <div class="skeleton"></div>
    {:else if jobs.length === 0}
      <div class="empty-state">
        <p>No saved job descriptions yet.</p>
        <p class="hint">Paste a job description above and click "Save" to keep it for later.</p>
      </div>
    {:else}
      {#each jobs as job}
        <SavedJobItem
          {job}
          selected={selectedId === job.id}
          onLoad={handleLoad}
          onDelete={confirmDelete}
        />
      {/each}
    {/if}
  </div>
  {/if}
</div>

{#if deleteId}
<ConfirmDialog
  title="Delete Job Description?"
  message={`This will also delete ${deleteResumeCount} generated resume${deleteResumeCount !== 1 ? 's' : ''} linked to this job description. This action cannot be undone.`}
  onConfirm={handleDelete}
  onCancel={() => deleteId = null}
/>
{/if}
