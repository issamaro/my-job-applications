<script>
  let { value = '', disabled = false, error = null, onInput } = $props();

  let charCount = $derived(value.length);
  let isValid = $derived(charCount >= 100);
</script>

<div class="jd-input">
  <h2>Generate Tailored Resume</h2>
  <p class="instructions">
    Paste a job description below. We'll analyze it and create a resume highlighting your most relevant experience.
  </p>

  <div class="form-row">
    <label for="job-description" class="required">Job Description</label>
    <textarea
      id="job-description"
      placeholder="Paste job description here..."
      {disabled}
      class:dimmed={disabled}
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
</div>
