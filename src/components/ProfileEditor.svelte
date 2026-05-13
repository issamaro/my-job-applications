<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->
<!-- Scope: Editorial profile editor shell — header, seven numbered sections, import modal, toast. -->

<script>
  import EditorialSection from './EditorialSection.svelte';
  import UserProfile from './UserProfile.svelte';
  import WorkExperience from './WorkExperience.svelte';
  import Education from './Education.svelte';
  import Skills from './Skills.svelte';
  import Projects from './Projects.svelte';
  import Languages from './Languages.svelte';
  import ImportModal from './ImportModal.svelte';
  import Toast from './Toast.svelte';
  import { store, writeProfile } from '../lib/profileStore.svelte.js';

  let workExperienceRef = $state(null);
  let educationRef = $state(null);
  let skillsRef = $state(null);
  let languagesRef = $state(null);
  let projectsRef = $state(null);
  let importModalOpen = $state(false);
  let importButtonRef = $state(null);
  let toastMessage = $state(null);
  let workExperienceCount = $state(0);
  let educationCount = $state(0);
  let skillsCount = $state(0);
  let languagesCount = $state(0);
  let projectsCount = $state(0);
  let summaryTimeout = null;

  function handleImportSuccess() {
    toastMessage = 'Profile imported successfully';
  }

  function handleImportClose() {
    importButtonRef?.focus();
  }

  function handleSummaryBlur() {
    if (summaryTimeout) clearTimeout(summaryTimeout);
    summaryTimeout = setTimeout(() => { void writeProfile(); }, 500);
  }
</script>

<Toast bind:message={toastMessage} type="success" />

<ImportModal
  bind:open={importModalOpen}
  onSuccess={handleImportSuccess}
  onClose={handleImportClose}
/>

<main class="editor-main">
  <div class="editor-column">
    <header class="editor-header">
      <div>
        <div class="eyebrow">Workspace · profile</div>
        <h1 class="display editor-title">Your <span class="serif-italic">source of truth</span>.</h1>
        <p class="editor-sub">The single profile every tailored CV draws from. Edit once, ship anywhere.</p>
      </div>
      <div class="profile-header">
        <button
          class="btn"
          onclick={() => importModalOpen = true}
          bind:this={importButtonRef}
        >
          Import JSON
        </button>
      </div>
    </header>

    <div class="editor-sections">
      <EditorialSection number="01" title="Identity">
        <UserProfile />
      </EditorialSection>

      <EditorialSection number="02" title="Summary">
        <div class="form-row">
          <label for="summary" class="eyebrow">Summary</label>
          <textarea
            id="summary"
            class="textarea"
            bind:value={store.profile.summary}
            onblur={handleSummaryBlur}
          ></textarea>
        </div>
      </EditorialSection>

      <EditorialSection number="03" title="Experience" count={workExperienceCount}>
        <WorkExperience bind:this={workExperienceRef} bind:count={workExperienceCount} />
      </EditorialSection>

      <EditorialSection number="04" title="Education" count={educationCount}>
        <Education bind:this={educationRef} bind:count={educationCount} />
      </EditorialSection>

      <EditorialSection number="05" title="Skills" count={skillsCount}>
        <Skills bind:this={skillsRef} bind:count={skillsCount} />
      </EditorialSection>

      <EditorialSection number="06" title="Languages" count={languagesCount}>
        <Languages bind:this={languagesRef} bind:count={languagesCount} />
      </EditorialSection>

      <EditorialSection number="07" title="Projects" count={projectsCount}>
        <Projects bind:this={projectsRef} bind:count={projectsCount} />
      </EditorialSection>
    </div>
  </div>
</main>

<style>
  .editor-main {
    padding: var(--d-pad) 0;
    background: var(--paper);
  }
  .editor-column {
    max-width: 940px;
    margin: 0 auto;
    padding: 0 36px;
  }
  .editor-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    margin-bottom: 28px;
  }
  .editor-title {
    font-size: 44px;
    margin: 0;
  }
  .editor-sub {
    margin-top: 8px;
    color: var(--ink-3);
    font-size: 13px;
    max-width: 520px;
  }
  .editor-sections {
    display: flex;
    flex-direction: column;
    gap: 36px;
  }
</style>
