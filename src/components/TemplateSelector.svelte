<script>
  let { selected = $bindable('classic') } = $props();

  const templates = [
    { id: 'classic', name: 'Classic' },
    { id: 'modern', name: 'Modern' }
  ];
</script>

<div class="template-selector" role="radiogroup" aria-label="Resume template">
  {#each templates as template}
    <button
      type="button"
      class="template-btn"
      class:selected={selected === template.id}
      onclick={() => selected = template.id}
      role="radio"
      aria-checked={selected === template.id}
    >
      {template.name}
    </button>
  {/each}
</div>

<style>
  .template-selector {
    display: flex;
    gap: 8px;
  }

  .template-btn {
    padding: 8px 16px;
    font-size: 14px;
    font-family: inherit;
    background: transparent;
    border: 1px solid #e0e0e0;
    border-radius: 2px;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .template-btn:hover {
    border-color: #0066cc;
  }

  .template-btn:focus {
    outline: 2px solid #0066cc;
    outline-offset: 2px;
  }

  .template-btn.selected {
    color: #fff;
    background: #0066cc;
    border-color: #0066cc;
  }
</style>
