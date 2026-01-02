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
