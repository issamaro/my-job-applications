<script>
  let { message = "Are you sure?", onConfirm, onCancel } = $props();
  let dialogRef = $state(null);

  $effect(() => {
    if (dialogRef) {
      dialogRef.focus();
    }
  });

  function handleKeydown(e) {
    if (e.key === 'Escape') {
      onCancel();
    }
  }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<div
  class="dialog-backdrop"
  onclick={onCancel}
  onkeydown={handleKeydown}
  role="presentation"
>
  <div
    class="dialog"
    onclick={(e) => e.stopPropagation()}
    onkeydown={(e) => e.stopPropagation()}
    bind:this={dialogRef}
    tabindex="-1"
    role="dialog"
    aria-modal="true"
    aria-labelledby="dialog-title"
  >
    <h3 id="dialog-title" class="dialog-title">{message}</h3>
    <div class="dialog-actions">
      <button class="btn" onclick={onCancel}>Cancel</button>
      <button class="btn btn-primary" onclick={onConfirm}>Delete</button>
    </div>
  </div>
</div>

<style>
  .dialog-backdrop {
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: oklch(0 0 0 / 0.5);
    z-index: 1000;
  }

  .dialog {
    min-width: 320px;
    max-width: 440px;
    padding: 24px 28px;
    background: var(--paper);
    color: var(--ink);
    border: 1px solid var(--rule);
    border-radius: var(--r-md);
    box-shadow: 0 12px 36px oklch(0 0 0 / 0.18);
  }

  .dialog:focus {
    outline: 1px solid var(--accent);
    outline-offset: 2px;
  }

  .dialog-title {
    margin: 0 0 18px;
    font-size: 16px;
    font-weight: 600;
    line-height: 1.4;
    color: var(--ink);
  }

  .dialog-actions {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
    margin-top: 20px;
  }
</style>
