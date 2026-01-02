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
