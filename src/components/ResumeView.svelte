<script>
  import JobAnalysis from './JobAnalysis.svelte';
  import ResumeSection from './ResumeSection.svelte';
  import TemplateSelector from './TemplateSelector.svelte';
  import PdfPreview from './PdfPreview.svelte';
  import Toast from './Toast.svelte';
  import { updateResume, downloadPdf } from '../lib/api.js';

  let { resume, onBack, onRegenerate } = $props();

  const languageLabels = {
    en: 'English',
    fr: 'Français',
    nl: 'Nederlands'
  };

  // Section translations for edit view
  const sectionTranslations = {
    en: {
      resumeEditor: 'Resume Editor',
      resumePreview: 'Resume Preview',
      workExperience: 'Work Experience',
      skills: 'Skills',
      education: 'Education',
      languages: 'Languages',
      projects: 'Projects'
    },
    fr: {
      resumeEditor: 'Éditeur de CV',
      resumePreview: 'Aperçu du CV',
      workExperience: 'Expérience',
      skills: 'Compétences',
      education: 'Formation',
      languages: 'Langues',
      projects: 'Projets'
    },
    nl: {
      resumeEditor: 'CV Bewerken',
      resumePreview: 'CV Voorbeeld',
      workExperience: 'Werkervaring',
      skills: 'Vaardigheden',
      education: 'Opleiding',
      languages: 'Talen',
      projects: 'Projecten'
    }
  };

  // Reactive translations based on resume.language
  let labels = $derived.by(() => {
    const lang = resume?.language || 'en';
    return sectionTranslations[lang] || sectionTranslations.en;
  });

  let resumeData = $state(null);
  let editingId = $state(null);
  let editValue = $state('');
  let saving = $state(false);
  let savedId = $state(null);

  let editMode = $state('edit');
  let selectedTemplate = $state('classic');
  let isExporting = $state(false);
  let toastMessage = $state(null);
  let toastType = $state('success');

  $effect(() => {
    if (resume?.resume) {
      resumeData = JSON.parse(JSON.stringify(resume.resume));
    }
  });

  function getScoreClass(score) {
    if (score >= 80) return 'score-high';
    if (score >= 60) return 'score-medium';
    return 'score-low';
  }

  function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }

  function formatWorkDate(dateStr) {
    if (!dateStr) return 'Present';
    const [year, month] = dateStr.split('-');
    const date = new Date(parseInt(year), parseInt(month) - 1);
    return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
  }

  function startEdit(id, currentValue) {
    editingId = id;
    editValue = currentValue || '';
  }

  async function saveEdit(expIndex) {
    if (!resume?.id) {
      throw new Error('Cannot save: resume ID is missing');
    }
    saving = true;
    try {
      resumeData.work_experiences[expIndex].description = editValue;
      await updateResume(resume.id, resumeData);
      savedId = editingId;
      editingId = null;
      setTimeout(() => savedId = null, 2000);
    } catch (e) {
      console.error('Failed to save:', e);
    } finally {
      saving = false;
    }
  }

  function cancelEdit() {
    editingId = null;
    editValue = '';
  }

  function toggleSection(section) {
    if (section === 'work') {
      resumeData.work_experiences = resumeData.work_experiences.map(we => ({
        ...we,
        included: !resumeData.work_experiences[0]?.included
      }));
    } else if (section === 'skills') {
      resumeData.skills = resumeData.skills.map(s => ({
        ...s,
        included: !resumeData.skills[0]?.included
      }));
    } else if (section === 'education') {
      resumeData.education = resumeData.education.map(e => ({
        ...e,
        included: !resumeData.education[0]?.included
      }));
    } else if (section === 'projects') {
      resumeData.projects = resumeData.projects.map(p => ({
        ...p,
        included: !resumeData.projects[0]?.included
      }));
    } else if (section === 'languages') {
      resumeData.languages = resumeData.languages.map(lang => ({
        ...lang,
        included: !resumeData.languages[0]?.included
      }));
    }
  }

  async function handleDownloadPdf() {
    if (!resume?.id) {
      throw new Error('Cannot download PDF: resume ID is missing');
    }
    isExporting = true;
    try {
      await downloadPdf(resume.id, selectedTemplate, resume.language || 'en');
      toastType = 'success';
      toastMessage = 'PDF downloaded';
    } catch (e) {
      toastType = 'error';
      toastMessage = 'Could not generate PDF. Please try again.';
    } finally {
      isExporting = false;
    }
  }
</script>

