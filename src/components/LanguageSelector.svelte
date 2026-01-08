<script>
  let { value = 'en', onchange } = $props();

  const languages = [
    { code: 'en', label: 'English' },
    { code: 'fr', label: 'Français' },
    { code: 'nl', label: 'Nederlands' }
  ];

  function handleChange(event) {
    const newValue = event.target.value;
    if (onchange) {
      onchange(newValue);
    }
  }
</script>

<div class="language-selector">
  <label for="language-select">Language</label>
  <select id="language-select" bind:value onchange={handleChange}>
    {#each languages as lang}
      <option value={lang.code}>{lang.label}</option>
    {/each}
  </select>
</div>

<style>
  .language-selector {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  label {
    font-size: 0.875rem;
    color: var(--color-text-secondary, #6b7280);
  }

  select {
    padding: 0.375rem 0.75rem;
    border: 1px solid var(--color-border, #d1d5db);
    border-radius: 0.375rem;
    background-color: var(--color-bg, #fff);
    color: var(--color-text, #111827);
    font-size: 0.875rem;
    cursor: pointer;
  }

  select:focus {
    outline: none;
    border-color: var(--color-primary, #3b82f6);
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
  }
</style>
