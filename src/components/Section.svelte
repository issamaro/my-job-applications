<script>
  let { title, onAdd = null, children } = $props();
  let expanded = $state(true);

  function toggle() {
    expanded = !expanded;
  }
</script>

<section class="section">
  <div
    class="section-header"
    onclick={toggle}
    onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); } }}
    role="button"
    tabindex="0"
    aria-expanded={expanded}
  >
    <h2 class="section-title">{title}</h2>
    <div class="section-actions">
      {#if onAdd}
        <button
          class="btn btn-add"
          onclick={(e) => { e.stopPropagation(); onAdd(); }}
          onkeydown={(e) => e.stopPropagation()}
          aria-label="Add {title}"
        >
          + Add
        </button>
      {/if}
      <span aria-hidden="true">{expanded ? '▼' : '▶'}</span>
    </div>
  </div>
  <div class="section-content" class:collapsed={!expanded}>
    {@render children()}
  </div>
</section>

<style>
  .section {
    margin-bottom: var(--spacing-section);
    border: 1px solid var(--color-border);
    border-radius: 2px;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-grid);
    border-bottom: 1px solid var(--color-border);
    cursor: pointer;
    user-select: none;

    &:hover {
      background: rgb(0 0 0 / 0.02);
    }
  }

  .section-title {
    margin: 0;
    font-size: var(--font-size-heading);
  }

  .section-actions {
    display: flex;
    gap: var(--spacing-grid);
    align-items: center;
  }

  .section-content {
    padding: var(--spacing-grid);
  }

  .section-content.collapsed {
    display: none;
  }
</style>
