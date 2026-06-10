<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->
<!-- Scope: Transient status toast — success and error variants, auto-dismiss. -->

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
    color: var(--positive);
    background: var(--positive-soft);
    border: 1px solid var(--positive);
  }

  .toast-error {
    color: var(--negative);
    background: var(--negative-soft);
    border: 1px solid var(--negative);
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
