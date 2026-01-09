<script>
  let { activeTab = 'profile', onTabChange } = $props();
</script>

<div class="tab-nav" role="tablist">
  <button
    class="tab-btn"
    class:active={activeTab === 'profile'}
    role="tab"
    aria-selected={activeTab === 'profile'}
    onclick={() => onTabChange('profile')}
  >
    Profile
  </button>
  <button
    class="tab-btn"
    class:active={activeTab === 'resume'}
    role="tab"
    aria-selected={activeTab === 'resume'}
    onclick={() => onTabChange('resume')}
  >
    Resume Generator
  </button>
</div>

<style>
  .tab-nav {
    display: flex;
    gap: var(--spacing-grid);
  }

  .tab-btn {
    padding: 8px var(--spacing-grid);
    font-size: var(--font-size-body);
    font-family: inherit;
    color: var(--color-text);
    background: none;
    border: none;
    cursor: pointer;
    border-bottom: 2px solid transparent;

    &:hover {
      color: var(--color-primary);
    }

    &:focus {
      outline: 2px solid var(--color-primary);
      outline-offset: 2px;
    }

    &.active {
      border-bottom-color: var(--color-primary);
      color: var(--color-primary);
    }
  }
</style>
