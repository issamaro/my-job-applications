<script>
  let { title, included = true, onToggle, children } = $props();

  let collapsed = $state(false);
</script>

<div class="resume-section">
  <div class="resume-section-header">
    <button
      class="section-title-btn"
      onclick={() => collapsed = !collapsed}
      aria-expanded={!collapsed}
    >
      <h4>{title}</h4>
      <span class="collapse-toggle">{collapsed ? '[+]' : '[-]'}</span>
    </button>

    {#if onToggle}
    <button
      class="toggle-btn"
      class:on={included}
      class:off={!included}
      aria-pressed={included}
      onclick={onToggle}
    >
      [{included ? 'ON' : 'OFF'}]
    </button>
    {/if}
  </div>

  {#if !collapsed}
  <div class="resume-section-content">
    {#if included}
      {@render children()}
    {:else}
      <p class="section-hidden">(Section hidden from resume)</p>
    {/if}
  </div>
  {/if}
</div>

<style>
  .resume-section {
    margin-bottom: var(--spacing-grid);
    border: 1px solid var(--color-border);
    border-radius: 2px;
  }

  .resume-section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-grid);
    border-bottom: 1px solid var(--color-border);
  }

  .section-title-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    background: none;
    border: none;
    cursor: pointer;
    font-family: inherit;

    h4 {
      margin: 0;
    }

    &:hover {
      color: var(--color-primary);
    }

    &:focus {
      outline: 2px solid var(--color-primary);
      outline-offset: 2px;
    }
  }

  .collapse-toggle {
    font-family: monospace;
    color: rgb(var(--color-text-rgb) / 0.6);
  }

  .toggle-btn {
    padding: 4px 8px;
    font-size: 14px;
    font-family: monospace;
    background: none;
    border: 1px solid var(--color-border);
    border-radius: 2px;
    cursor: pointer;

    &.on {
      color: var(--color-success);
      border-color: rgb(var(--color-success-rgb) / 0.3);
    }

    &.off {
      color: rgb(var(--color-text-rgb) / 0.5);
    }

    &:hover {
      background: rgb(0 0 0 / 0.02);
    }

    &:focus {
      outline: 2px solid var(--color-primary);
      outline-offset: 2px;
    }
  }

  .resume-section-content {
    padding: var(--spacing-grid);
  }

  .section-hidden {
    color: rgb(var(--color-text-rgb) / 0.5);
    font-style: italic;
  }
</style>
