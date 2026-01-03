<script>
  import JobDescriptionInput from './JobDescriptionInput.svelte';
  import ProgressBar from './ProgressBar.svelte';
  import ResumePreview from './ResumePreview.svelte';
  import ResumeHistory from './ResumeHistory.svelte';
  import { generateResume, getResume, getCompleteProfile } from '../lib/api.js';

  let view = $state('input');
  let jobDescription = $state('');
  let currentResume = $state(null);
  let error = $state(null);
  let loadingStatus = $state('Analyzing job description...');
  let abortController = $state(null);
  let historyRef = $state(null);
  let profileIncomplete = $state(false);

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
      const result = await generateResume(jobDescription);
      currentResume = result;
      view = 'preview';
      historyRef?.refresh();
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
      } else {
        error = 'Could not generate resume. Please try again.';
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

  async function handleHistorySelect(id) {
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
      onInput={(val) => {
        jobDescription = val;
        error = null;
      }}
    />

    <div class="generator-actions">
      <button
        class="btn btn-primary"
        onclick={handleGenerate}
        disabled={jobDescription.trim().length < 100}
      >
        Generate Resume
      </button>
    </div>

    <hr />

    <ResumeHistory bind:this={historyRef} onSelect={handleHistorySelect} />

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
      resume={currentResume.resume}
      jobAnalysis={currentResume.job_analysis}
      jobTitle={currentResume.job_title}
      companyName={currentResume.company_name}
      matchScore={currentResume.match_score}
      createdAt={currentResume.created_at}
      onBack={handleBack}
      onRegenerate={handleRegenerate}
    />
  {/if}
</div>
