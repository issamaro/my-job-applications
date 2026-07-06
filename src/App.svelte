<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->
<!-- Scope: App shell — mounts editorial Topbar and renders the active screen. -->

<script>
  import Topbar from './components/Topbar.svelte';
  import ProfileEditor from './components/ProfileEditor.svelte';
  import ResumeGenerator from './components/ResumeGenerator.svelte';

  let activeTab = $state('profile');

  function updateActiveTab(tab) {
    activeTab = tab;
  }

  $effect(() => {
    function updateTabFromEvent(e) {
      activeTab = e.detail;
    }
    window.addEventListener('switchTab', updateTabFromEvent);
    return () => window.removeEventListener('switchTab', updateTabFromEvent);
  });
</script>

<Topbar {activeTab} onTabChange={updateActiveTab} />

{#if activeTab === 'profile'}
  <ProfileEditor />
{:else if activeTab === 'resume'}
  <ResumeGenerator />
{/if}
