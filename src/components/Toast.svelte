<script>
  let { message = $bindable(null), type = 'success' } = $props();

  let visible = $state(false);

  $effect(() => {
    if (message) {
      visible = true;
      const timer = setTimeout(() => {
        visible = false;
        message = null;
      }, 3000);
      return () => clearTimeout(timer);
    }
  });
</script>

{#if visible && message}
<div class="toast toast-{type}" role="status" aria-live="polite">
  {message}
</div>
{/if}

<style>
  .toast {
    position: fixed;
    bottom: 24px;
    right: 24px;
    padding: 12px 16px;
    border-radius: 2px;
    font-size: 14px;
    z-index: 1000;
    animation: slideIn 0.2s ease-out;
  }

  .toast-success {
    color: #008800;
    background: rgba(0, 136, 0, 0.1);
    border: 1px solid rgba(0, 136, 0, 0.3);
  }

  .toast-error {
    color: #cc0000;
    background: rgba(204, 0, 0, 0.1);
    border: 1px solid rgba(204, 0, 0, 0.3);
  }

  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
</style>
