<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->
<!-- Scope: Resume preview screen — editorial chrome, left rail, Edit/Preview pane. -->

<script>
  import JobAnalysis from './JobAnalysis.svelte';
  import EditorialSection from './EditorialSection.svelte';
  import TemplateSelector from './TemplateSelector.svelte';
  import PdfPreview from './PdfPreview.svelte';
  import Toast from './Toast.svelte';
  import { updateResume, downloadPdf, getSkills } from '../lib/api.js';

  let { resume, onBack, onRegenerate } = $props();

  const sectionTranslations = {
    en: {
      workExperience: 'Experience',
      skills: 'Skills',
      education: 'Education',
      languages: 'Languages',
      projects: 'Projects',
      in: 'in',
      availableSkills: 'Available skills'
    },
    fr: {
      workExperience: 'Expérience',
      skills: 'Compétences',
      education: 'Formation',
      languages: 'Langues',
      projects: 'Projets',
      in: 'en',
      availableSkills: 'Available skills'
    },
    nl: {
      workExperience: 'Werkervaring',
      skills: 'Vaardigheden',
      education: 'Opleiding',
      languages: 'Talen',
      projects: 'Projecten',
      in: 'in',
      availableSkills: 'Available skills'
    }
  };

  const languageLockedLabels = {
    en: 'Resume language: English (locked)',
    fr: 'Resume language: French (locked)',
    nl: 'Resume language: Dutch (locked)'
  };

  let labels = $derived.by(() => {
    const lang = resume?.language || 'en';
    return sectionTranslations[lang] || sectionTranslations.en;
  });

  let resumeData = $state(null);
  let editingId = $state(null);
  let editValue = $state('');
  let saving = $state(false);
  let savedId = $state(null);

  let editingSummary = $state(false);
  let summaryDraft = $state('');
  let editingSkillIndex = $state(null);
  let skillDraft = $state('');
  let savingSkillIndex = $state(null);
  let profileSkills = $state([]);
  let savingProfileSkillName = $state(null);

  let availableProfileSkills = $derived.by(() => {
    if (!resumeData?.skills) return [];
    const present = new Set(resumeData.skills.map(s => s.name.toLowerCase()));
    return profileSkills.filter(p => !present.has(p.name.toLowerCase()));
  });

  let editMode = $state('edit');
  let editTabRef = $state(null);
  let previewTabRef = $state(null);
  let selectedTemplate = $state('classic');
  let isExporting = $state(false);
  let toastMessage = $state(null);
  let toastType = $state('success');
  let draggedIndex = $state(null);
  let orderBeforeDrag = null;

  let sectionRows = $derived.by(() => {
    if (!resumeData) return [];
    const work = resumeData.work_experiences?.[0]?.included !== false;
    const skills = resumeData.skills?.length > 0
      ? !resumeData.skills.every(s => s.included === false)
      : true;
    const edu = resumeData.education?.[0]?.included !== false;
    const langs = resumeData.languages?.[0]?.included !== false;
    const projs = resumeData.projects?.[0]?.included === true;
    return [
      { key: null,        label: 'Identity',   included: true,   disabled: true  },
      { key: null,        label: 'Summary',    included: true,   disabled: true  },
      { key: 'work',      label: labels.workExperience, included: work,   disabled: false },
      { key: 'education', label: labels.education,      included: edu,    disabled: false },
      { key: 'skills',    label: labels.skills,         included: skills, disabled: false },
      { key: 'languages', label: labels.languages,      included: langs,  disabled: false },
      { key: 'projects',  label: labels.projects,       included: projs,  disabled: false }
    ];
  });

  $effect(() => {
    if (resume?.resume) {
      resumeData = JSON.parse(JSON.stringify(resume.resume));
    }
  });

  async function readProfileSkills() {
    try {
      profileSkills = await getSkills();
    } catch (e) {
      profileSkills = [];
    }
  }

  $effect(() => {
    readProfileSkills();
  });

  async function createSkillFromProfile(name) {
    if (!resume?.id) {
      throw new Error('Cannot save: resume ID is missing');
    }
    savingProfileSkillName = name;
    const previous = JSON.parse(JSON.stringify(resumeData.skills));
    try {
      resumeData.skills = [...resumeData.skills, { name, matched: false, included: true }];
      await updateResume(resume.id, resumeData);
      toastType = 'success';
      toastMessage = 'Saved';
    } catch (err) {
      resumeData.skills = previous;
      toastType = 'error';
      toastMessage = 'Could not save skills. Try again.';
    } finally {
      savingProfileSkillName = null;
    }
  }

  function findMatchPillVariant(score) {
    if (score == null) return null;
    if (score >= 80) return 'pill-positive';
    if (score >= 60) return 'pill-warn';
    return 'pill-accent';
  }

  function findMatchAriaLabel(score) {
    if (score == null) return null;
    const rounded = Math.round(score);
    if (score >= 80) return `Match score: ${rounded} percent, strong fit`;
    if (score >= 60) return `Match score: ${rounded} percent, moderate fit`;
    return `Match score: ${rounded} percent, weak fit`;
  }

  function readSectionAriaLabel(row) {
    if (row.disabled) return `${row.label} — always shown`;
    return `${row.label} — ${row.included ? 'included' : 'excluded'}`;
  }

  function updateSectionFromRail(row) {
    if (row.disabled || !row.key) return;
    void updateSectionInclusion(row.key, !row.included);
  }

  function updateModeOnKey(e) {
    if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight' && e.key !== 'Home' && e.key !== 'End') return;
    e.preventDefault();
    if (e.key === 'Home') editMode = 'edit';
    else if (e.key === 'End') editMode = 'preview';
    else editMode = editMode === 'edit' ? 'preview' : 'edit';
    const target = editMode === 'edit' ? editTabRef : previewTabRef;
    target?.focus();
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

  function startEditSummary() {
    summaryDraft = resumeData.summary || '';
    editingSummary = true;
  }

  function cancelEditSummary() {
    editingSummary = false;
    summaryDraft = '';
  }

  async function writeSummaryEdit() {
    if (!resume?.id) {
      throw new Error('Cannot save: resume ID is missing');
    }
    saving = true;
    try {
      resumeData.summary = summaryDraft;
      await updateResume(resume.id, resumeData);
      editingSummary = false;
      savedId = '__summary__';
      setTimeout(() => savedId = null, 2000);
    } catch (e) {
      console.error('Failed to save summary:', e);
      toastType = 'error';
      toastMessage = 'Could not save summary. Try again.';
    } finally {
      saving = false;
    }
  }

  function readSummaryKey(e) {
    if (e.key === 'Escape') {
      e.preventDefault();
      cancelEditSummary();
    } else if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      writeSummaryEdit();
    }
  }

  function startEditSkill(skillIndex) {
    skillDraft = resumeData.skills[skillIndex].name;
    editingSkillIndex = skillIndex;
  }

  function cancelEditSkill() {
    editingSkillIndex = null;
    skillDraft = '';
  }

  async function writeSkillRename(skillIndex) {
    if (skillDraft.trim() === '') {
      cancelEditSkill();
      return;
    }
    if (!resume?.id) {
      throw new Error('Cannot save: resume ID is missing');
    }
    savingSkillIndex = skillIndex;
    const previous = resumeData.skills[skillIndex].name;
    try {
      resumeData.skills[skillIndex].name = skillDraft.trim();
      await updateResume(resume.id, resumeData);
      toastType = 'success';
      toastMessage = 'Saved';
    } catch (err) {
      resumeData.skills[skillIndex].name = previous;
      toastType = 'error';
      toastMessage = 'Could not save skills. Try again.';
    } finally {
      savingSkillIndex = null;
      editingSkillIndex = null;
      skillDraft = '';
    }
  }

  function readSkillKey(e, skillIndex) {
    if (e.key === 'Escape') {
      e.preventDefault();
      cancelEditSkill();
    } else if (e.key === 'Enter') {
      e.preventDefault();
      writeSkillRename(skillIndex);
    }
  }

  async function updateSkillInclusion(skillIndex, included) {
    if (!resume?.id) {
      throw new Error('Cannot save: resume ID is missing');
    }
    savingSkillIndex = skillIndex;
    const previous = resumeData.skills[skillIndex].included;
    try {
      resumeData.skills[skillIndex].included = included;
      await updateResume(resume.id, resumeData);
      toastType = 'success';
      toastMessage = 'Saved';
    } catch (err) {
      resumeData.skills[skillIndex].included = previous;
      toastType = 'error';
      toastMessage = 'Could not save skills. Try again.';
    } finally {
      savingSkillIndex = null;
    }
  }

  const sectionListKeys = {
    work: 'work_experiences',
    education: 'education',
    skills: 'skills',
    languages: 'languages',
    projects: 'projects'
  };

  async function updateSectionInclusion(section, included) {
    const key = sectionListKeys[section];
    if (!key || !resumeData?.[key]?.length) return;
    if (!resume?.id) {
      throw new Error('Cannot save: resume ID is missing');
    }
    const previous = resumeData[key];
    resumeData[key] = resumeData[key].map(item => ({ ...item, included }));
    try {
      await updateResume(resume.id, resumeData);
      toastType = 'success';
      toastMessage = 'Saved';
    } catch (err) {
      resumeData[key] = previous;
      toastType = 'error';
      toastMessage = 'Could not save sections. Try again.';
    }
  }

  function updateDraggedIndex(e, index) {
    draggedIndex = index;
    orderBeforeDrag = [...resumeData.work_experiences];
    e.dataTransfer.effectAllowed = 'move';
  }

  function updateOrderOnHover(e, index) {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === index) return;

    const next = [...resumeData.work_experiences];
    const moved = next[draggedIndex];
    next.splice(draggedIndex, 1);
    next.splice(index, 0, moved);
    resumeData.work_experiences = next;
    draggedIndex = index;
  }

  async function writeReorderedOrder(e) {
    e.preventDefault();
    if (draggedIndex === null) return;

    const previous = orderBeforeDrag;
    draggedIndex = null;
    orderBeforeDrag = null;
    try {
      await updateResume(resume.id, resumeData);
      toastType = 'success';
      toastMessage = 'Order saved';
    } catch (err) {
      toastType = 'error';
      toastMessage = 'Could not save order. Reverting.';
      if (previous) resumeData.work_experiences = previous;
    }
  }

  function deleteDraggedIndex() {
    if (draggedIndex !== null && orderBeforeDrag) {
      resumeData.work_experiences = orderBeforeDrag;
    }
    draggedIndex = null;
    orderBeforeDrag = null;
  }

  async function writeDownloadedPdf() {
    if (!resume?.id) {
      throw new Error('Cannot download PDF: resume ID is missing');
    }
    isExporting = true;
    try {
      await downloadPdf(resume.id, selectedTemplate, resume.language || 'en');
      toastType = 'success';
      toastMessage = 'PDF downloaded';
    } catch (e) {
      console.error('PDF download failed:', e);
      toastType = 'error';
      toastMessage = e?.message ? `PDF download failed: ${e.message}` : 'Could not generate PDF. Please try again.';
    } finally {
      isExporting = false;
    }
  }

  function findRowIncluded(key) {
    return sectionRows.find(r => r.key === key)?.included ?? true;
  }
