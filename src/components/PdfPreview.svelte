<script>
  let { resumeData, template = 'classic' } = $props();

  function formatWorkDate(dateStr) {
    if (!dateStr) return 'Present';
    const [year, month] = dateStr.split('-');
    const date = new Date(parseInt(year), parseInt(month) - 1);
    return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
  }

  let includedWork = $derived(
    (resumeData?.work_experiences || []).filter(exp => exp.included !== false)
  );
  let includedSkills = $derived(
    (resumeData?.skills || []).filter(skill => skill.included !== false)
  );
  let includedEducation = $derived(
    (resumeData?.education || []).filter(edu => edu.included !== false)
  );
  let includedProjects = $derived(
    (resumeData?.projects || []).filter(proj => proj.included === true)
  );
  let includedLanguages = $derived(
    (resumeData?.languages || []).filter(lang => lang.included !== false)
  );
</script>

<div class="pdf-preview template-{template}">
  {#if resumeData}
    <header>
      <h1 class="name">{resumeData.personal_info?.full_name || ''}</h1>
      <p class="contact">
        {resumeData.personal_info?.email || ''}
        {#if resumeData.personal_info?.phone} | {resumeData.personal_info.phone}{/if}
      </p>
      {#if resumeData.personal_info?.location || resumeData.personal_info?.linkedin_url}
      <p class="contact">
        {resumeData.personal_info?.location || ''}
        {#if resumeData.personal_info?.linkedin_url} | {resumeData.personal_info.linkedin_url}{/if}
      </p>
      {/if}
    </header>

    {#if resumeData.summary}
    <section class="summary">
      <h2>Professional Summary</h2>
      <p>{resumeData.summary}</p>
    </section>
    {/if}

    {#if includedWork.length > 0}
    <section class="experience">
      <h2>Experience</h2>
      {#each includedWork as exp}
      <div class="job">
        <div class="job-header">
          <span class="job-title">{exp.title}</span>
          <span class="job-company">{template === 'classic' ? '|' : 'at'} {exp.company}</span>
          <span class="job-dates">{formatWorkDate(exp.start_date)} - {formatWorkDate(exp.end_date)}</span>
        </div>
        {#if exp.description}
        <p class="job-description">{exp.description}</p>
        {/if}
      </div>
      {/each}
    </section>
    {/if}

    {#if includedSkills.length > 0}
    <section class="skills">
      <h2>Skills</h2>
      {#if template === 'modern'}
      <div class="skills-list">
        {#each includedSkills as skill}
        <span class="skill-item">{skill.name}</span>
        {/each}
      </div>
      {:else}
      <p>{includedSkills.map(s => s.name).join(', ')}</p>
      {/if}
    </section>
    {/if}

    {#if includedEducation.length > 0}
    <section class="education">
      <h2>Education</h2>
      {#each includedEducation as edu}
      <p>
        {#if template === 'modern'}
          <strong>{edu.degree}{edu.field_of_study ? ` in ${edu.field_of_study}` : ''}</strong>
        {:else}
          {edu.degree}{edu.field_of_study ? ` in ${edu.field_of_study}` : ''}
        {/if}
        | {edu.institution}
        {#if edu.graduation_year}| {edu.graduation_year}{/if}
      </p>
      {/each}
    </section>
    {/if}

    {#if includedLanguages.length > 0}
    <section class="languages">
      <h2>Languages</h2>
      <p>{includedLanguages.map(l => `${l.name} - ${l.level}`).join(', ')}</p>
    </section>
    {/if}

    {#if includedProjects.length > 0}
    <section class="projects">
      <h2>Projects</h2>
      {#each includedProjects as project}
      <div class="project">
        <p class="project-name">{project.name}</p>
        {#if project.description}<p>{project.description}</p>{/if}
        {#if project.technologies}<p class="technologies">{template === 'modern' ? 'Technologies: ' : ''}{project.technologies}</p>{/if}
      </div>
      {/each}
    </section>
    {/if}
  {/if}
</div>

<style>
  .pdf-preview {
    background: #fff;
    border: 1px solid #e0e0e0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 48px;
    max-width: 8.5in;
    margin: 0 auto;
  }

  /* Classic Template */
  .template-classic {
    font-family: Georgia, "Times New Roman", serif;
    font-size: 11pt;
  }

  .template-classic header {
    text-align: center;
    margin-bottom: 16pt;
  }

  .template-classic .name {
    font-size: 18pt;
    text-transform: uppercase;
    letter-spacing: 1pt;
    margin: 0 0 4pt;
  }

  .template-classic .contact {
    font-size: 10pt;
    color: #333;
    margin: 0 0 2pt;
  }

  .template-classic section {
    margin-bottom: 12pt;
  }

  .template-classic h2 {
    font-size: 12pt;
    text-transform: uppercase;
    letter-spacing: 0.5pt;
    border-bottom: 1px solid #1a1a1a;
    padding-bottom: 2pt;
    margin: 0 0 8pt;
  }

  .template-classic .job {
    margin-bottom: 10pt;
  }

  .template-classic .job-header {
    display: flex;
    flex-wrap: wrap;
    gap: 4pt;
    margin-bottom: 4pt;
  }

  .template-classic .job-title {
    font-weight: bold;
  }

  .template-classic .job-company {
    font-style: italic;
  }

  .template-classic .job-dates {
    margin-left: auto;
    font-size: 10pt;
    color: #333;
  }

  .template-classic .job-description {
    font-size: 10pt;
    white-space: pre-wrap;
    margin: 0;
  }

  .template-classic .skills p,
  .template-classic .education p,
  .template-classic .languages p {
    font-size: 10pt;
    margin: 0 0 4pt;
  }

  .template-classic .project {
    margin-bottom: 8pt;
  }

  .template-classic .project-name {
    font-weight: bold;
    font-size: 10pt;
    margin: 0 0 2pt;
  }

  .template-classic .project p {
    font-size: 10pt;
    margin: 0 0 2pt;
  }

  .template-classic .technologies {
    font-style: italic;
    color: #333;
  }

  /* Modern Template */
  .template-modern {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 10pt;
  }

  .template-modern header {
    text-align: left;
    margin-bottom: 16pt;
    border-bottom: 2px solid #0066cc;
    padding-bottom: 8pt;
  }

  .template-modern .name {
    font-size: 20pt;
    font-weight: bold;
    color: #0066cc;
    margin: 0 0 4pt;
  }

  .template-modern .contact {
    font-size: 9pt;
    color: #333;
    margin: 0 0 2pt;
  }

  .template-modern section {
    margin-bottom: 12pt;
  }

  .template-modern h2 {
    font-size: 11pt;
    font-weight: bold;
    color: #0066cc;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 2pt;
    margin: 0 0 8pt;
  }

  .template-modern .job {
    margin-bottom: 10pt;
  }

  .template-modern .job-header {
    display: flex;
    flex-wrap: wrap;
    gap: 4pt;
    margin-bottom: 4pt;
  }

  .template-modern .job-title {
    font-weight: bold;
  }

  .template-modern .job-company {
    color: #333;
  }

  .template-modern .job-dates {
    margin-left: auto;
    font-size: 9pt;
    color: #666;
  }

  .template-modern .job-description {
    font-size: 9pt;
    white-space: pre-wrap;
    margin: 0;
  }

  .template-modern .skills-list {
    display: flex;
    flex-wrap: wrap;
    gap: 6pt;
  }

  .template-modern .skill-item {
    display: inline-block;
    padding: 2pt 6pt;
    background: #f0f0f0;
    border-radius: 2pt;
    font-size: 9pt;
  }

  .template-modern .education p,
  .template-modern .languages p {
    font-size: 9pt;
    margin: 0 0 4pt;
  }

  .template-modern .project {
    margin-bottom: 8pt;
  }

  .template-modern .project-name {
    font-weight: bold;
    font-size: 9pt;
    margin: 0 0 2pt;
  }

  .template-modern .project p {
    font-size: 9pt;
    margin: 0 0 2pt;
  }

  .template-modern .technologies {
    color: #666;
  }
</style>
