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