</script>

<div class="resume-preview">
  <header class="resume-page-header">
    <button
      type="button"
      class="btn-ghost"
      onclick={onBack}
      aria-label="Back to job input"
    >← Back to Input</button>

    <div class="resume-page-title">
      <span class="eyebrow">RESUME · FOR JOB</span>
      <h1 class="display">{resume.job_title || 'Untitled'} · {resume.company_name || 'Unknown'}</h1>
      <div class="resume-page-meta">
        <span>Generated {formatDate(resume.created_at)}</span>
        {#if resume.match_score != null}
          <span
            class="pill {findMatchPillVariant(resume.match_score)}"
            aria-label={findMatchAriaLabel(resume.match_score)}
          >Match {Math.round(resume.match_score)}%</span>
        {/if}
      </div>
    </div>

    <button type="button" class="btn" onclick={onRegenerate}>Regenerate</button>
  </header>

  <JobAnalysis jobAnalysis={resume.job_analysis} />

  <div class="resume-3col">
    <aside class="resume-rail" aria-label="Resume controls">
      <div class="resume-rail-group">
        <span class="eyebrow">Templates · 04</span>
        <TemplateSelector bind:selected={selectedTemplate} />
      </div>

      <hr class="rule-soft" />

      <div class="resume-rail-group">
        <span class="eyebrow">Language</span>
        <span
          class="pill pill-solid resume-rail-language"
          aria-label={languageLockedLabels[resume?.language || 'en']}
        >{(resume?.language || 'en').toUpperCase()}</span>
      </div>

      <hr class="rule-soft" />

      <div class="resume-rail-group">
        <span class="eyebrow">Sections</span>
        <div class="resume-rail-sections">
          {#each sectionRows as row (row.label)}
            <button
              type="button"
              class="rail-section-row"
              class:included={row.included && !row.disabled}
              class:disabled={row.disabled}
              aria-pressed={row.disabled ? undefined : row.included}
              aria-disabled={row.disabled ? 'true' : undefined}
              aria-label={readSectionAriaLabel(row)}
              tabindex={row.disabled ? -1 : 0}
              onclick={() => updateSectionFromRail(row)}
            >
              <span class="rail-section-checkbox" aria-hidden="true"></span>
              <span class="rail-section-label">{row.label}</span>
            </button>
          {/each}
        </div>
      </div>
    </aside>

    <div class="resume-pane">
      <div class="resume-tabs" role="tablist" aria-label="View mode">
        <button
          type="button"
          class:btn={editMode === 'edit'}
          class:btn-ghost={editMode !== 'edit'}
          role="tab"
          aria-selected={editMode === 'edit'}
          tabindex={editMode === 'edit' ? 0 : -1}
          bind:this={editTabRef}
          onclick={() => editMode = 'edit'}
          onkeydown={updateModeOnKey}
        >Edit</button>
        <button
          type="button"
          class:btn={editMode === 'preview'}
          class:btn-ghost={editMode !== 'preview'}
          role="tab"
          aria-selected={editMode === 'preview'}
          tabindex={editMode === 'preview' ? 0 : -1}
          bind:this={previewTabRef}
          onclick={() => editMode = 'preview'}
          onkeydown={updateModeOnKey}
        >Preview</button>
      </div>

      {#if editMode === 'preview'}
        <div class="resume-pane-preview">
          <div class="resume-page-meta-eyebrow">
            <span class="eyebrow num">A4 · 210 × 297</span>
            <span class="resume-page-count">1 / 1 page</span>
          </div>
          <div class="resume-page">
            <PdfPreview {resumeData} template={selectedTemplate} language={resume?.language || 'en'} />
          </div>
          <div class="resume-pane-actions">
            <button
              type="button"
              class="btn btn-primary"
              onclick={writeDownloadedPdf}
              disabled={isExporting}
              aria-live="polite"
            >{isExporting ? 'Generating…' : 'Download PDF'}</button>
          </div>
        </div>
      {:else}
        <div class="resume-pane-edit">
          {#if resumeData}
            {#if resumeData.personal_info}
              <div class="resume-block-wrapper">
                <EditorialSection number="01" title="Identity">
                  {#snippet children()}
                    <div class="resume-identity">
                      <p class="resume-identity-name">{resumeData.personal_info.full_name}</p>
                      <p class="resume-identity-contact">
                        {resumeData.personal_info.email}
                        {#if resumeData.personal_info.phone} · {resumeData.personal_info.phone}{/if}
                      </p>
                      {#if resumeData.personal_info.location || resumeData.personal_info.linkedin_url}
                        <p class="resume-identity-contact">
                          {resumeData.personal_info.location || ''}
                          {#if resumeData.personal_info.linkedin_url} · {resumeData.personal_info.linkedin_url}{/if}
                        </p>
                      {/if}
                    </div>
                  {/snippet}
                </EditorialSection>
              </div>
            {/if}

            <div class="resume-block-wrapper">
              <EditorialSection number="02" title="Summary">
                {#snippet children()}
                  {#if editingSummary}
                    <!-- svelte-ignore a11y_autofocus -->
                    <textarea
                      class="textarea"
                      bind:value={summaryDraft}
                      onkeydown={readSummaryKey}
                      rows="4"
                      autofocus
                    ></textarea>
                    <div class="resume-edit-actions">
                      <button type="button" class="btn btn-primary" onclick={writeSummaryEdit} disabled={saving}>
                        {saving ? 'Saving…' : 'Save'}
                      </button>
                      <button type="button" class="btn-ghost" onclick={cancelEditSummary} disabled={saving}>Cancel</button>
                    </div>
                  {:else if resumeData.summary}
                    <p class="resume-summary-text">{resumeData.summary}</p>
                    <div class="resume-edit-actions">
                      <button type="button" class="btn-ghost" onclick={startEditSummary}>Edit</button>
                      {#if savedId === '__summary__'}
                        <span class="resume-saved-indicator" aria-live="polite">Saved</span>
                      {/if}
                    </div>
                  {:else}
                    <button type="button" class="btn-ghost" onclick={startEditSummary}>Add summary</button>
                  {/if}
                {/snippet}
              </EditorialSection>
            </div>

            {@const workIncluded = findRowIncluded('work')}
            <div class="resume-block-wrapper" class:section-dimmed={!workIncluded}>
              <EditorialSection number="03" title={labels.workExperience} count={resumeData.work_experiences?.length ?? 0}>
                {#snippet children()}
                  {#if !workIncluded}
                    <p class="resume-block-excluded">Hidden from resume — re-check {labels.workExperience} in the left rail to include.</p>
                  {/if}
                  <div class="resume-work-list">
                    {#each resumeData.work_experiences as exp, index}
                      <div
                        class="resume-work-row"
                        class:dragging={draggedIndex === index}
                        draggable={editingId !== exp.id}
                        ondragstart={(e) => updateDraggedIndex(e, index)}
                        ondragover={(e) => updateOrderOnHover(e, index)}
                        ondrop={writeReorderedOrder}
                        ondragend={deleteDraggedIndex}
                      >
                        <span class="num resume-work-dates">
                          {formatWorkDate(exp.start_date)} — {formatWorkDate(exp.end_date)}
                        </span>
                        <div class="resume-work-body">
                          <div class="resume-work-title-row">
                            <span class="resume-work-handle" aria-label="Drag to reorder">⋮⋮</span>
                            <span class="resume-work-title">
                              {exp.title} <span class="resume-work-company">· {exp.company}</span>
                            </span>
                          </div>
                          {#if editingId === exp.id}
                            <textarea
                              class="textarea"
                              bind:value={editValue}
                              rows="4"
                            ></textarea>
                            <div class="resume-edit-actions">
                              <button type="button" class="btn btn-primary" onclick={() => saveEdit(index)} disabled={saving}>
                                {saving ? 'Saving…' : 'Save'}
                              </button>
                              <button type="button" class="btn-ghost" onclick={cancelEdit}>Cancel</button>
                            </div>
                          {:else}
                            <p class="resume-work-description">{exp.description}</p>
                            {#if exp.match_reasons?.length > 0}
                              <p class="resume-work-match">Match: {exp.match_reasons.join(', ')}</p>
                            {/if}
                          {/if}
                        </div>
                        <div class="resume-work-actions">
                          {#if editingId !== exp.id}
                            <button type="button" class="btn-ghost" onclick={() => startEdit(exp.id, exp.description)}>Edit</button>
                          {/if}
                          {#if savedId === exp.id}
                            <span class="resume-saved-indicator">Saved</span>
                          {/if}
                        </div>
                      </div>
                    {/each}
                    {#if resumeData.work_experiences.length === 0}
                      <p class="resume-empty">No experiences added.</p>
                    {/if}
                  </div>
                {/snippet}
              </EditorialSection>
            </div>

            {@const eduIncluded = findRowIncluded('education')}
            <div class="resume-block-wrapper" class:section-dimmed={!eduIncluded}>
              <EditorialSection number="04" title={labels.education} count={resumeData.education?.length ?? 0}>
                {#snippet children()}
                  {#if !eduIncluded}
                    <p class="resume-block-excluded">Hidden from resume — re-check {labels.education} in the left rail to include.</p>
                  {/if}
                  <div class="resume-education-list">
                    {#each resumeData.education as edu}
                      <div class="resume-education-row">
                        <span class="num resume-education-year">{edu.graduation_year || ''}</span>
                        <div class="resume-education-body">
                          <span class="resume-education-degree">{edu.degree}{edu.field_of_study ? ` ${labels.in} ${edu.field_of_study}` : ''}</span>
                          <span class="resume-education-institution"> · {edu.institution}</span>
                        </div>
                      </div>
                    {/each}
                    {#if resumeData.education.length === 0}
                      <p class="resume-empty">No education added.</p>
                    {/if}
                  </div>
                {/snippet}
              </EditorialSection>
            </div>

            {@const skillsIncluded = findRowIncluded('skills')}
            <div class="resume-block-wrapper" class:section-dimmed={!skillsIncluded}>
              <EditorialSection number="05" title={labels.skills} count={resumeData.skills?.length ?? 0}>
                {#snippet children()}
                  {#if !skillsIncluded}
                    <p class="resume-block-excluded">Hidden from resume — re-check {labels.skills} in the left rail to include.</p>
                  {/if}
                  {#if resumeData.skills.length === 0 && availableProfileSkills.length === 0}
                    <p class="resume-empty">No skills.</p>
                  {:else}
                    <div class="resume-skills-cluster">
                      {#each resumeData.skills as skill, index}
                        {#if skill.included !== false}
                          <span
                            class="pill skill-chip"
                            class:pill-positive={skill.matched}
                            class:saving-skill={savingSkillIndex === index}
                          >
                            {#if editingSkillIndex === index}
                              <!-- svelte-ignore a11y_autofocus -->
                              <input
                                class="skill-chip-input"
                                bind:value={skillDraft}
                                onkeydown={(e) => readSkillKey(e, index)}
                                aria-label="Rename skill {skill.name}"
                                autofocus
                              />
                              <button type="button" class="skill-chip-action" onclick={() => writeSkillRename(index)} aria-label="Save skill name">✓</button>
                              <button type="button" class="skill-chip-action" onclick={cancelEditSkill} aria-label="Cancel rename">×</button>
                            {:else}
                              <span class="skill-chip-name">{skill.name}{skill.matched ? ' ✓' : ''}</span>
                              <button type="button" class="skill-chip-action" onclick={() => startEditSkill(index)} aria-label="Rename skill {skill.name}">✎</button>
                              <button type="button" class="skill-chip-action" onclick={() => updateSkillInclusion(index, false)} aria-label="Exclude skill {skill.name}">×</button>
                            {/if}
                          </span>
                        {/if}
                      {/each}
                    </div>

                    {#if resumeData.skills.some(s => s.included === false) || availableProfileSkills.length > 0}
                      <span class="eyebrow resume-skills-available-eyebrow">{labels.availableSkills}</span>
                      <div class="resume-skills-cluster">
                        {#each resumeData.skills as skill, index}
                          {#if skill.included === false}
                            <span class="pill skill-chip-available" class:saving-skill={savingSkillIndex === index}>
                              <span class="skill-chip-name">{skill.name}</span>
                              <button type="button" class="skill-chip-action" onclick={() => updateSkillInclusion(index, true)} aria-label="Re-include skill {skill.name}">+</button>
                            </span>
                          {/if}
                        {/each}
                        {#each availableProfileSkills as profileSkill (profileSkill.id)}
                          <span class="pill skill-chip-available" class:saving-skill={savingProfileSkillName === profileSkill.name}>
                            <span class="skill-chip-name">{profileSkill.name}</span>
                            <button type="button" class="skill-chip-action" onclick={() => createSkillFromProfile(profileSkill.name)} aria-label="Add skill {profileSkill.name}">+</button>
                          </span>
                        {/each}
                      </div>
                    {/if}

                    {#if resumeData.skills.length > 0 && resumeData.skills.every(s => s.included === false)}
                      <p class="resume-empty">All skills excluded — re-include one below, or use the section toggle.</p>
                    {/if}
                  {/if}
                {/snippet}
              </EditorialSection>
            </div>

            {#if resumeData.languages?.length > 0}
              {@const langsIncluded = findRowIncluded('languages')}
              <div class="resume-block-wrapper" class:section-dimmed={!langsIncluded}>
                <EditorialSection number="06" title={labels.languages} count={resumeData.languages.length}>
                  {#snippet children()}
                    {#if !langsIncluded}
                      <p class="resume-block-excluded">Hidden from resume — re-check {labels.languages} in the left rail to include.</p>
                    {/if}
                    <div class="resume-languages-grid">
                      {#each resumeData.languages as lang}
                        <div class="resume-language-card">
                          <span class="resume-language-name">{lang.name}</span>
                          <span class="resume-language-level">{lang.level}</span>
                        </div>
                      {/each}
                    </div>
                  {/snippet}
                </EditorialSection>
              </div>
            {/if}

            {@const projsIncluded = findRowIncluded('projects')}
            <div class="resume-block-wrapper" class:section-dimmed={!projsIncluded}>
              <EditorialSection number="07" title={labels.projects} count={resumeData.projects?.length ?? 0}>
                {#snippet children()}
                  {#if !projsIncluded}
                    <p class="resume-block-excluded">Hidden from resume — re-check {labels.projects} in the left rail to include.</p>
                  {/if}
                  <div class="resume-projects-list">
                    {#each resumeData.projects as project}
                      <div class="resume-project-row">
                        <div class="resume-project-body">
                          <p class="resume-project-name">{project.name}</p>
                          {#if project.description}
                            <p class="resume-project-description">{project.description}</p>
                          {/if}
                          {#if project.technologies}
                            <p class="resume-project-tech">{project.technologies}</p>
                          {/if}
                        </div>
                      </div>
                    {/each}
                    {#if resumeData.projects.length === 0}
                      <p class="resume-empty">No projects.</p>
                    {/if}
                  </div>
                {/snippet}
              </EditorialSection>
            </div>
          {:else}
            <p class="resume-loading-note">Loading resume…</p>
          {/if}
        </div>
      {/if}
    </div>
  </div>
</div>

<Toast bind:message={toastMessage} type={toastType} />

<style>
  .resume-preview {
    padding: var(--d-pad);
    display: flex;
    flex-direction: column;
    gap: var(--d-gap);
  }

  .resume-page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    padding-bottom: var(--d-gap);
    border-bottom: 1px solid var(--rule-soft);
  }

  .resume-page-title {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    flex: 1;
    min-width: 0;
  }

  .resume-page-title h1 {
    font-size: 32px;
    line-height: 1.15;
    margin: 0;
    color: var(--ink);
    text-align: center;
  }

  .resume-page-meta {
    display: flex;
    align-items: baseline;
    gap: 12px;
    color: var(--ink-3);
    font-size: 12px;
  }

  .resume-3col {
    display: flex;
    gap: var(--d-gap);
    flex-wrap: wrap;
    align-items: flex-start;
  }

  .resume-rail {
    width: 240px;
    flex-shrink: 0;
    min-width: 240px;
    padding-right: var(--d-pad);
    border-right: 1px solid var(--rule);
    display: flex;
    flex-direction: column;
  }

  .resume-rail-group {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 12px 0;
  }

  .resume-rail hr {
    margin: 8px 0;
  }

  .resume-rail-language {
    align-self: flex-start;
    cursor: default;
  }

  .resume-rail-sections {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .rail-section-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 0;
    background: transparent;
    border: 0;
    font-family: inherit;
    text-align: left;
    cursor: pointer;
    color: var(--ink-3);
  }

  .rail-section-row.included {
    color: var(--ink);
  }

  .rail-section-row.disabled {
    color: var(--ink-4);
    cursor: default;
  }

  .rail-section-checkbox {
    width: 14px;
    height: 14px;
    border-radius: 2px;
    border: 1px solid var(--rule);
    background: transparent;
    flex-shrink: 0;
    display: inline-block;
  }

  .rail-section-row.included .rail-section-checkbox {
    background: var(--ink);
    border-color: var(--ink);
  }

  .rail-section-row.disabled .rail-section-checkbox {
    border-color: var(--rule-soft);
  }

  .rail-section-label {
    font-size: 12px;
  }

  .rail-section-row:not(.disabled):focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }

  .resume-pane {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: var(--d-gap);
  }

  .resume-tabs {
    display: flex;
    gap: 4px;
    padding: 4px;
    align-self: flex-start;
  }

  .resume-tabs button {
    font-size: 12px;
    padding: 6px 12px;
  }

  .resume-pane-preview {
    background: var(--paper-3);
    padding: 28px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
  }

  .resume-page-meta-eyebrow {
    display: flex;
    align-items: baseline;
    gap: 12px;
  }

  .resume-page-count {
    color: var(--ink-3);
    font-size: 11px;
  }

  .resume-page {
    width: 600px;
    max-width: 100%;
    min-height: 848px;
    background: white;
    box-shadow: 0 1px 0 rgba(0, 0, 0, 0.04), 0 24px 48px -16px rgba(0, 0, 0, 0.18);
    overflow: auto;
  }

  .resume-page :global(.pdf-preview) {
    border: none;
    box-shadow: none;
    max-width: none;
  }

  .resume-pane-actions {
    display: flex;
    gap: 10px;
    justify-content: center;
  }

  .resume-pane-edit {
    display: flex;
    flex-direction: column;
    gap: var(--d-row);
  }

  .resume-block-wrapper {
    display: flex;
    flex-direction: column;
  }

  :global(.resume-block-wrapper.section-dimmed .editorial-section-title) {
    color: var(--ink-3);
  }

  :global(.resume-block-wrapper.section-dimmed .editorial-section-header .eyebrow) {
    color: var(--ink-4);
  }

  .resume-block-excluded {
    color: var(--ink-3);
    font-size: 12px;
    font-style: italic;
    margin: 0 0 16px;
  }

  .resume-identity {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .resume-identity-name {
    font-size: 16px;
    font-weight: 600;
    color: var(--ink);
    margin: 0;
  }

  .resume-identity-contact {
    font-size: 12px;
    color: var(--ink-3);
    margin: 0;
  }

  .resume-summary-text {
    font-size: 13px;
    color: var(--ink);
    line-height: 1.5;
    margin: 0;
  }

  .resume-edit-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 8px;
  }

  .resume-saved-indicator {
    color: var(--positive);
    font-size: 11px;
  }

  .resume-work-list,
  .resume-education-list,
  .resume-projects-list {
    display: flex;
    flex-direction: column;
  }

  .resume-work-row {
    display: grid;
    grid-template-columns: 110px 1fr auto;
    gap: 18px;
    padding: 12px 0;
    border-bottom: 1px solid var(--rule-soft);
    align-items: start;
  }

  .resume-work-row:last-child {
    border-bottom: 0;
  }

  .resume-work-row.dragging {
    opacity: 0.5;
    background: var(--paper-2);
  }

  .resume-work-dates {
    color: var(--ink-3);
    font-size: 11px;
    padding-top: 2px;
  }

  .resume-work-body {
    min-width: 0;
  }

  .resume-work-title-row {
    display: flex;
    align-items: baseline;
    gap: 8px;
  }

  .resume-work-handle {
    color: var(--ink-3);
    cursor: grab;
    user-select: none;
    font-size: 14px;
  }

  .resume-work-handle:active {
    cursor: grabbing;
  }

  .resume-work-title {
    font-weight: 600;
    font-size: 14px;
    color: var(--ink);
  }

  .resume-work-company {
    font-weight: 400;
    color: var(--ink-3);
  }

  .resume-work-description {
    font-size: 13px;
    color: var(--ink-2);
    white-space: pre-wrap;
    margin: 8px 0 0;
  }

  .resume-work-match {
    font-size: 11px;
    color: var(--positive);
    margin: 4px 0 0;
  }

  .resume-work-actions {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 4px;
  }

  .resume-education-row {
    display: grid;
    grid-template-columns: 70px 1fr;
    gap: 18px;
    padding: 12px 0;
    border-bottom: 1px solid var(--rule-soft);
  }

  .resume-education-row:last-child {
    border-bottom: 0;
  }

  .resume-education-year {
    color: var(--ink-3);
    font-size: 11px;
  }

  .resume-education-body {
    font-size: 13px;
    color: var(--ink);
  }

  .resume-education-degree {
    font-weight: 600;
  }

  .resume-education-institution {
    color: var(--ink-3);
  }

  .resume-skills-cluster {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
  }

  .skill-chip {
    text-transform: none;
    letter-spacing: 0;
    font-family: var(--font-ui);
    font-size: 11px;
    gap: 4px;
  }

  .skill-chip-available {
    text-transform: none;
    letter-spacing: 0;
    font-family: var(--font-ui);
    font-size: 11px;
    border-style: dashed;
    gap: 4px;
  }

  .saving-skill {
    opacity: 0.5;
    pointer-events: none;
  }

  .skill-chip-action {
    background: none;
    border: 0;
    cursor: pointer;
    padding: 0 2px;
    font-size: 11px;
    line-height: 1;
    opacity: 0.6;
    color: inherit;
    font-family: inherit;
  }

  .skill-chip-action:hover {
    opacity: 1;
  }

  .skill-chip-input {
    min-width: 100px;
    max-width: 300px;
    width: auto;
    field-sizing: content;
    font-size: 11px;
    font-family: inherit;
    padding: 0 4px;
    border: 0;
    background: transparent;
    color: inherit;
  }

  .resume-skills-available-eyebrow {
    margin-top: 12px;
  }

  .resume-languages-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }

  .resume-language-card {
    display: flex;
    flex-direction: column;
    gap: 2px;
    padding: 12px;
    background: var(--paper-2);
    border: 1px solid var(--rule);
    border-radius: var(--r-sm);
  }

  .resume-language-name {
    font-weight: 600;
    color: var(--ink);
    font-size: 14px;
  }

  .resume-language-level {
    color: var(--ink-3);
    font-size: 12px;
  }

  .resume-project-row {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 8px;
    padding: 12px 0;
    border-bottom: 1px solid var(--rule-soft);
  }

  .resume-project-row:last-child {
    border-bottom: 0;
  }

  .resume-project-name {
    font-weight: 600;
    color: var(--ink);
    font-size: 14px;
    margin: 0;
  }

  .resume-project-description {
    color: var(--ink-2);
    font-size: 13px;
    margin: 4px 0 0;
  }

  .resume-project-tech {
    color: var(--ink-3);
    font-size: 11px;
    margin: 4px 0 0;
  }

  .resume-loading-note {
    color: var(--ink-3);
    font-size: 13px;
    text-align: center;
    font-style: italic;
  }

  .resume-empty {
    color: var(--ink-3);
    font-size: 12px;
    font-style: italic;
    margin: 8px 0 0;
  }

  .resume-preview button:focus-visible,
  .resume-preview input:focus-visible,
  .resume-preview textarea:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }
</style>
