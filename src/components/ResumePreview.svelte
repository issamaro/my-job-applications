<script>
  import RequirementsAnalysis from './RequirementsAnalysis.svelte';
  import ResumeSection from './ResumeSection.svelte';
  import TemplateSelector from './TemplateSelector.svelte';
  import PdfPreview from './PdfPreview.svelte';
  import Toast from './Toast.svelte';
  import { updateResume, downloadResumePdf } from '../lib/api.js';

  let { resume, onBack, onRegenerate } = $props();

  const languageLabels = {
    en: 'English',
    fr: 'Français',
    nl: 'Nederlands'
  };

  // Section translations for edit view
  const sectionTranslations = {
    en: {
      resumePreview: 'Resume Preview',
      workExperience: 'Work Experience',
      skills: 'Skills',
      education: 'Education',
      languages: 'Languages',
      projects: 'Projects'
    },
    fr: {
      resumePreview: 'Aperçu du CV',
      workExperience: 'Expérience',
      skills: 'Compétences',
      education: 'Formation',
      languages: 'Langues',
      projects: 'Projets'
    },
    nl: {
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

  let viewMode = $state('edit');
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
      await downloadResumePdf(resume.id, selectedTemplate, resume.language || 'en');
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

  <RequirementsAnalysis jobAnalysis={resume.job_analysis} />

  <hr />

  <div class="view-mode-container">
    <div class="view-mode-toggle" role="tablist" aria-label="View mode">
      <button
        type="button"
        class="view-mode-btn"
        class:active={viewMode === 'edit'}
        onclick={() => viewMode = 'edit'}
        role="tab"
        aria-selected={viewMode === 'edit'}
      >
        Edit
      </button>
      <button
        type="button"
        class="view-mode-btn"
        class:active={viewMode === 'preview'}
        onclick={() => viewMode = 'preview'}
        role="tab"
        aria-selected={viewMode === 'preview'}
      >
        Preview
      </button>
    </div>

    {#if viewMode === 'preview'}
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

  {#if viewMode === 'edit'}
  <h3 class="section-heading">{labels.resumePreview}</h3>

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
