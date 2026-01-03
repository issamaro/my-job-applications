<script>
  import ConfirmDialog from './ConfirmDialog.svelte';
  import { getResumes, deleteResume } from '../lib/api.js';

  let { onSelect } = $props();

  let history = $state([]);
  let loading = $state(true);
  let collapsed = $state(false);
  let deleteId = $state(null);

  $effect(() => {
    loadHistory();
  });

  async function loadHistory() {
    try {
      history = await getResumes();
    } catch (e) {
      console.error('Failed to load history:', e);
    } finally {
      loading = false;
    }
  }

  function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }

  async function handleDelete() {
    if (deleteId) {
      try {
        await deleteResume(deleteId);
        history = history.filter(h => h.id !== deleteId);
      } catch (e) {
        console.error('Failed to delete resume:', e);
      }
      deleteId = null;
    }
  }

  export function refresh() {
    loadHistory();
  }
</script>

<div class="history-section">
  <button
    class="history-header"
    onclick={() => collapsed = !collapsed}
    aria-expanded={!collapsed}
  >
    <h3>History</h3>
    <span class="collapse-toggle">{collapsed ? '[+]' : '[-]'}</span>
  </button>

  {#if !collapsed}
  <div class="history-content">
    {#if loading}
      <div class="skeleton"></div>
    {:else if history.length === 0}
      <p class="empty-state">No resumes generated yet.</p>
    {:else}
      <div class="history-list">
        {#each history as item}
          <div class="history-item">
            <button
              class="history-item-info"
              onclick={() => onSelect(item.id)}
            >
              <span class="history-title">
                {item.job_title || 'Untitled'} · {item.company_name || 'Unknown'}
              </span>
              <span class="history-meta">
                {formatDate(item.created_at)} · Match: {item.match_score?.toFixed(0) || 0}%
              </span>
            </button>
            <button
              class="delete-link"
              onclick={() => deleteId = item.id}
            >
              Delete
            </button>
          </div>
        {/each}
      </div>
    {/if}
  </div>
  {/if}
</div>

{#if deleteId}
<ConfirmDialog
  title="Delete Resume"
  message="Are you sure you want to delete this generated resume? This action cannot be undone."
  onConfirm={handleDelete}
  onCancel={() => deleteId = null}
/>
{/if}
