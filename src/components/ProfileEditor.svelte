<script>
  import Section from './Section.svelte';
  import PersonalInfo from './PersonalInfo.svelte';
  import WorkExperience from './WorkExperience.svelte';
  import Education from './Education.svelte';
  import Skills from './Skills.svelte';
  import Projects from './Projects.svelte';

  let workExperienceRef = $state(null);
  let educationRef = $state(null);
  let skillsRef = $state(null);
  let projectsRef = $state(null);
</script>

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

<Section title="Projects" onAdd={() => projectsRef?.add()}>
  <Projects bind:this={projectsRef} />
</Section>
