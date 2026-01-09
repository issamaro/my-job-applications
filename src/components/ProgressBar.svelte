<script>
  let { status = 'Analyzing job description...' } = $props();
</script>

<div class="progress-container" role="status" aria-live="polite">
  <p class="progress-status">{status}</p>
  <div class="progress-bar">
    <div class="progress-bar-fill"></div>
  </div>
</div>

<style>
  .progress-container {
    margin: var(--spacing-section) 0;
  }

  .progress-status {
    margin-bottom: 8px;
    font-size: 14px;
  }

  .progress-bar {
    height: 4px;
    background: var(--color-border);
    border-radius: 2px;
    overflow: hidden;
  }

  .progress-bar-fill {
    height: 100%;
    width: 100%;
    background: var(--color-primary);
    animation: progress 2s ease-in-out infinite;
  }
</style>
