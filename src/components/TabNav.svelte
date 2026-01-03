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