<div class="resume-preview">
  <div class="preview-header">
    <button class="back-link" onclick={onBack}>
      ← Back to Input
    </button>
    <span class="match-score {getScoreClass(resume.match_score)}">
      Match Score: {resume.match_score?.toFixed(0) || 0}%
    </span>
  </div>

  <div class="preview-title">
    <h2>{resume.job_title || 'Untitled'} · {resume.company_name || 'Unknown'}</h2>
    <p class="preview-date">
      Generated {formatDate(resume.created_at)}
      {#if resume.language}
        <span class="language-badge">{languageLabels[resume.language] || resume.language}</span>
      {/if}
    </p>
  </div>

  <hr />

  <JobAnalysis jobAnalysis={resume.job_analysis} />

  <hr />

  <div class="view-mode-container">
    <div class="view-mode-toggle" role="tablist" aria-label="View mode">
      <button
        type="button"
        class="view-mode-btn"
        class:active={editMode === 'edit'}
        onclick={() => editMode = 'edit'}
        role="tab"
        aria-selected={editMode === 'edit'}
      >
        Edit
      </button>
      <button
        type="button"
        class="view-mode-btn"
        class:active={editMode === 'preview'}
        onclick={() => editMode = 'preview'}
        role="tab"
        aria-selected={editMode === 'preview'}
      >
        Preview
      </button>
    </div>

    {#if editMode === 'preview'}
    <div class="preview-controls">
      <TemplateSelector bind:selected={selectedTemplate} />
      <button
        type="button"
        class="btn btn-primary download-btn"
        onclick={handleDownloadPdf}
        disabled={isExporting}
        aria-live="polite"
      >
        {isExporting ? 'Generating...' : 'Download PDF'}
      </button>
    </div>
    {/if}
  </div>

  {#if editMode === 'edit'}
  <h3 class="section-heading">{labels.resumeEditor}</h3>

  {#if resumeData}
    {#if resumeData.personal_info}
    <div class="personal-info-preview">
      <h4>{resumeData.personal_info.full_name}</h4>
      <p class="contact-line">
        {resumeData.personal_info.email}
        {#if resumeData.personal_info.phone} · {resumeData.personal_info.phone}{/if}
      </p>
      {#if resumeData.personal_info.location || resumeData.personal_info.linkedin_url}
      <p class="contact-line">
        {resumeData.personal_info.location || ''}
        {#if resumeData.personal_info.linkedin_url} · {resumeData.personal_info.linkedin_url}{/if}
      </p>
      {/if}
      {#if resumeData.summary}
      <p class="summary">{resumeData.summary}</p>
      {/if}
    </div>
    {/if}

    <ResumeSection
      title={labels.workExperience}
      included={resumeData.work_experiences?.[0]?.included !== false}
      onToggle={() => toggleSection('work')}
    >
      {#snippet children()}
        <div class="work-list">
          {#each resumeData.work_experiences as exp, index}
            <div class="work-item">
              <div class="work-header">
                <span class="work-number">{index + 1}.</span>
                <span class="work-title">{exp.title} · {exp.company}</span>
              </div>
              <p class="work-dates">{formatWorkDate(exp.start_date)} – {formatWorkDate(exp.end_date)}</p>

              {#if editingId === exp.id}
                <div class="inline-edit">
                  <textarea
                    bind:value={editValue}
                    rows="4"
                  ></textarea>
                  <div class="edit-actions">
                    <button class="btn" onclick={() => saveEdit(index)} disabled={saving}>
                      {saving ? 'Saving...' : 'Save'}
                    </button>
                    <button class="btn" onclick={cancelEdit}>Cancel</button>
                  </div>
                </div>
              {:else}
                <p class="work-description">{exp.description}</p>
                <div class="work-footer">
                  {#if exp.match_reasons?.length > 0}
                    <span class="match-reasons">Match: {exp.match_reasons.join(', ')}</span>
                  {/if}
                  <button class="edit-btn" onclick={() => startEdit(exp.id, exp.description)}>
                    Edit
                  </button>
                  {#if savedId === exp.id}
                    <span class="saved-indicator">Saved</span>
                  {/if}
                </div>
              {/if}
            </div>
          {/each}
        </div>
      {/snippet}
    </ResumeSection>

    <ResumeSection
      title={labels.skills}
      included={resumeData.skills?.[0]?.included !== false}
      onToggle={() => toggleSection('skills')}
    >
      {#snippet children()}
        <div class="skill-tags">
          {#each resumeData.skills as skill}
            <span class="skill-tag" class:matched={skill.matched}>
              {skill.name} {skill.matched ? '✓' : ''}
            </span>
          {/each}
        </div>
      {/snippet}
    </ResumeSection>

    <ResumeSection
      title={labels.education}
      included={resumeData.education?.[0]?.included !== false}
      onToggle={() => toggleSection('education')}
    >
      {#snippet children()}
        {#each resumeData.education as edu}
          <p>{edu.degree} {edu.field_of_study ? `in ${edu.field_of_study}` : ''} · {edu.institution} · {edu.graduation_year || ''}</p>
        {/each}
      {/snippet}
    </ResumeSection>

    {#if resumeData.languages?.length > 0}
    <ResumeSection
      title={labels.languages}
      included={resumeData.languages?.[0]?.included !== false}
      onToggle={() => toggleSection('languages')}
    >
      {#snippet children()}
        <div class="languages-list">
          {#each resumeData.languages as lang, i}
            <span class="language-item">{lang.name} - {lang.level}{#if i < resumeData.languages.length - 1},{/if}</span>{' '}
          {/each}
        </div>
      {/snippet}
    </ResumeSection>
    {/if}

    <ResumeSection
      title={labels.projects}
      included={resumeData.projects?.[0]?.included === true}
      onToggle={() => toggleSection('projects')}
    >
      {#snippet children()}
        {#each resumeData.projects as project}
          <div class="project-item">
            <p class="project-name">{project.name}</p>
            {#if project.description}
              <p class="project-description">{project.description}</p>
            {/if}
            {#if project.technologies}
              <p class="project-tech">{project.technologies}</p>
            {/if}
          </div>
        {/each}
      {/snippet}
    </ResumeSection>
  {/if}
  {:else}
  <h3 class="section-heading">{labels.resumePreview}</h3>
  <PdfPreview {resumeData} template={selectedTemplate} language={resume?.language || 'en'} />
  {/if}

  <hr />

  <div class="preview-actions">
    <button class="btn btn-primary" onclick={onRegenerate}>
      Regenerate
    </button>
  </div>
</div>

<Toast bind:message={toastMessage} type={toastType} />

<style>
  .resume-preview {
    hr {
      border: none;
      border-top: 1px solid var(--color-border);
      margin: var(--spacing-section) 0;
    }
  }

  .preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-grid);
  }

  .back-link {
    color: var(--color-primary);
    background: none;
    border: none;
    cursor: pointer;
    font-size: var(--font-size-body);
    font-family: inherit;
    padding: 0;

    &:hover {
      text-decoration: underline;
    }

    &:focus {
      outline: 2px solid var(--color-primary);
      outline-offset: 2px;
    }
  }

  .match-score {
    font-size: var(--font-size-heading);
    font-weight: bold;

    &.score-high {
      color: var(--color-success);
    }

    &.score-medium {
      color: var(--color-text);
    }

    &.score-low {
      color: #cc6600;
    }
  }

  .preview-title {
    h2 {
      margin-bottom: 4px;
    }
  }

  .preview-date {
    color: rgb(var(--color-text-rgb) / 0.6);
    font-size: 14px;
    margin: 0;
  }

  .language-badge {
    display: inline-block;
    margin-left: 8px;
    padding: 2px 8px;
    font-size: 12px;
    font-weight: 500;
    background-color: rgb(var(--color-primary-rgb) / 0.1);
    color: var(--color-primary);
    border-radius: 4px;
  }

  .section-heading {
    margin-bottom: var(--spacing-grid);
  }

  .personal-info-preview {
    margin-bottom: var(--spacing-section);
    padding: var(--spacing-grid);
    border: 1px solid var(--color-border);
    border-radius: 2px;

    h4 {
      margin-bottom: 4px;
    }

    .contact-line {
      font-size: 14px;
      color: rgb(var(--color-text-rgb) / 0.7);
      margin-bottom: 4px;
    }

    .summary {
      margin-top: var(--spacing-grid);
      font-size: 14px;
    }
  }

  .work-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-grid);
  }

  .work-item {
    padding-bottom: var(--spacing-grid);
    border-bottom: 1px solid var(--color-border);

    &:last-child {
      padding-bottom: 0;
      border-bottom: none;
    }
  }

  .work-header {
    display: flex;
    align-items: baseline;
    gap: 8px;
  }

  .work-number {
    font-weight: 600;
    color: rgb(var(--color-text-rgb) / 0.5);
  }

  .work-title {
    font-weight: 600;
  }

  .work-dates {
    font-size: 14px;
    color: rgb(var(--color-text-rgb) / 0.6);
    margin: 4px 0;
  }

  .work-description {
    font-size: 14px;
    white-space: pre-wrap;
    margin: 8px 0;
  }

  .work-footer {
    display: flex;
    align-items: center;
    gap: var(--spacing-grid);
    font-size: 14px;
  }

  .match-reasons {
    color: var(--color-success);
  }

  .inline-edit {
    margin-top: 8px;

    textarea {
      margin-bottom: 8px;
    }
  }

  .edit-actions {
    display: flex;
    gap: 8px;
  }

  .project-item {
    margin-bottom: var(--spacing-grid);

    &:last-child {
      margin-bottom: 0;
    }
  }

  .project-name {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .project-description {
    font-size: 14px;
    margin-bottom: 4px;
  }

  .project-tech {
    font-size: 14px;
    color: rgb(var(--color-text-rgb) / 0.6);
  }

  .preview-actions {
    margin-top: var(--spacing-section);
  }

  .view-mode-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-section);
    flex-wrap: wrap;
    gap: var(--spacing-grid);
  }

  .view-mode-toggle {
    display: flex;
    gap: 0;
  }

  .view-mode-btn {
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

  .preview-controls {
    display: flex;
    gap: var(--spacing-grid);
    align-items: center;
  }

  .download-btn {
    min-width: 120px;

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  }

  .skill-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .skill-tag {
    display: inline-flex;
    align-items: center;
    padding: 4px 8px;
    font-size: 14px;
    background: rgb(var(--color-primary-rgb) / 0.1);
    border: 1px solid rgb(var(--color-primary-rgb) / 0.3);
    border-radius: 2px;

    &.matched {
      color: var(--color-success);
      background: rgb(var(--color-success-rgb) / 0.1);
      border-color: rgb(var(--color-success-rgb) / 0.3);
    }
  }
</style>
