<script>
  import { importProfile } from '../lib/api.js';

  let { open = $bindable(false), onSuccess = () => {}, onClose = () => {} } = $props();

  let state = $state('initial'); // initial, validating, preview, error, importing
  let fileInput = $state(null);
  let dropZoneRef = $state(null);
  let dialogRef = $state(null);
  let errors = $state([]);
  let profileData = $state(null);
  let counts = $state(null);
  let isDragging = $state(false);

  function validateProfileJson(data) {
    const errs = [];

    // Required sections
    if (!data.personal_info) {
      errs.push('Missing required section: personal_info');
    }

    // Required fields in personal_info
    if (data.personal_info) {
      if (!data.personal_info.full_name) {
        errs.push('Missing required field: personal_info.full_name');
      }
      if (!data.personal_info.email) {
        errs.push('Missing required field: personal_info.email');
      }
    }

    // Array sections should be arrays
    ['work_experiences', 'education', 'skills', 'projects'].forEach(section => {
      if (data[section] !== undefined && !Array.isArray(data[section])) {
        errs.push(`${section} must be an array`);
      }
    });

    // Required fields in work_experiences
    if (Array.isArray(data.work_experiences)) {
      data.work_experiences.forEach((item, i) => {
        if (!item.company) errs.push(`Missing required field: work_experiences[${i}].company`);
        if (!item.title) errs.push(`Missing required field: work_experiences[${i}].title`);
        if (!item.start_date) errs.push(`Missing required field: work_experiences[${i}].start_date`);
      });
    }

    // Required fields in education
    if (Array.isArray(data.education)) {
      data.education.forEach((item, i) => {
        if (!item.institution) errs.push(`Missing required field: education[${i}].institution`);
        if (!item.degree) errs.push(`Missing required field: education[${i}].degree`);
      });
    }

    // Required fields in skills
    if (Array.isArray(data.skills)) {
      data.skills.forEach((item, i) => {
        if (!item.name) errs.push(`Missing required field: skills[${i}].name`);
      });
    }

    // Required fields in projects
    if (Array.isArray(data.projects)) {
      data.projects.forEach((item, i) => {
        if (!item.name) errs.push(`Missing required field: projects[${i}].name`);
      });
    }

    // Type validations
    if (Array.isArray(data.education)) {
      data.education.forEach((item, i) => {
        if (item.graduation_year !== undefined && item.graduation_year !== null && typeof item.graduation_year !== 'number') {
          errs.push(`Invalid type: education[${i}].graduation_year must be a number`);
        }
      });
    }

    return errs.slice(0, 5); // Return first 5 errors
  }

  function countItems(data) {
    return {
      work_experiences: data.work_experiences?.length || 0,
      education: data.education?.length || 0,
      skills: data.skills?.length || 0,
      projects: data.projects?.length || 0
    };
  }

  async function handleFile(file) {
    if (!file) return;

    state = 'validating';
    errors = [];
    profileData = null;

    try {
      const text = await file.text();
      let data;

      try {
        data = JSON.parse(text);
      } catch (parseError) {
        errors = [`Invalid JSON: ${parseError.message}`];
        state = 'error';
        return;
      }

      const validationErrors = validateProfileJson(data);
      if (validationErrors.length > 0) {
        errors = validationErrors;
        state = 'error';
        return;
      }

      profileData = data;
      counts = countItems(data);
      state = 'preview';
    } catch (e) {
      errors = ['Could not read file. Please try again.'];
      state = 'error';
    }
  }

  function handleFileSelect(event) {
    const file = event.target.files?.[0];
    if (file) {
      handleFile(file);
    }
  }

  function handleDrop(event) {
    event.preventDefault();
    isDragging = false;
    const file = event.dataTransfer?.files?.[0];
    if (file && file.type === 'application/json') {
      handleFile(file);
    } else if (file) {
      errors = ['Please drop a JSON file'];
      state = 'error';
    }
  }

  function handleDragOver(event) {
    event.preventDefault();
    isDragging = true;
  }

  function handleDragLeave(event) {
    event.preventDefault();
    isDragging = false;
  }

  async function handleImport() {
    if (!profileData) return;

    state = 'importing';
    errors = [];

    try {
      await importProfile(profileData);
      onSuccess();
      closeModal();
      // Reload page after successful import
      setTimeout(() => window.location.reload(), 100);
    } catch (e) {
      errors = ['Import failed. Please try again.'];
      state = 'error';
    }
  }

  function closeModal() {
    open = false;
    state = 'initial';
    errors = [];
    profileData = null;
    counts = null;
    isDragging = false;
    onClose();
  }

  function handleBackdropClick(event) {
    if (event.target === event.currentTarget) {
      closeModal();
    }
  }

  function handleKeyDown(event) {
    if (event.key === 'Escape') {
      closeModal();
    }
  }

  function handleDropZoneKeyDown(event) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      fileInput?.click();
    }
  }

  function triggerFileInput() {
    fileInput?.click();
  }

  function resetToInitial() {
    state = 'initial';
    errors = [];
    profileData = null;
    counts = null;
  }

  $effect(() => {
    if (open && dialogRef) {
      dialogRef.focus();
    }
  });
