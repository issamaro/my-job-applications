<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->
<!-- Scope: Resume language picker — labelled select for en/fr/nl. -->

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
    gap: 8px;
  }

  label {
    font-family: var(--font-ui);
    font-size: 13px;
    font-weight: 500;
    color: var(--ink-3);
  }

  select {
    padding: 6px 10px;
    border: 1px solid var(--rule);
    border-radius: var(--r-sm);
    background-color: var(--paper);
    color: var(--ink);
    font-family: var(--font-ui);
    font-size: 13px;
    cursor: pointer;
  }

  select:focus {
    outline: none;
    border-color: var(--ink);
  }

  select:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }
</style>
