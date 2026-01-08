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

  let isEuropeanTemplate = $derived(template === 'brussels' || template === 'eu_classic');
</script>

<div class="pdf-preview template-{template}">
  {#if resumeData}
    {#if template === 'brussels'}
      <!-- Brussels Template: Two-column with sidebar -->
      <aside class="sidebar">
        {#if resumeData.personal_info?.photo}
          <img src={resumeData.personal_info.photo} alt="Profile photo" class="profile-photo">
        {:else}
          <div class="photo-placeholder" role="img" aria-label="Photo placeholder">
            <svg viewBox="0 0 100 100" class="silhouette">
              <circle cx="50" cy="35" r="20" fill="#9CA3AF"/>
              <ellipse cx="50" cy="85" rx="35" ry="25" fill="#9CA3AF"/>
            </svg>
          </div>
        {/if}

        <div class="contact">
          <h3>Contact</h3>
          {#if resumeData.personal_info?.email}
            <p class="contact-item">{resumeData.personal_info.email}</p>
          {/if}
          {#if resumeData.personal_info?.phone}
            <p class="contact-item">{resumeData.personal_info.phone}</p>
          {/if}
          {#if resumeData.personal_info?.location}
            <p class="contact-item">{resumeData.personal_info.location}</p>
          {/if}
          {#if resumeData.personal_info?.linkedin_url}
            <p class="contact-item">{resumeData.personal_info.linkedin_url}</p>
          {/if}
        </div>

        {#if includedSkills.length > 0}
          <div class="skills">
            <h3>Skills</h3>
            <div class="skills-list">
              {#each includedSkills as skill}
                <span class="skill-item">{skill.name}</span>
              {/each}
            </div>
          </div>
        {/if}

        {#if includedLanguages.length > 0}
          <div class="languages">
            <h3>Languages</h3>
            {#each includedLanguages as lang}
              <p class="language-item">{lang.name} - {lang.level}</p>
            {/each}
          </div>
        {/if}
      </aside>

      <main class="main-content">
        <h1 class="name">{resumeData.personal_info?.full_name || ''}</h1>

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
                  <span class="job-company">at {exp.company}</span>
                  <span class="job-dates">{formatWorkDate(exp.start_date)} - {formatWorkDate(exp.end_date)}</span>
                </div>
                {#if exp.description}
                  <p class="job-description">{exp.description}</p>
                {/if}
              </div>
            {/each}
          </section>
        {/if}

        {#if includedEducation.length > 0}
          <section class="education">
            <h2>Education</h2>
            {#each includedEducation as edu}
              <p>
                <strong>{edu.degree}{edu.field_of_study ? ` in ${edu.field_of_study}` : ''}</strong>
                | {edu.institution}
                {#if edu.graduation_year}| {edu.graduation_year}{/if}
              </p>
            {/each}
          </section>
        {/if}

        {#if includedProjects.length > 0}
          <section class="projects">
            <h2>Projects</h2>
            {#each includedProjects as project}
              <div class="project">
                <p class="project-name">{project.name}</p>
                {#if project.description}<p>{project.description}</p>{/if}
                {#if project.technologies}<p class="technologies">Technologies: {project.technologies}</p>{/if}
              </div>
            {/each}
          </section>
        {/if}
      </main>

    {:else if template === 'eu_classic'}
      <!-- EU Classic Template: Single-column with header photo -->
      <header class="cv-header">
        <div class="header-content">
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
        </div>
        {#if resumeData.personal_info?.photo}
          <img src={resumeData.personal_info.photo} alt="Profile photo" class="profile-photo">
        {:else}
          <div class="photo-placeholder" role="img" aria-label="Photo placeholder">
            <svg viewBox="0 0 100 100" class="silhouette">
              <circle cx="50" cy="35" r="20" fill="#9CA3AF"/>
              <ellipse cx="50" cy="85" rx="35" ry="25" fill="#9CA3AF"/>
            </svg>
          </div>
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
                <span class="job-company">| {exp.company}</span>
                <span class="job-dates">{formatWorkDate(exp.start_date)} - {formatWorkDate(exp.end_date)}</span>
              </div>
              {#if exp.description}
                <p class="job-description">{exp.description}</p>
              {/if}
            </div>
          {/each}
        </section>
      {/if}

      {#if includedEducation.length > 0}
        <section class="education">
          <h2>Education</h2>
          {#each includedEducation as edu}
            <p>
              {edu.degree}{edu.field_of_study ? ` in ${edu.field_of_study}` : ''}
              | {edu.institution}
              {#if edu.graduation_year}| {edu.graduation_year}{/if}
            </p>
          {/each}
        </section>
      {/if}

      {#if includedSkills.length > 0}
        <section class="skills">
          <h2>Skills</h2>
          <p>{includedSkills.map(s => s.name).join(', ')}</p>
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
              {#if project.technologies}<p class="technologies">{project.technologies}</p>{/if}
            </div>
          {/each}
        </section>
      {/if}

    {:else}
      <!-- Classic/Modern Templates -->
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

  /* Brussels Template - Two Column with Sidebar */
  .template-brussels {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 10pt;
    display: grid;
    grid-template-columns: 180px 1fr;
    gap: 24px;
  }

  .template-brussels .sidebar {
    display: flex;
    flex-direction: column;
    gap: 16pt;
  }

  .template-brussels .main-content {
    display: flex;
    flex-direction: column;
  }

  .template-brussels .profile-photo {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    object-fit: cover;
  }

  .template-brussels .photo-placeholder {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    background: #F3F4F6;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .template-brussels .photo-placeholder svg {
    width: 100%;
    height: 100%;
  }

  .template-brussels .name {
    font-size: 18pt;
    font-weight: bold;
    color: #0066cc;
    margin: 0 0 8pt;
  }

  .template-brussels .sidebar h3 {
    font-size: 11pt;
    font-weight: bold;
    color: #0066cc;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 4pt;
    margin: 0 0 8pt;
  }

  .template-brussels .contact-item {
    font-size: 9pt;
    margin: 0 0 4pt;
    word-break: break-word;
  }

  .template-brussels .skills-list {
    display: flex;
    flex-direction: column;
    gap: 4pt;
  }

  .template-brussels .skill-item {
    font-size: 9pt;
    padding: 2pt 6pt;
    background: #f0f0f0;
    border-radius: 2pt;
  }

  .template-brussels .language-item {
    font-size: 9pt;
    margin: 0 0 4pt;
  }

  .template-brussels .main-content section {
    margin-bottom: 12pt;
  }

  .template-brussels .main-content h2 {
    font-size: 12pt;
    font-weight: bold;
    color: #0066cc;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 2pt;
    margin: 0 0 8pt;
  }

  .template-brussels .summary p {
    font-size: 9pt;
    margin: 0;
  }

  .template-brussels .job {
    margin-bottom: 10pt;
  }

  .template-brussels .job-header {
    display: flex;
    flex-wrap: wrap;
    gap: 4pt;
    margin-bottom: 4pt;
  }

  .template-brussels .job-title {
    font-weight: bold;
    font-size: 10pt;
  }

  .template-brussels .job-company {
    color: #333;
    font-size: 10pt;
  }

  .template-brussels .job-dates {
    margin-left: auto;
    font-size: 9pt;
    color: #666;
  }

  .template-brussels .job-description {
    font-size: 9pt;
    white-space: pre-wrap;
    margin: 0;
  }

  .template-brussels .education p {
    font-size: 9pt;
    margin: 0 0 4pt;
  }

  .template-brussels .project {
    margin-bottom: 8pt;
  }

  .template-brussels .project-name {
    font-weight: bold;
    font-size: 9pt;
    margin: 0 0 2pt;
  }

  .template-brussels .project p {
    font-size: 9pt;
    margin: 0 0 2pt;
  }

  .template-brussels .technologies {
    color: #666;
  }

  /* EU Classic Template - Single Column Traditional */
  .template-eu_classic {
    font-family: Georgia, "Times New Roman", serif;
    font-size: 11pt;
  }

  .template-eu_classic .cv-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16pt;
    border-bottom: 2px solid #1a1a1a;
    padding-bottom: 12pt;
  }

  .template-eu_classic .header-content {
    flex: 1;
  }

  .template-eu_classic .profile-photo {
    width: 100px;
    height: 100px;
    object-fit: cover;
    border: 1px solid #e0e0e0;
  }

  .template-eu_classic .photo-placeholder {
    width: 100px;
    height: 100px;
    background: #F3F4F6;
    border: 1px solid #e0e0e0;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .template-eu_classic .photo-placeholder svg {
    width: 100%;
    height: 100%;
  }

  .template-eu_classic .name {
    font-size: 20pt;
    font-weight: normal;
    margin: 0 0 8pt;
  }

  .template-eu_classic .contact {
    font-size: 10pt;
    color: #333;
    margin: 0 0 4pt;
  }

  .template-eu_classic section {
    margin-bottom: 14pt;
  }

  .template-eu_classic h2 {
    font-size: 12pt;
    text-transform: uppercase;
    letter-spacing: 0.5pt;
    border-bottom: 1px solid #1a1a1a;
    padding-bottom: 2pt;
    margin: 0 0 8pt;
  }

  .template-eu_classic .summary p {
    font-size: 10pt;
    margin: 0;
  }

  .template-eu_classic .job {
    margin-bottom: 10pt;
  }

  .template-eu_classic .job-header {
    display: flex;
    flex-wrap: wrap;
    gap: 4pt;
    margin-bottom: 4pt;
  }

  .template-eu_classic .job-title {
    font-weight: bold;
  }

  .template-eu_classic .job-company {
    font-style: italic;
  }

  .template-eu_classic .job-dates {
    margin-left: auto;
    font-size: 10pt;
    color: #333;
  }

  .template-eu_classic .job-description {
    font-size: 10pt;
    white-space: pre-wrap;
    margin: 0;
  }

  .template-eu_classic .skills p {
    font-size: 10pt;
    margin: 0;
  }

  .template-eu_classic .education p {
    font-size: 10pt;
    margin: 0 0 4pt;
  }

  .template-eu_classic .languages p {
    font-size: 10pt;
    margin: 0;
  }

  .template-eu_classic .project {
    margin-bottom: 8pt;
  }

  .template-eu_classic .project-name {
    font-weight: bold;
    font-size: 10pt;
    margin: 0 0 2pt;
  }

  .template-eu_classic .project p {
    font-size: 10pt;
    margin: 0 0 2pt;
  }

  .template-eu_classic .technologies {
    font-style: italic;
    color: #333;
  }
</style>