</script>

{#if open}
<div
  class="dialog-backdrop"
  onclick={handleBackdropClick}
  onkeydown={handleKeyDown}
  role="presentation"
>
  <div
    class="dialog import-modal"
    role="dialog"
    aria-modal="true"
    aria-labelledby="import-modal-title"
    tabindex="-1"
    bind:this={dialogRef}
  >
    <div class="modal-header">
      <h2 id="import-modal-title" class="dialog-title">Import JSON Profile</h2>
      <button class="close-btn" onclick={closeModal} aria-label="Close">
        &times;
      </button>
    </div>

    {#if state === 'initial' || state === 'error'}
      <div
        class="drop-zone"
        class:dragging={isDragging}
        class:error={state === 'error'}
        ondrop={handleDrop}
        ondragover={handleDragOver}
        ondragleave={handleDragLeave}
        onclick={triggerFileInput}
        onkeydown={handleDropZoneKeyDown}
        role="button"
        tabindex="0"
        aria-label="Drop zone for JSON file upload"
        bind:this={dropZoneRef}
      >
        <input
          type="file"
          accept=".json"
          onchange={handleFileSelect}
          bind:this={fileInput}
          class="file-input"
          aria-hidden="true"
        />
        <p class="drop-text">Drag & drop your JSON file here or click to browse</p>
      </div>

      {#if state === 'error' && errors.length > 0}
        <div class="error-messages" aria-live="assertive">
          {#each errors as error}
            <p class="error-message">{error}</p>
          {/each}
        </div>
      {/if}

      <div class="sample-link">
        <a href="/sample-profile.json" download="sample-profile.json">
          Download Sample JSON
        </a>
      </div>
    {/if}

    {#if state === 'validating'}
      <div class="validating-state" aria-busy="true">
        <span class="spinner"></span>
        <p>Validating...</p>
      </div>
    {/if}

    {#if state === 'preview'}
      <div class="preview-state">
        <div class="preview-counts">
          <h3>Data to import:</h3>
          <ul>
            <li>Work Experiences: {counts.work_experiences}</li>
            <li>Education: {counts.education}</li>
            <li>Skills: {counts.skills}</li>
            <li>Projects: {counts.projects}</li>
          </ul>
        </div>
        <div class="warning-box">
          <p class="warning-text">This will replace all existing data.</p>
          <p class="photo-note">Your profile photo will be preserved.</p>
        </div>
      </div>
    {/if}

    {#if state === 'importing'}
      <div class="importing-state" aria-busy="true">
        <span class="spinner"></span>
        <p>Importing...</p>
      </div>
    {/if}

    <div class="dialog-actions">
      {#if state === 'preview'}
        <button class="btn" onclick={resetToInitial}>
          Back
        </button>
        <button class="btn btn-primary" onclick={handleImport}>
          Import
        </button>
      {:else if state === 'importing'}
        <button class="btn btn-primary" disabled>
          <span class="spinner-small"></span>
          Importing...
        </button>
      {:else}
        <button class="btn" onclick={closeModal}>
          Cancel
        </button>
      {/if}
    </div>
  </div>
</div>
{/if}
