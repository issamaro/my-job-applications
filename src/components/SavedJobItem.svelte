<script>
  import { updateJobDescription, getJobDescriptionResumes, deleteResume } from '../lib/api.js';
  import ConfirmDialog from './ConfirmDialog.svelte';

  let { job, selected = false, autoExpand = false, onLoad, onDelete, onSelectResume } = $props();

  let editing = $state(false);
  let editTitle = $state('');
  let expanded = $state(false);
  let resumes = $state([]);
  let loadingResumes = $state(false);
  let resumesFetched = $state(false);
  let deleteResumeId = $state(null);
  let resumeError = $state(null);

  let preview = $derived(
    job.raw_text_preview.length > 200
      ? job.raw_text_preview.slice(0, 200) + '...'
      : job.raw_text_preview
  );

  $effect(() => {
    if (autoExpand && job.resume_count > 0 && !resumesFetched) {
      toggleExpand();
    }
  });

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

  async function toggleExpand(e) {
    if (e) e.stopPropagation();

    if (!expanded && !resumesFetched && job.resume_count > 0) {
      loadingResumes = true;
      resumeError = null;
      try {
        resumes = await getJobDescriptionResumes(job.id);
        resumesFetched = true;
      } catch (err) {
        console.error('Failed to load resumes:', err);
        resumeError = 'Could not load resumes';
      } finally {
        loadingResumes = false;
      }
    }
    expanded = !expanded;
  }

  function handleResumeClick(e, resumeId) {
    e.stopPropagation();
    onSelectResume?.(resumeId);
  }

  function confirmDeleteResume(e, resumeId) {
    e.stopPropagation();
    deleteResumeId = resumeId;
  }

  async function handleDeleteResume() {
    if (deleteResumeId) {
      try {
        await deleteResume(deleteResumeId);
        resumes = resumes.filter(r => r.id !== deleteResumeId);
        job.resume_count = Math.max(0, job.resume_count - 1);
      } catch (err) {
        console.error('Failed to delete resume:', err);
        resumeError = 'Could not delete resume. Please try again.';
      }
      deleteResumeId = null;
    }
  }

  export function refreshResumes() {
    resumesFetched = false;
    if (expanded) {
      toggleExpand();
    }
  }
</script>

<div class="saved-job-item" class:selected class:expanded>
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
    </button>
    <div class="job-meta">
      <span>{formatDate(job.updated_at)}</span>
      {#if job.resume_count > 0}
        <button
          class="expand-toggle"
          onclick={toggleExpand}
          aria-expanded={expanded}
          aria-controls="resume-list-{job.id}"
          aria-label="{expanded ? 'Collapse' : 'Expand'} {job.resume_count} resume{job.resume_count !== 1 ? 's' : ''}"
        >
          {#if loadingResumes}
            <span class="spinner-small"></span>
          {:else}
            {expanded ? '[^]' : '[v]'} {job.resume_count} resume{job.resume_count !== 1 ? 's' : ''}
          {/if}
        </button>
      {:else}
        <span class="resume-count-text">0 resumes</span>
      {/if}
    </div>
  </div>
  <button
    class="delete-link"
    onclick={() => onDelete(job.id, job.resume_count)}
    aria-label="Delete job description"
  >
    Delete
  </button>
</div>

{#if expanded && job.resume_count > 0}
  <div class="resume-list" id="resume-list-{job.id}" role="list" aria-busy={loadingResumes}>
    {#if resumeError}
      <p class="resume-error">{resumeError}</p>
    {:else if loadingResumes}
      <div class="skeleton resume-skeleton"></div>
      <div class="skeleton resume-skeleton"></div>
    {:else}
      {#each resumes as resume}
        <div class="resume-item" role="listitem">
          <button
            class="resume-info"
            onclick={(e) => handleResumeClick(e, resume.id)}
            aria-label="Load resume from {formatDate(resume.created_at)} with {resume.match_score}% match"
          >
            <span>Resume · {formatDate(resume.created_at)} · Match: {resume.match_score ?? 0}%</span>
          </button>
          <button
            class="delete-link"
            onclick={(e) => confirmDeleteResume(e, resume.id)}
            aria-label="Delete resume from {formatDate(resume.created_at)}"
          >
            Delete
          </button>
        </div>
      {/each}
    {/if}
  </div>
{/if}

{#if deleteResumeId}
<ConfirmDialog
  title="Delete Resume?"
  message="This generated resume will be permanently deleted. This cannot be undone."
  onConfirm={handleDeleteResume}
  onCancel={() => deleteResumeId = null}
/>
{/if}
