<script>
  let {
    value = '',
    disabled = false,
    error = null,
    saving = false,
    loadedJobId = null,
    loadedJobTitle = null,
    onInput,
    onSave,
    onClear
  } = $props();

  let charCount = $derived(value.length);
  let isValid = $derived(charCount >= 100);
</script>

<div class="jd-input">
  <h2>Generate Tailored Resume</h2>
  <p class="instructions">
    Paste a job description below. We'll analyze it and create a resume highlighting your most relevant experience.
  </p>

  {#if loadedJobId}
  <div class="loaded-indicator">
    <span class="loaded-badge">Editing: {loadedJobTitle}</span>
    <button class="clear-link" onclick={onClear}>Clear</button>
  </div>
  {/if}

  <div class="form-row">
    <label for="job-description" class="required">Job Description</label>
    <textarea
      id="job-description"
      placeholder="Paste job description here..."
      disabled={disabled || saving}
      class:dimmed={disabled || saving}
      class:error={error}
      aria-required="true"
      aria-describedby={error ? 'jd-error' : 'jd-counter'}
      oninput={(e) => onInput(e.target.value)}
    >{value}</textarea>

    <div class="jd-meta">
      <span id="jd-counter" class="char-counter" class:valid={isValid}>
        {charCount} / 100 minimum characters
      </span>
      {#if error}
        <span id="jd-error" class="error-message">{error}</span>
      {/if}
    </div>
  </div>

  <div class="button-row">
    <button
      class="btn"
      disabled={!isValid || disabled || saving}
      onclick={onSave}
    >
      {saving ? 'Saving...' : 'Save'}
    </button>
  </div>
</div>

<style>
  .jd-input {
    h2 {
      margin-bottom: var(--spacing-grid);
    }

    .instructions {
      color: rgb(var(--color-text-rgb) / 0.7);
      margin-bottom: var(--spacing-section);
    }

    textarea {
      min-height: 200px;

      &.dimmed {
        opacity: 0.6;
        background: rgb(0 0 0 / 0.02);
      }
    }
  }

  .jd-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 4px;
  }

  .char-counter {
    font-size: 14px;
    color: rgb(var(--color-text-rgb) / 0.6);

    &.valid {
      color: var(--color-success);
    }
  }

  .loaded-indicator {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    margin-bottom: var(--spacing-grid);
    background: rgb(var(--color-primary-rgb) / 0.05);
    border-left: 3px solid var(--color-primary);
    border-radius: 2px;
  }

  .loaded-badge {
    font-size: 14px;
    color: var(--color-primary);
  }

  .clear-link {
    background: none;
    border: none;
    color: rgb(var(--color-text-rgb) / 0.6);
    cursor: pointer;
    font-size: 14px;

    &:hover {
      color: var(--color-text);
      text-decoration: underline;
    }

    &:focus {
      outline: 2px solid var(--color-primary);
      outline-offset: 2px;
    }
  }

  .button-row {
    display: flex;
    gap: var(--spacing-grid);
    margin-top: var(--spacing-grid);
  }
</style>
