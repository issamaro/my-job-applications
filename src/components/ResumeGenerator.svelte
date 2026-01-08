<script>
  import JobDescriptionInput from './JobDescriptionInput.svelte';
  import ProgressBar from './ProgressBar.svelte';
  import ResumePreview from './ResumePreview.svelte';
  import SavedJobsList from './SavedJobsList.svelte';
  import LanguageSelector from './LanguageSelector.svelte';
  import { generateResume, getResume, getCompleteProfile, createJobDescription, updateJobDescription } from '../lib/api.js';

  let view = $state('input');
  let jobDescription = $state('');
  let currentResume = $state(null);
  let error = $state(null);
  let loadingStatus = $state('Analyzing job description...');
  let abortController = $state(null);
  let savedJobsRef = $state(null);
  let profileIncomplete = $state(false);
  let loadedJobId = $state(null);
  let loadedJobTitle = $state(null);
  let saving = $state(false);
  let selectedLanguage = $state('en');

  const statusMessages = [
    'Analyzing job description...',
    'Matching your experience...',
    'Composing tailored resume...'
  ];

  $effect(() => {
    checkProfile();
  });

  async function checkProfile() {
    try {
      const profile = await getCompleteProfile();
      profileIncomplete = !profile.work_experiences || profile.work_experiences.length === 0;
    } catch (e) {
      console.error('Failed to check profile:', e);
    }
  }

  async function handleGenerate() {
    if (jobDescription.trim().length < 100) {
      error = 'Please paste a job description (at least 100 characters)';
      return;
    }

    error = null;
    view = 'loading';
    loadingStatus = statusMessages[0];

    let statusIndex = 0;
    const statusInterval = setInterval(() => {
      statusIndex = (statusIndex + 1) % statusMessages.length;
      loadingStatus = statusMessages[statusIndex];
    }, 5000);

    abortController = new AbortController();

    try {
      const result = await generateResume(jobDescription, loadedJobId, selectedLanguage);
      currentResume = result;
      view = 'preview';
      savedJobsRef?.refresh();
    } catch (e) {
      if (e.name === 'AbortError') {
        view = 'input';
      } else if (e.message.includes('work experience')) {
        error = 'Your profile needs work experience before you can generate a tailored resume.';
        view = 'input';
        profileIncomplete = true;
      } else if (e.message.includes('100 characters')) {
        error = 'Please paste a job description (at least 100 characters)';
        view = 'input';
      } else if (e.message.includes("doesn't appear to be")) {
        error = "This doesn't appear to be a job description. Please paste a complete job posting.";
        view = 'input';
      } else if (e.message.includes('truncated')) {
        error = 'The job description is too long for processing. Try removing non-essential details.';
        view = 'input';
      } else if (e.message.includes('busy')) {
        error = 'AI service is busy. Please try again in a moment.';
        view = 'input';
      } else {
        // Show actual error message for debugging
        error = e.message || 'Could not generate resume. Please try again.';
        console.error('Resume generation error:', e);
        view = 'input';
      }
    } finally {
      clearInterval(statusInterval);
      abortController = null;
    }
  }

  function handleCancel() {
    if (abortController) {
      abortController.abort();
    }
    view = 'input';
  }

  function handleBack() {
    view = 'input';
    jobDescription = '';
    currentResume = null;
    error = null;
  }

  function handleRegenerate() {
    view = 'input';
    handleGenerate();
  }

  async function handleSelectResume(id) {
    try {
      const resume = await getResume(id);
      currentResume = resume;
      view = 'preview';
    } catch (e) {
      error = 'Could not load resume. Please try again.';
    }
  }

  function goToProfile() {
    window.dispatchEvent(new CustomEvent('switchTab', { detail: 'profile' }));
  }

  function handleLoadJob(id, rawText, title) {
    jobDescription = rawText;
    loadedJobId = id;
    loadedJobTitle = title;
    error = null;
  }

  function handleClearLoaded() {
    loadedJobId = null;
    loadedJobTitle = null;
    jobDescription = '';
    error = null;
  }

  async function handleSaveJob() {
    if (jobDescription.trim().length < 100) {
      error = 'Job description must be at least 100 characters';
      return;
    }

    saving = true;
    error = null;

    try {
      if (loadedJobId) {
        await updateJobDescription(loadedJobId, { raw_text: jobDescription });
      } else {
        const result = await createJobDescription(jobDescription);
        loadedJobId = result.id;
        loadedJobTitle = result.title;
      }
      savedJobsRef?.refresh();
    } catch (e) {
      error = 'Could not save. Please try again.';
      console.error('Failed to save job description:', e);
    } finally {
      saving = false;
    }
  }
</script>

<div class="resume-generator">
  {#if profileIncomplete && view === 'input'}
    <div class="profile-incomplete">
      <p>Your profile needs work experience before you can generate a tailored resume.</p>
      <button class="btn btn-primary" onclick={goToProfile}>
        Go to Profile
      </button>
    </div>
  {:else if view === 'input'}
    <JobDescriptionInput
      value={jobDescription}
      {error}
      {saving}
      {loadedJobId}
      {loadedJobTitle}
      onInput={(val) => {
        jobDescription = val;
        error = null;
      }}
      onSave={handleSaveJob}
      onClear={handleClearLoaded}
    />

    <div class="generator-actions">
      <LanguageSelector
        value={selectedLanguage}
        onchange={(val) => selectedLanguage = val}
      />
      <button
        class="btn btn-primary"
        onclick={handleGenerate}
        disabled={jobDescription.trim().length < 100 || saving}
      >
        Generate Resume
      </button>
    </div>

    <SavedJobsList
      bind:this={savedJobsRef}
      onLoad={handleLoadJob}
      onSelectResume={handleSelectResume}
      selectedId={loadedJobId}
    />

  {:else if view === 'loading'}
    <JobDescriptionInput
      value={jobDescription}
      disabled={true}
    />

    <ProgressBar status={loadingStatus} />

    <div class="loading-actions">
      <button class="btn" onclick={handleCancel}>
        Cancel
      </button>
    </div>

  {:else if view === 'preview' && currentResume}
    <ResumePreview
      resume={currentResume}
      onBack={handleBack}
      onRegenerate={handleRegenerate}
    />
  {/if}
</div>
