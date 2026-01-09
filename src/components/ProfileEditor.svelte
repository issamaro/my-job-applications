<script>
  import Section from './Section.svelte';
  import PersonalInfo from './PersonalInfo.svelte';
  import WorkExperience from './WorkExperience.svelte';
  import Education from './Education.svelte';
  import Skills from './Skills.svelte';
  import Projects from './Projects.svelte';
  import Languages from './Languages.svelte';
  import ImportModal from './ImportModal.svelte';
  import Toast from './Toast.svelte';

  let workExperienceRef = $state(null);
  let educationRef = $state(null);
  let skillsRef = $state(null);
  let projectsRef = $state(null);
  let languagesRef = $state(null);
  let importModalOpen = $state(false);
  let importButtonRef = $state(null);
  let toastMessage = $state(null);

  function handleImportSuccess() {
    toastMessage = 'Profile imported successfully';
  }

  function handleImportClose() {
    importButtonRef?.focus();
  }
</script>

<div class="profile-header">
  <button
    class="btn"
    onclick={() => importModalOpen = true}
    bind:this={importButtonRef}
  >
    Import JSON
  </button>
</div>

<ImportModal
  bind:open={importModalOpen}
  onSuccess={handleImportSuccess}
  onClose={handleImportClose}
/>

<Toast bind:message={toastMessage} type="success" />

<Section title="Personal Info">
  <PersonalInfo />
</Section>

<Section title="Work Experience" onAdd={() => workExperienceRef?.add()}>
  <WorkExperience bind:this={workExperienceRef} />
</Section>

<Section title="Education" onAdd={() => educationRef?.add()}>
  <Education bind:this={educationRef} />
</Section>

<Section title="Skills" onAdd={() => skillsRef?.add()}>
  <Skills bind:this={skillsRef} />
</Section>

<Section title="Languages" onAdd={() => languagesRef?.add()}>
  <Languages bind:this={languagesRef} />
</Section>

<Section title="Projects" onAdd={() => projectsRef?.add()}>
  <Projects bind:this={projectsRef} />
</Section>

<style>
  .profile-header {
    display: flex;
    justify-content: flex-end;
    margin-bottom: var(--spacing-grid);
  }
</style>
