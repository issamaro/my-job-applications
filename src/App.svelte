<script>
  import Section from './components/Section.svelte';
  import PersonalInfo from './components/PersonalInfo.svelte';
  import WorkExperience from './components/WorkExperience.svelte';
  import Education from './components/Education.svelte';
  import Skills from './components/Skills.svelte';
  import Projects from './components/Projects.svelte';

  let workExperienceRef = $state(null);
  let educationRef = $state(null);
  let skillsRef = $state(null);
  let projectsRef = $state(null);
</script>

<div class="container">
  <header class="header">
    <h1>MyCV</h1>
  </header>

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
</div>
