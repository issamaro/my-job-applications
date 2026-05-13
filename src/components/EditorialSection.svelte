<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->
<!-- Scope: Numbered editorial section header — eyebrow, display title, optional count. -->

<script>
  let { number, title, count = null, children } = $props();
</script>

<section class="editorial-section">
  <div class="editorial-section-header">
    <span class="eyebrow num">№ {number}</span>
    <h2 class="display editorial-section-title">{title}</h2>
    {#if count != null}
      <span class="num editorial-section-count">{count}</span>
    {/if}
  </div>
  <div class="editorial-section-body">
    {@render children()}
  </div>
</section>

<style>
  .editorial-section {
    display: flex;
    flex-direction: column;
    gap: 14px;
  }
  .editorial-section-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
  }
  .editorial-section-title {
    font-size: 26px;
    margin: 0;
  }
  .editorial-section-count {
    font-size: 12px;
    color: var(--ink-3);
  }
</style>
