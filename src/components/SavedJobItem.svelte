<script>
  import { updateJobDescription } from '../lib/api.js';

  let { job, selected = false, onLoad, onDelete } = $props();

  let editing = $state(false);
  let editTitle = $state('');

  let preview = $derived(
    job.raw_text_preview.length > 200
      ? job.raw_text_preview.slice(0, 200) + '...'
      : job.raw_text_preview
  );

  function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }

  function startEdit(e) {
    e.stopPropagation();
    editTitle = job.title;
    editing = true;
  }

  async function saveTitle() {
    if (editTitle.trim() && editTitle !== job.title) {
      try {
        await updateJobDescription(job.id, { title: editTitle.trim() });
        job.title = editTitle.trim();
      } catch (e) {
        console.error('Failed to update title:', e);
      }
    }
    editing = false;
  }

  function cancelEdit() {
    editing = false;
  }

  function handleKeydown(e) {
    if (e.key === 'Enter') {
      saveTitle();
    } else if (e.key === 'Escape') {
      cancelEdit();
    }
  }
</script>

<div class="saved-job-item" class:selected>
  <div class="job-info">
    <div class="job-header">
      {#if editing}
        <!-- svelte-ignore a11y_autofocus -->
        <input
          type="text"
          bind:value={editTitle}
          onkeydown={handleKeydown}
          onblur={saveTitle}
          class="title-input"
          maxlength="100"
          autofocus
        />
        <button class="icon-btn" onclick={saveTitle} aria-label="Save title">OK</button>
      {:else}
        <button
          class="job-title-btn"
          onclick={() => onLoad(job.id, job.raw_text, job.title)}
          aria-label="{job.title}, {formatDate(job.updated_at)}, {job.resume_count} resumes. Click to load."
        >
          <span class="job-title">{job.title}</span>
        </button>
        <button class="icon-btn" onclick={startEdit} aria-label="Edit title">Edit</button>
      {/if}
    </div>
    <button
      class="job-content"
      onclick={() => onLoad(job.id, job.raw_text, job.title)}
    >
      <p class="job-preview">{preview}</p>
      <div class="job-meta">
        <span>{formatDate(job.updated_at)}</span>
        <span>{job.resume_count} resume{job.resume_count !== 1 ? 's' : ''}</span>
      </div>
    </button>
  </div>
  <button
    class="delete-link"
    onclick={() => onDelete(job.id, job.resume_count)}
    aria-label="Delete job description"
  >
    Delete
  </button>
</div>
