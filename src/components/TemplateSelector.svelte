<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->
<!-- Scope: Vertical stack of TemplateCard buttons bound to the resume's selected template. -->

<script>
  let { selected = $bindable('classic') } = $props();

  const templates = [
    { id: 'classic',    name: 'Classic',    sub: 'Serif · centered' },
    { id: 'modern',     name: 'Modern',     sub: 'Sans · accent rule' },
    { id: 'brussels',   name: 'Brussels',   sub: 'Two-column · photo' },
    { id: 'eu_classic', name: 'EU Classic', sub: 'Serif · header bar' }
  ];

  function updateSelected(id) {
    selected = id;
  }
</script>

<div class="template-stack" role="group" aria-label="Resume template">
  {#each templates as template (template.id)}
    {@const isActive = template.id === selected}
    <button
      type="button"
      class="template-card"
      class:template-card-active={isActive}
      aria-pressed={isActive}
      onclick={() => updateSelected(template.id)}
    >
      <div class="template-card-mini" aria-hidden="true">
        <span class="template-card-mini-bar template-card-mini-bar-name"></span>
        <span class="template-card-mini-bar template-card-mini-bar-sub"></span>
        <span class="template-card-mini-bar template-card-mini-bar-body"></span>
        <span class="template-card-mini-bar template-card-mini-bar-body"></span>
        <span class="template-card-mini-bar template-card-mini-bar-body"></span>
      </div>
      <div class="template-card-row">
        <span class="template-card-name">{template.name}</span>
        {#if isActive}
          <span class="num template-card-active-mark">● active</span>
        {/if}
      </div>
      <span class="template-card-sub">{template.sub}</span>
    </button>
  {/each}
</div>

<style>
  .template-stack {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .template-card {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 12px;
    background: var(--paper-2);
    border: 1px solid var(--rule);
    border-radius: var(--r-sm);
    cursor: pointer;
    text-align: left;
    font-family: inherit;
    width: 100%;
    transition: border-color .15s, background .15s;
  }

  .template-card:hover:not(.template-card-active) {
    border-color: var(--ink-3);
  }

  .template-card-active {
    background: var(--card);
    border-color: var(--ink);
  }

  .template-card:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }

  .template-card-mini {
    display: flex;
    flex-direction: column;
    gap: 6px;
    height: 90px;
    padding: 12px 10px;
    background: var(--card);
    border: 1px solid var(--rule-soft);
    border-radius: var(--r-sm);
    align-items: center;
    justify-content: flex-start;
  }

  .template-card-mini-bar {
    display: block;
    height: 4px;
    border-radius: 1px;
    background: var(--rule-soft);
  }

  .template-card-mini-bar-name {
    width: 60%;
    height: 6px;
    background: var(--ink);
  }

  .template-card-mini-bar-sub {
    width: 40%;
    background: var(--ink-3);
  }

  .template-card-mini-bar-body {
    width: 80%;
  }

  .template-card-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 8px;
  }

  .template-card-name {
    font-size: 12px;
    font-weight: 600;
    color: var(--ink);
  }

  .template-card-active-mark {
    color: var(--accent);
    font-size: 10px;
  }

  .template-card-sub {
    font-size: 10px;
    color: var(--ink-3);
  }
</style>
