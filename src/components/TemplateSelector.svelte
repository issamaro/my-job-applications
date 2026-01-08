<script>
  let { selected = $bindable('classic') } = $props();

  const templates = [
    { id: 'classic', name: 'Classic' },
    { id: 'modern', name: 'Modern' },
    { id: 'brussels', name: 'Brussels' },
    { id: 'eu_classic', name: 'EU Classic' }
  ];
</script>

<div class="template-selector">
  <label for="template-select" class="template-label">Template</label>
  <select
    id="template-select"
    bind:value={selected}
    class="template-dropdown"
    aria-label="Resume template"
  >
    {#each templates as template}
      <option value={template.id}>{template.name}</option>
    {/each}
  </select>
</div>

<style>
  .template-selector {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .template-label {
    font-size: 14px;
    color: #333;
  }

  .template-dropdown {
    padding: 8px 32px 8px 12px;
    font-size: 14px;
    font-family: inherit;
    background: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 2px;
    cursor: pointer;
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23333' d='M2 4l4 4 4-4'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 10px center;
  }

  .template-dropdown:hover {
    border-color: #0066cc;
  }

  .template-dropdown:focus {
    outline: 2px solid #0066cc;
    outline-offset: 2px;
  }
</style>
