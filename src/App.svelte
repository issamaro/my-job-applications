<script>
  import TabNav from './components/TabNav.svelte';
  import ProfileEditor from './components/ProfileEditor.svelte';
  import ResumeGenerator from './components/ResumeGenerator.svelte';

  let activeTab = $state('profile');

  function handleTabChange(tab) {
    activeTab = tab;
  }

  $effect(() => {
    function handleSwitchTab(e) {
      activeTab = e.detail;
    }
    window.addEventListener('switchTab', handleSwitchTab);
    return () => window.removeEventListener('switchTab', handleSwitchTab);
  });
</script>

<div class="container">
  <header class="header">
    <h1>MyCV</h1>
    <TabNav {activeTab} onTabChange={handleTabChange} />
  </header>

  {#if activeTab === 'profile'}
    <ProfileEditor />
  {:else if activeTab === 'resume'}
    <ResumeGenerator />
  {/if}
</div>
