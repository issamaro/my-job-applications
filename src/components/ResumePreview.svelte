<script>
  import RequirementsAnalysis from './RequirementsAnalysis.svelte';
  import ResumeSection from './ResumeSection.svelte';
  import { updateResume } from '../lib/api.js';

  let { resume, jobAnalysis, jobTitle, companyName, matchScore, createdAt, onBack, onRegenerate } = $props();

  let resumeData = $state(null);
  let editingId = $state(null);
  let editValue = $state('');
  let saving = $state(false);
  let savedId = $state(null);

  $effect(() => {
    if (resume) {
      resumeData = JSON.parse(JSON.stringify(resume));
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
    saving = true;
    try {
      resumeData.work_experiences[expIndex].description = editValue;
      await updateResume(resume.id || 1, resumeData);
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
    }
  }
</script>

<div class="resume-preview">
  <div class="preview-header">
    <button class="back-link" onclick={onBack}>
      ← Back to Input
    </button>
    <span class="match-score {getScoreClass(matchScore)}">
      Match Score: {matchScore?.toFixed(0) || 0}%
    </span>
  </div>

  <div class="preview-title">
    <h2>{jobTitle || 'Untitled'} · {companyName || 'Unknown'}</h2>
    <p class="preview-date">Generated {formatDate(createdAt)}</p>
  </div>

  <hr />

  <RequirementsAnalysis {jobAnalysis} />

  <hr />

  <h3 class="section-heading">Resume Preview</h3>

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
      title="Work Experience"
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
      title="Skills"
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
      title="Education"
      included={resumeData.education?.[0]?.included !== false}
      onToggle={() => toggleSection('education')}
    >
      {#snippet children()}
        {#each resumeData.education as edu}
          <p>{edu.degree} {edu.field_of_study ? `in ${edu.field_of_study}` : ''} · {edu.institution} · {edu.graduation_year || ''}</p>
        {/each}
      {/snippet}
    </ResumeSection>

    <ResumeSection
      title="Projects"
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

  <hr />

  <div class="preview-actions">
    <button class="btn btn-primary" onclick={onRegenerate}>
      Regenerate
    </button>
  </div>
</div>
