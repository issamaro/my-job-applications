<script>
  let { status = 'Analyzing job description...' } = $props();
</script>

<div class="progress-container" role="status" aria-live="polite">
  <p class="progress-status">{status}</p>
  <div class="progress-bar">
    <div class="progress-bar-fill"></div>
  </div>
</div>
